"""Run Go browser tests in shards, then merge their HTML and JUnit reports."""

import argparse
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
import zipfile


def inventory():
    result = subprocess.run(["go", "test", "./tests", "-list", "^Test"],
                            text=True, capture_output=True, check=True)
    names = sorted(name for name in result.stdout.splitlines() if re.fullmatch(r"Test\w+", name))
    if not names:
        raise ValueError("No browser tests found in ./tests")
    return names


def select_shard(names, index, total):
    if not 1 <= index <= total:
        raise ValueError("Shard must satisfy 1 <= index <= total")
    return sorted(names)[index - 1::total]


def run_attempt(names, attempt, root, workers):
    folder = root / f"attempt-{attempt}"
    folder.mkdir(parents=True)
    pattern = "^(" + "|".join(re.escape(name) for name in names) + ")$"
    print(f"Attempt {attempt + 1}: {', '.join(names)}", flush=True)
    result = subprocess.run(
        ["go", "test", "./tests", "-json", "-count=1", f"-parallel={workers}",
         "-timeout=6m", "-run", pattern], text=True, capture_output=True,
        env=dict(os.environ, TEST_RESULTS_DIR=str(folder.resolve()), CI_ATTEMPT=str(attempt)),
    )
    (folder / "events.jsonl").write_text(result.stdout)
    (folder / "stderr.log").write_text(result.stderr)
    records = {name: dict(number=attempt, status="missing", seconds=0, output="") for name in names}
    errors = []
    for line in result.stdout.splitlines():
        event = json.loads(line)
        name = event.get("Test", "")
        print(event.get("Output", ""), end="", flush=True)
        if event["Action"] == "skip" and "/" in name:
            errors.append(f"Skipped subtest: {name}")
        record = records.get(name.split("/")[0])
        if record is not None:
            record["output"] += event.get("Output", "")
            if name in records and event["Action"] in ("pass", "fail", "skip"):
                record.update(status=event["Action"], seconds=event.get("Elapsed", 0))
    if any(record["status"] == "missing" for record in records.values()):
        errors.append("Some tests did not finish; inspect events.jsonl and stderr.log")
    if result.returncode and not any(record["status"] == "fail" for record in records.values()):
        errors.append(f"go test exited {result.returncode}: {result.stderr}")
    return records, errors


def run_suite(selected, root, retries, workers):
    cases = {name: dict(name=name, attempts=[]) for name in selected}
    errors = []
    pending = selected
    for attempt in range(retries + 1):
        if not pending:
            break
        records, problems = run_attempt(pending, attempt, root, workers)
        errors.extend(problems)
        for name, record in records.items():
            cases[name]["attempts"].append(record)
        if problems:
            break
        pending = [name for name, record in records.items() if record["status"] == "fail"]
    return list(cases.values()), errors


def status(case):
    attempts = case["attempts"]
    if not attempts or attempts[-1]["status"] != "pass":
        return "failed"
    return "flaky" if any(a["status"] != "pass" for a in attempts[:-1]) else "passed"


def validate_evidence(result):
    errors = []
    for case in result["cases"]:
        for attempt in case["attempts"]:
            folder = Path(result["directory"]) / f"attempt-{attempt['number']}"
            evidence = folder / case["name"]
            required = [folder / "events.jsonl", evidence / "trace.zip"]
            if attempt["status"] == "fail":
                required += [evidence / "page.png", evidence / "page.html"]
            for path in required:
                if not path.is_file() or path.stat().st_size == 0:
                    errors.append(f"missing or empty required evidence: {path}")
            if not (folder / "stderr.log").is_file():
                errors.append(f"missing required evidence: {folder / 'stderr.log'}")
            trace = evidence / "trace.zip"
            if trace.is_file():
                try:
                    with zipfile.ZipFile(trace) as archive:
                        has_trace = any(
                            entry.filename.endswith(".trace") and entry.file_size > 0
                            for entry in archive.infolist()
                        )
                        if archive.testzip() or not has_trace:
                            raise ValueError("trace data is missing or corrupt")
                except (OSError, ValueError, zipfile.BadZipFile) as error:
                    errors.append(f"invalid trace: {trace}: {error}")
    return errors


def write_reports(results, destination, merged=False):
    destination.mkdir(parents=True, exist_ok=True)
    cases = [(result, case) for result in results for case in result["cases"]]
    errors = [error for result in results for error in result["errors"] + validate_evidence(result)]
    failed = sum(status(case) == "failed" for _, case in cases)
    flaky = sum(status(case) == "flaky" for _, case in cases)
    summary = f"{len(cases)} tests: {failed} failed, {flaky} flaky, {len(errors)} evidence/infrastructure errors"
    suite = ET.Element("testsuite", name="Playwright Go", tests=str(len(cases) + len(errors)),
                       failures=str(failed), errors=str(len(errors)))
    sections = ["<h1>Playwright Go results</h1>", f"<p>{summary}</p>"]
    for result, case in cases:
        state = status(case)
        test = ET.SubElement(suite, "testcase", name=case["name"], classname="sis2/tests",
                             time=str(sum(a["seconds"] for a in case["attempts"])))
        properties = ET.SubElement(test, "properties")
        ET.SubElement(properties, "property", name="status", value=state)
        sections.append(f"<h2>{html.escape(case['name'])}: {state}</h2>")
        logs = []
        for attempt in case["attempts"]:
            log = f"Attempt {attempt['number'] + 1} ({attempt['status']}):\n{attempt['output']}"
            logs.append(log)
            sections.append(f"<pre>{html.escape(log)}</pre>")
            relative = f"attempt-{attempt['number']}/{case['name']}"
            prefix = f"evidence/shard-{result['shard']}/" if merged else ""
            for name in ("trace.zip", "page.png", "page.html"):
                if (Path(result["directory"]) / relative / name).is_file():
                    link = html.escape(prefix + relative + "/" + name)
                    sections.append(f'<p><a href="{link}">{name}</a></p>')
        output = "\n".join(logs)
        ET.SubElement(test, "system-out").text = output
        if state == "failed":
            ET.SubElement(test, "failure", message="Test failed, skipped or incomplete").text = output
    for error in errors:
        test = ET.SubElement(suite, "testcase", name="CI evidence/infrastructure", classname="ci")
        ET.SubElement(test, "error", message="CI validation failed").text = error
        sections.append(f"<pre>{html.escape(error)}</pre>")
    ET.indent(suite)
    ET.ElementTree(suite).write(destination / "junit.xml", encoding="utf-8", xml_declaration=True)
    header = '<!doctype html><html lang="en"><meta charset="utf-8"><title>Playwright Go</title>'
    document = header + '<style>pre{white-space:pre-wrap}</style>'
    document += "\n".join(sections) + "</html>"
    (destination / "index.html").write_text(document)
    print(summary, flush=True)
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as file:
            file.write(summary + "\n")
    if flaky and os.getenv("GITHUB_ACTIONS"):
        print(f"::warning::{flaky} tests needed a retry; inspect their original failures.")
    return bool(failed or errors)


def run(args):
    index, total = map(int, args.shard.split("/"))
    root = Path(args.output) / f"shard-{index}"
    root.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    names, selected, cases, errors = [], [], [], []
    try:
        names = inventory()
        selected = select_shard(names, index, total)
        cases, errors = run_suite(selected, root, args.retries, args.workers)
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        errors.append(str(error))
    result = dict(shard=index, total=total, inventory=names, selected=selected, cases=cases,
                  errors=errors, seconds=time.monotonic() - start, directory=str(root.resolve()))
    (root / "summary.json").write_text(json.dumps(result, indent=2))
    return write_reports([result], root)


def load_shards(source, total):
    results, errors = [], []
    for path in sorted(Path(source).rglob("summary.json")):
        result = json.loads(path.read_text())
        result["directory"] = str(path.parent.resolve())
        results.append(result)
    if sorted(result["shard"] for result in results) != list(range(1, total + 1)):
        errors.append(f"Expected shards 1..{total}")
    names = results[0]["inventory"] if results else []
    executed = []
    for result in results:
        expected = select_shard(names, result["shard"], total)
        if result["total"] != total or result["inventory"] != names:
            errors.append(f"Shard {result['shard']}: inconsistent inventory or shard count")
        if result["selected"] != expected:
            errors.append(f"Shard {result['shard']}: incorrect declared selection")
        actual = sorted(case["name"] for case in result["cases"])
        if actual != expected:
            errors.append(f"Shard {result['shard']}: actual cases {actual} differ from {expected}")
        executed.extend(actual)
    if not names or sorted(executed) != names:
        errors.append("Combined shards must cover every discovered test exactly once")
    return results, errors


def merge(args):
    results, errors = load_shards(args.input, args.shards)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    for result in results:
        shutil.copytree(result["directory"], output / "evidence" / f"shard-{result['shard']}")
    if errors:
        results.append(dict(cases=[], errors=errors))
    return write_reports(results, output, merged=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run_parser = commands.add_parser("run")
    run_parser.add_argument("--shard", default="1/1")
    run_parser.add_argument("--output", default="test-results")
    run_parser.add_argument("--workers", type=int, default=2)
    is_ci = os.getenv("CI", "").lower() not in ("", "0", "false")
    run_parser.add_argument("--retries", type=int, default=2 if is_ci else 0)
    merge_parser = commands.add_parser("merge")
    merge_parser.add_argument("--input", default="test-results")
    merge_parser.add_argument("--output", default="playwright-report")
    merge_parser.add_argument("--shards", type=int, default=4)
    args = parser.parse_args()
    if args.command == "run" and (args.retries < 0 or args.workers < 1):
        parser.error("Use nonnegative retries and positive workers")
    if args.command == "merge" and args.shards < 1:
        parser.error("Use a positive shard count")
    try:
        return run(args) if args.command == "run" else merge(args)
    except (OSError, ValueError, KeyError) as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
