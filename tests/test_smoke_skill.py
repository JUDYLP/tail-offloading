"""Regression checks for false positives; these do not replace a live smoke run."""

import copy
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import smoke_skill


class SmokeAssertionsTests(unittest.TestCase):
    def setUp(self):
        self.installed = ROOT / "SKILL.md"
        self.fixture = {"nonce": "unique-run", "values": [17, 3, 6]}
        self.result = {"skill": "tail-offloading", "default_attempt_budget": 2,
                       "max_failed_attempts": 5, "nonce": "unique-run", "total": 26}
        self.events = [{"type": "turn.completed"}]
        for path in (self.installed, ROOT / "references" / "contracts.md"):
            self.events.append({"type": "item.completed", "item": {
                "type": "command_execution", "command": f"cat {path}",
                "status": "completed", "exit_code": 0,
                "aggregated_output": path.read_text(encoding="utf-8"),
            }})

    def verify(self, events=None, result=None):
        smoke_skill.verify_invocation(self.events if events is None else events,
                                      self.result if result is None else result,
                                      self.fixture, self.installed)

    def test_success_requires_evidence_and_correct_result(self):
        self.verify()
        for field, wrong in (("nonce", "old-run"), ("total", 27),
                             ("default_attempt_budget", 5), ("max_failed_attempts", 6)):
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.verify(result={**self.result, field: wrong})

    def test_self_report_without_reads_cannot_pass(self):
        events = [{"type": "turn.completed"}, {"type": "item.completed", "item": {
            "type": "agent_message", "text": f"I loaded {self.installed}"}}]
        with self.assertRaisesRegex(ValueError, "No successful"):
            self.verify(events=events)

    def test_failed_wrong_path_or_truncated_reads_cannot_pass(self):
        for field, wrong in (("exit_code", 1), ("status", "failed"),
                             ("command", "cat /other/SKILL.md"),
                             ("aggregated_output", "name: tail-offloading")):
            events = copy.deepcopy(self.events)
            events[1]["item"][field] = wrong
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "No successful"):
                self.verify(events=events)
        with self.assertRaisesRegex(ValueError, "contracts.md"):
            self.verify(events=self.events[:-1])

    def test_failed_or_incomplete_turn_cannot_pass(self):
        for events in (self.events[1:], self.events + [{"type": "turn.failed"}],
                       self.events + [{"type": "error", "message": "transport failed"}]):
            with self.subTest(events=events[0]["type"]), self.assertRaises(ValueError):
                self.verify(events=events)

    def test_real_installation_identity_is_required(self):
        fields = smoke_skill.parse_required_fields(
            smoke_skill.parse_frontmatter(self.installed.read_text())[0])
        skill = {"name": "tail-offloading", "path": str(self.installed),
                 "description": fields["description"], "enabled": True, "scope": "user"}
        row = {"cwd": str(ROOT), "skills": [skill], "errors": []}
        smoke_skill.verify_discovery({"data": [row]}, ROOT, self.installed)
        bad_rows = [
            {**row, "skills": []}, {**row, "skills": [skill, skill]},
            {**row, "cwd": "/other"}, {**row, "errors": [{"message": "parse failed"}]},
        ]
        for field, wrong in (("path", "/other/SKILL.md"), ("enabled", False),
                             ("scope", "repo"), ("description", "stale")):
            bad_rows.append({**row, "skills": [{**skill, field: wrong}]})
        for bad in bad_rows:
            with self.subTest(row=bad), self.assertRaises(ValueError):
                smoke_skill.verify_discovery({"data": [bad]}, ROOT, self.installed)

    def test_missing_live_credentials_is_blocked_not_green(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "evidence"
            args = ["smoke_skill.py", "--live", "--output-dir", str(output)]
            with patch.object(sys, "argv", args), patch.dict(os.environ, {}, clear=True), \
                 patch.object(smoke_skill.shutil, "which", return_value="codex"), \
                 patch.object(smoke_skill.subprocess, "check_output", return_value="test-only"), \
                 patch.object(smoke_skill, "discover", return_value={}), \
                 patch.object(smoke_skill, "verify_discovery", return_value={}), \
                 patch.object(smoke_skill, "invoke") as invoke, \
                 contextlib.redirect_stdout(io.StringIO()):
                self.assertNotEqual(smoke_skill.main(), 0)
            invoke.assert_not_called()
            report = json.loads((output / "report.json").read_text())
            self.assertEqual(report["discovery"], "passed")
            self.assertEqual(report["invocation"], "blocked")
            self.assertEqual(report["e2e"], "blocked")

    @unittest.skipUnless(os.name == "posix", "smoke runner targets POSIX / WSL")
    def test_silent_discovery_process_times_out(self):
        with tempfile.TemporaryDirectory() as temporary:
            work = Path(temporary)
            stub = work / "silent-codex"
            stub.write_text(f"#!{sys.executable}\nimport time\ntime.sleep(60)\n")
            stub.chmod(0o700)
            with self.assertRaisesRegex(TimeoutError, "timed out"):
                smoke_skill.discover(str(stub), work, os.environ.copy(), work, 1)


if __name__ == "__main__":
    unittest.main()
