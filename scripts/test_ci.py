"""Checks that CI cannot silently lose a test, a failure, or a shard."""

import contextlib
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
import zipfile

import ci


class PipelineTests(unittest.TestCase):
    def test_shards_are_disjoint_and_cover_new_tests(self):
        for count in (1, 8, 9):
            names = [f"TestScenario{n}" for n in range(count)]
            shards = [ci.select_shard(names, n, 4) for n in range(1, 5)]
            combined = [name for shard in shards for name in shard]
            self.assertCountEqual(combined, names)
            self.assertEqual(len(combined), len(set(combined)))
        with self.assertRaises(ValueError):
            ci.select_shard(names, 0, 4)

    def test_retry_only_failed_tests_and_preserve_original_error(self):
        responses = [
            ({"TestA": self.attempt("fail", 0), "TestB": self.attempt("pass", 0)}, []),
            ({"TestA": self.attempt("pass", 1)}, []),
        ]
        with patch.object(ci, "run_attempt", side_effect=responses) as run:
            cases, errors = ci.run_suite(["TestA", "TestB"], Path("unused"), 2, 2)
        self.assertEqual(run.call_args_list[1].args[0], ["TestA"])
        self.assertEqual(ci.status(cases[0]), "flaky")
        self.assertEqual(len(cases[0]["attempts"]), 2)
        self.assertIn("original failure", cases[0]["attempts"][0]["output"])
        self.assertEqual(errors, [])

    def test_persistent_failure_uses_two_retries_and_stays_red(self):
        responses = [({"TestA": self.attempt("fail", n)}, []) for n in range(3)]
        with patch.object(ci, "run_attempt", side_effect=responses) as run:
            cases, _ = ci.run_suite(["TestA"], Path("unused"), 2, 2)
        self.assertEqual(run.call_count, 3)
        self.assertEqual(ci.status(cases[0]), "failed")

    def test_missing_shard_cannot_merge_as_green(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = self.result(root)
            result.update(total=2, inventory=["TestA", "TestB"])
            (root / "summary.json").write_text(json.dumps(result))
            _, errors = ci.load_shards(root, 2)
            self.assertTrue(any("Expected shards" in error for error in errors))
            self.assertTrue(any("every discovered test" in error for error in errors))

    def test_report_preserves_failures_and_links_to_trace(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = self.result(root)
            result["cases"][0]["attempts"] = [self.attempt("fail", 0)]
            self.evidence(result)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertTrue(ci.write_reports([result], root))
            xml = ET.parse(root / "junit.xml").getroot()
            self.assertEqual(xml.attrib["failures"], "1")
            self.assertIn("original failure", xml.find("testcase/failure").text)
            document = (root / "index.html").read_text()
            self.assertIn('href="attempt-0/TestA/trace.zip"', document)
            self.assertIn("&lt;original failure&gt;", document)

    def test_passing_summary_without_trace_fails_merge(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shard = root / "input" / "shard-1"
            result = self.result(shard)
            self.evidence(result)
            (shard / "attempt-0/TestA/trace.zip").unlink()
            (shard / "summary.json").write_text(json.dumps(result))
            output = root / "report"
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertTrue(ci.merge(SimpleNamespace(input=root / "input", shards=1, output=output)))
            xml = ET.parse(output / "junit.xml").getroot()
            self.assertGreater(int(xml.attrib["errors"]), 0)
            self.assertIn("trace.zip", xml.find("testcase/error").text)
            self.assertIn("missing or empty required evidence", (output / "index.html").read_text())

    def test_invalid_traces_cannot_make_a_passing_report(self):
        for invalid in (b"", b"not a zip"):
            with self.subTest(trace=invalid), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                result = self.result(root)
                self.evidence(result)
                (root / "attempt-0/TestA/trace.zip").write_bytes(invalid)
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertTrue(ci.write_reports([result], root))

    def test_trace_archive_must_contain_trace_data(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = self.result(root)
            self.evidence(result)
            with zipfile.ZipFile(root / "attempt-0/TestA/trace.zip", "w") as archive:
                archive.writestr("readme.txt", "no browser trace")
            self.assertTrue(any("invalid trace" in error for error in ci.validate_evidence(result)))

    def test_successful_retry_still_requires_original_failure_evidence(self):
        for filename in ("trace.zip", "page.png", "page.html", "../events.jsonl", "../stderr.log"):
            with self.subTest(missing=filename), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                result = self.result(root)
                result["cases"][0]["attempts"] = [self.attempt("fail", 0), self.attempt("pass", 1)]
                self.evidence(result)
                (root / "attempt-0" / "TestA" / filename).unlink()
                self.assertEqual(ci.status(result["cases"][0]), "flaky")
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertTrue(ci.write_reports([result], root))

    def test_cases_swapped_between_shards_fail_despite_complete_global_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for shard, expected, actual in ((1, "TestA", "TestB"), (2, "TestB", "TestA")):
                folder = root / "input" / f"shard-{shard}"
                result = self.result(folder)
                result.update(shard=shard, total=2, inventory=["TestA", "TestB"], selected=[expected])
                result["cases"][0]["name"] = actual
                self.evidence(result)
                (folder / "summary.json").write_text(json.dumps(result))
            _, errors = ci.load_shards(root / "input", 2)
            self.assertEqual(sum("actual cases" in error for error in errors), 2)
            self.assertFalse(any("every discovered test" in error for error in errors))
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertTrue(ci.merge(SimpleNamespace(input=root / "input", shards=2, output=root / "report")))

    def test_complete_valid_evidence_and_correct_shards_merge_green(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for shard, name in ((1, "TestA"), (2, "TestB")):
                folder = root / "input" / f"shard-{shard}"
                result = self.result(folder)
                result.update(shard=shard, total=2, inventory=["TestA", "TestB"], selected=[name])
                result["cases"][0]["name"] = name
                self.evidence(result)
                (folder / "summary.json").write_text(json.dumps(result))
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertFalse(ci.merge(SimpleNamespace(input=root / "input", shards=2, output=root / "report")))
            xml = ET.parse(root / "report/junit.xml").getroot()
            self.assertEqual(xml.attrib["errors"], "0")

    def test_skip_and_infrastructure_failure_stay_red(self):
        self.assertEqual(ci.status({"attempts": [self.attempt("skip", 0)]}), "failed")
        with tempfile.TemporaryDirectory() as directory:
            result = self.result(Path(directory))
            result["errors"] = ["compiler failed"]
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertTrue(ci.write_reports([result], Path(directory)))

    def test_skipped_subtest_cannot_hide_inside_passing_parent(self):
        events = [dict(Action="skip", Test="TestA/child"),
                  dict(Action="pass", Test="TestA", Elapsed=0.1)]
        process = SimpleNamespace(
            stdout=io.StringIO("".join(json.dumps(event) + "\n" for event in events)),
            wait=lambda: 0,
        )
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(ci.subprocess, "Popen", return_value=process), \
                contextlib.redirect_stdout(io.StringIO()):
            records, errors = ci.run_attempt(["TestA"], 0, Path(directory), 2)
        self.assertEqual(records["TestA"]["status"], "pass")
        self.assertIn("Skipped subtest: TestA/child", errors)

    @staticmethod
    def attempt(state, number):
        return dict(status=state, number=number, seconds=0.1,
                    output="<original failure>" if state == "fail" else "ok")

    def result(self, directory):
        return dict(shard=1, total=1, inventory=["TestA"], selected=["TestA"],
                    cases=[dict(name="TestA", attempts=[self.attempt("pass", 0)])],
                    errors=[], seconds=0.1, directory=str(directory))

    @staticmethod
    def evidence(result):
        for case in result["cases"]:
            for attempt in case["attempts"]:
                root = Path(result["directory"]) / f"attempt-{attempt['number']}"
                path = root / case["name"]
                path.mkdir(parents=True, exist_ok=True)
                (root / "events.jsonl").write_text('{"Action":"pass"}\n')
                (root / "stderr.log").write_text("")
                with zipfile.ZipFile(path / "trace.zip", "w") as archive:
                    archive.writestr("trace.trace", '{"type":"context-options"}\n')
                if attempt["status"] == "fail":
                    (path / "page.png").write_bytes(b"fixture screenshot")
                    (path / "page.html").write_text("<html>failure</html>")


if __name__ == "__main__":
    unittest.main()
