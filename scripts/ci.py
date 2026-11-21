#!/usr/bin/env python3
"""Go Playwright CI: deterministic shards, recorded retries, HTML and JUnit.

Uses only Python's standard library. Run from the repository root.
"""

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
    result = subprocess.run(
        ["go", "test", "./tests", "-list", "^Test"],
        text=True, capture_output=True, check=True,
    )
    names = sorted(line for line in result.stdout.splitlines()
                   if re.fullmatch(r"Test\w+", line))
    if not names:
        raise ValueError("No browser tests discovered in ./tests")
    return names


def select_shard(names, index, total):
    if total < 1 or not 1 <= index <= total:
        raise ValueError("Shard must satisfy 1 <= index <= total")
    return sorted(names)[index - 1::total]


def run_attempt(names, attempt, root, workers):
    directory = root / f"attempt-{attempt}"
    directory.mkdir(parents=True)
    env = dict(os.environ, TEST_RESULTS_DIR=str(directory.resolve()),
               CI_ATTEMPT=str(attempt))
    pattern = "^(" + "|".join(re.escape(name) for name in names) + ")$"
    command = ["go", "test", "./tests", "-json", "-count=1",
               f"-parallel={workers}", "-timeout=6m", "-run", pattern]
    print(f"Attempt {attempt + 1}: {', '.join(names)}", flush=True)
    records = {name: {"number": attempt, "status": "missing", "seconds": 0,
                      "output": ""} for name in names}
    errors = []
    with (directory / "events.jsonl").open("w") as events, \
            (directory / "stderr.log").open("w") as stderr:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=stderr,
                                   text=True, env=env)
        for line in process.stdout:
            events.write(line)
            events.flush()
            event = json.loads(line)
            if event.get("Output"):
                print(event["Output"], end="", flush=True)
            name = event.get("Test", "")
            if event["Action"] == "skip" and "/" in name:
                errors.append(f"Skipped subtest: {name}")
            # Subtest output belongs to its top-level scenario too.
            record = records.get(name.split("/")[0])
            if record is not None:
                record["output"] += event.get("Output", "")
                if name in records and event["Action"] in ("pass", "fail", "skip"):
                    record["status"] = event["Action"]
                    record["seconds"] = event.get("Elapsed", 0)
        code = process.wait()
    stderr_text = (directory / "stderr.log").read_text()
    if stderr_text:
        print(stderr_text, file=sys.stderr)
    missing = [name for name, record in records.items() if record["status"] == "missing"]
    if missing:
        errors.append(f"Attempt {attempt + 1}: missing results for {', '.join(missing)}. "
                      f"See attempt-{attempt}/events.jsonl and stderr.log. {stderr_text}")
    if code and not any(record["status"] == "fail" for record in records.values()):
        errors.append(f"go test exited {code} without a failed test result. {stderr_text}")
    return records, errors


def run_suite(selected, root, retries, workers):
    cases = {name: {"name": name, "attempts": []} for name in selected}
    errors = []
    pending = list(selected)
    for attempt in range(retries + 1):
        if not pending:
            break
        records, problems = run_attempt(pending, attempt, root, workers)
        errors.extend(problems)
        for name, record in records.items():
            cases[name]["attempts"].append(record)
        if problems:
            break  # Build/runner failures are not flaky-test retries.
        pending = [name for name, record in records.items() if record["status"] == "fail"]
    return list(cases.values()), errors


def status(case):
    attempts = case["attempts"]
    if not attempts or attempts[-1]["status"] != "pass":
        return "failed"  # A skipped/missing test must not make CI green.
    return "flaky" if any(a["status"] != "pass" for a in attempts[:-1]) else "passed"


def validate_evidence(result):
    errors = []
    for case in result["cases"]:
        for attempt in case["attempts"]:
            relative = Path(f"attempt-{attempt['number']}")
            root = Path(result["directory"]) / relative
            required = [(root / "events.jsonl", True), (root / "stderr.log", False)]
            evidence = root / case["name"]
            trace = evidence / "trace.zip"
            required.append((trace, True))
            if attempt["status"] == "fail":
                required.extend((evidence / name, True) for name in ("page.png", "page.html"))
            for path, nonempty in required:
                if not path.is_file() or (nonempty and path.stat().st_size == 0):
                    errors.append(f"Shard {result['shard']}: missing or empty required evidence: "
                                  f"{path.relative_to(Path(result['directory']))}")
            if trace.is_file():
                try:
                    with zipfile.ZipFile(trace) as archive:
                        if archive.testzip() is not None or not any(
                            entry.filename.endswith(".trace") and entry.file_size > 0
                            for entry in archive.infolist()
                        ):
                            raise ValueError("archive must contain nonempty trace data and valid CRCs")
                except (OSError, ValueError, zipfile.BadZipFile) as error:
                    errors.append(f"Shard {result['shard']}: invalid trace for "
                                  f"{case['name']} attempt {attempt['number'] + 1}: {error}")
    return errors


def write_reports(results, destination, merged=False):
    destination.mkdir(parents=True, exist_ok=True)
    cases = [(result, case) for result in results for case in result["cases"]]
    errors = [error for result in results for error in result["errors"]]
    errors.extend(error for result in results for error in validate_evidence(result))
    failed = sum(status(case) == "failed" for _, case in cases)
    flaky = sum(status(case) == "flaky" for _, case in cases)
    suite = ET.Element("testsuite", name="Playwright Go", tests=str(len(cases) + len(errors)),
                       failures=str(failed), errors=str(len(errors)),
                       time=f"{sum(r['seconds'] for r in results):.3f}")
    sections = []
    for result, case in cases:
        state = status(case)
        label = f"{case['name']} — {state} (shard {result['shard']}/{result['total']})"
        testcase = ET.SubElement(suite, "testcase", name=case["name"], classname="sis2/tests",
                                 time=f"{sum(a['seconds'] for a in case['attempts']):.3f}")
        properties = ET.SubElement(testcase, "properties")
        ET.SubElement(properties, "property", name="status", value=state)
        output = "\n".join(f"Attempt {a['number'] + 1} ({a['status']}):\n{a['output']}"
                           for a in case["attempts"])
        if state == "failed":
            ET.SubElement(testcase, "failure", message="Test failed, skipped, or incomplete").text = output
        ET.SubElement(testcase, "system-out").text = output
        attempts_html = []
        prefix = f"evidence/shard-{result['shard']}/" if merged else ""
        for attempt in case["attempts"]:
            relative = f"attempt-{attempt['number']}/{case['name']}"
            source = Path(result["directory"]) / relative
            links = " ".join(
                f'<a href="{html.escape(prefix + relative + "/" + file)}">{file}</a>'
                for file in ("trace.zip", "page.png", "page.html") if (source / file).is_file()
            )
            attempts_html.append(
                f"<details open><summary>Attempt {attempt['number'] + 1}: "
                f"{html.escape(attempt['status'])}, {attempt['seconds']:.2f}s</summary>"
                f"<p>{links}</p><pre>{html.escape(attempt['output'])}</pre></details>"
            )
        sections.append(f'<section class="{state}"><h2>{html.escape(label)}</h2>'
                        + "".join(attempts_html) + "</section>")
    for index, error in enumerate(errors, 1):
        testcase = ET.SubElement(suite, "testcase", name=f"CI infrastructure {index}",
                                 classname="ci.infrastructure", time="0")
        ET.SubElement(testcase, "error", message="CI infrastructure or report failure").text = error
    ET.indent(suite)
    ET.ElementTree(suite).write(destination / "junit.xml", encoding="utf-8", xml_declaration=True)
    error_html = "".join(f"<pre>{html.escape(error)}</pre>" for error in errors)
    document = f"""<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Playwright Go test report</title><style>
body{{font:16px system-ui;margin:2rem auto;padding:0 1rem;max-width:1000px;color:#17202a}}
section{{border-left:5px solid #19744a;padding:0.5rem 1rem;margin:1.5rem 0;background:#f5f7f8}}
.failed{{border-color:#bd2525}}.flaky{{border-color:#b57900}}h2{{font-size:1.1rem}}
pre{{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px}}a{{margin-right:1rem}}
summary{{cursor:pointer}}details{{margin:1rem 0}}
</style><h1>Playwright Go test report</h1>
<p>{len(cases)} tests · {failed} failed · {flaky} flaky · {len(errors)} infrastructure/report errors</p>
<p>A flaky result passed after a recorded failure. Every attempt remains below.
Download trace.zip and open it with the matching Playwright CLI's show-trace command.</p>
{error_html}{''.join(sections)}</html>"""
    (destination / "index.html").write_text(document)
    summary = (f"{len(cases)} tests: {failed} failed, {flaky} flaky, "
               f"{len(errors)} infrastructure/report errors")
    print(summary, flush=True)
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as file:
            file.write(f"### Playwright Go results\n\n{summary}\n\n")
            file.write("| Test | Result | Attempts |\n| --- | --- | --- |\n")
            for _, case in cases:
                file.write(f"| {case['name']} | {status(case)} | {len(case['attempts'])} |\n")
            for error in errors:
                file.write(f"\nError: {error}\n")
    if flaky and os.getenv("GITHUB_ACTIONS"):
        print(f"::warning::{flaky} flaky tests passed on retry. Inspect all attempts in the report.")
    return bool(failed or errors)


def run(args):
    index, total = map(int, args.shard.split("/"))
    root = Path(args.output) / f"shard-{index}"
    # Refuse stale results instead of accidentally merging evidence from another run.
    root.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    names, selected, cases, errors = [], [], [], []
    try:
        names = inventory()
        selected = select_shard(names, index, total)
        cases, errors = run_suite(selected, root, args.retries, args.workers)
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        errors.append(str(error))
    result = dict(shard=index, total=total, inventory=names, selected=selected,
                  cases=cases, errors=errors, seconds=time.monotonic() - start,
                  directory=str(root.resolve()))
    (root / "summary.json").write_text(json.dumps(result, indent=2))
    return write_reports([result], root)


def load_shards(source, total):
    results, errors = [], []
    for path in sorted(Path(source).rglob("summary.json")):
        result = json.loads(path.read_text())
        result["directory"] = str(path.parent.resolve())
        results.append(result)
    indices = sorted(result["shard"] for result in results)
    if indices != list(range(1, total + 1)):
        errors.append(f"Expected shards 1..{total}, received {indices}")
    if results:
        names = results[0]["inventory"]
        executed = []
        for result in results:
            if result["total"] != total or result["inventory"] != names:
                errors.append(f"Shard {result['shard']}: inconsistent suite inventory or shard count")
            expected = select_shard(names, result["shard"], total)
            if result["selected"] != expected:
                errors.append(f"Shard {result['shard']}: incorrect test selection")
            actual = [case["name"] for case in result["cases"]]
            if sorted(actual) != expected:
                errors.append(f"Shard {result['shard']}: actual cases {sorted(actual)} "
                              f"do not match expected selection {expected}")
            executed.extend(actual)
        if not names or sorted(executed) != sorted(names):
            errors.append("Combined shards must execute every discovered test exactly once (plus recorded retries)")
    return results, errors


def merge(args):
    results, errors = load_shards(args.input, args.shards)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    for result in results:
        shutil.copytree(result["directory"], output / "evidence" / f"shard-{result['shard']}")
    if errors:
        results.append(dict(shard=0, total=args.shards, cases=[], errors=errors, seconds=0))
    return write_reports(results, output, merged=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    runner = commands.add_parser("run")
    runner.add_argument("--shard", default="1/1", help="one-based index/total")
    runner.add_argument("--output", default="test-results")
    runner.add_argument("--workers", type=int, default=2)
    is_ci = os.getenv("CI", "").lower() not in ("", "0", "false")
    runner.add_argument("--retries", type=int, default=2 if is_ci else 0)
    merger = commands.add_parser("merge")
    merger.add_argument("--input", default="test-results")
    merger.add_argument("--output", default="playwright-report")
    merger.add_argument("--shards", type=int, default=4)
    args = parser.parse_args()
    if args.command == "run" and (args.retries < 0 or args.workers < 1):
        parser.error("retries must be nonnegative and workers must be positive")
    if args.command == "merge" and args.shards < 1:
        parser.error("shards must be positive")
    try:
        return run(args) if args.command == "run" else merge(args)
    except (OSError, ValueError, KeyError) as error:
        print(f"CI runner error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
