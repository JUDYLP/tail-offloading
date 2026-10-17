#!/usr/bin/env python3
"""Smoke-test ZIP installation with real Codex discovery and optional inference."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import queue
import secrets
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from zipfile import BadZipFile, ZipFile

from build_package import check
from validate_skill import parse_frontmatter, parse_required_fields, validate


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "tail-offloading"
PROMPT = """Use $tail-offloading for this installation smoke test.
Read the discovered SKILL.md and its linked references/contracts.md with shell
commands containing their absolute paths, even if the skill was already injected.
Do not search for another copy. This is one tiny task: do it directly, with no
subagents, network tools, or file changes.
Read input.json in the working directory. Return its nonce and the sum of its
values. Also report the skill's name, its default attempt budget, and its maximum
number of unsuccessful small-model attempts per work unit. Use the requested JSON
schema. Do not guess if the skill or the input cannot be read.
"""
SCHEMA = {
    "type": "object",
    "properties": {
        "skill": {"type": "string"},
        "default_attempt_budget": {"type": "integer"},
        "max_failed_attempts": {"type": "integer"},
        "nonce": {"type": "string"},
        "total": {"type": "integer"},
    },
    "required": ["skill", "default_attempt_budget", "max_failed_attempts", "nonce", "total"],
    "additionalProperties": False,
}


def save_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def stop_process(proc: subprocess.Popen) -> None:
    """Terminate the owned process group, including any command still running."""
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    proc.wait()


def discover(codex: str, work: Path, env: dict, evidence: Path, timeout: int) -> dict:
    """Use the real app-server parser; no model call and no path injected into it."""
    with (evidence / "discovery.stderr.log").open("w", encoding="utf-8") as err:
        proc = subprocess.Popen(
            [codex, "app-server"], cwd=work, env=env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=err, text=True, start_new_session=True,
        )
        messages = queue.Queue()

        def read_stdout():
            for line in proc.stdout:
                messages.put(line)
            messages.put(None)

        reader = threading.Thread(target=read_stdout, daemon=True)
        reader.start()
        deadline = time.monotonic() + timeout

        def send(message):
            proc.stdin.write(json.dumps(message) + "\n")
            proc.stdin.flush()

        def request(request_id, method, params):
            send({"id": request_id, "method": method, "params": params})
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("Codex discovery timed out")
                try:
                    line = messages.get(timeout=remaining)
                except queue.Empty as exc:
                    raise TimeoutError("Codex discovery timed out") from exc
                if line is None:
                    raise RuntimeError("Codex exited before discovery; see discovery.stderr.log")
                message = json.loads(line)
                if message.get("id") == request_id:
                    if "error" in message:
                        raise RuntimeError(f"{method}: {message['error']}")
                    return message["result"]

        try:
            request(1, "initialize", {"clientInfo": {"name": "tail_smoke", "version": "1"}})
            send({"method": "initialized"})
            return request(2, "skills/list", {"cwds": [str(work)], "forceReload": True})
        finally:
            stop_process(proc)
            proc.stdin.close()
            reader.join(timeout=3)
            proc.stdout.close()


def verify_discovery(result: dict, work: Path, installed: Path) -> dict:
    rows = result.get("data", [])
    if len(rows) != 1 or rows[0].get("cwd") != str(work):
        raise ValueError("skills/list did not return the isolated working directory")
    if rows[0].get("errors"):
        raise ValueError(f"Skill discovery errors: {rows[0]['errors']}")
    matches = [skill for skill in rows[0].get("skills", []) if skill.get("name") == SKILL_NAME]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one discovered {SKILL_NAME}; got {len(matches)}")
    skill = matches[0]
    if Path(skill.get("path", "")).resolve() != installed.resolve():
        raise ValueError("Codex discovered a different installation")
    if skill.get("enabled") is not True or skill.get("scope") != "user":
        raise ValueError("Installed skill must be enabled in user scope")
    fields = parse_required_fields(parse_frontmatter(installed.read_text(encoding="utf-8"))[0])
    if skill.get("description") != fields["description"]:
        raise ValueError("Discovered metadata differs from installed SKILL.md")
    return skill


def verify_invocation(events: list[dict], result: dict, fixture: dict, installed: Path) -> None:
    if any(event.get("type") in ("turn.failed", "error") for event in events):
        raise ValueError("Codex reported a failed turn or error")
    if not any(event.get("type") == "turn.completed" for event in events):
        raise ValueError("No completed Codex turn")
    # A self-reported skill name, or merely mentioning a filename, is not evidence.
    reads = [event.get("item", {}) for event in events if event.get("type") == "item.completed"]
    for path in (installed, installed.parent / "references" / "contracts.md"):
        content = path.read_text(encoding="utf-8").strip()
        if not any(
            item.get("type") == "command_execution"
            and item.get("status") == "completed" and item.get("exit_code") == 0
            and str(path) in item.get("command", "")
            and content in item.get("aggregated_output", "")
            for item in reads
        ):
            raise ValueError(f"No successful, complete read of installed {path.name} in trace")
    expected = {
        "skill": SKILL_NAME, "default_attempt_budget": 2, "max_failed_attempts": 5,
        "nonce": fixture["nonce"], "total": sum(fixture["values"]),
    }
    if result != expected:
        raise ValueError("Invocation result differs from independently computed result / skill policy")


def snapshot(directory: Path) -> dict[str, bytes]:
    return {str(path.relative_to(directory)): path.read_bytes()
            for path in directory.rglob("*") if path.is_file()}


def invoke(codex: str, work: Path, env: dict, evidence: Path, installed: Path,
           model: str | None, timeout: int) -> None:
    fixture = {"nonce": secrets.token_hex(16), "values": [secrets.randbelow(1000) for _ in range(8)]}
    save_json(work / "input.json", fixture)
    save_json(work / "response.schema.json", SCHEMA)
    save_json(evidence / "fixture.json", fixture)
    (evidence / "prompt.txt").write_text(PROMPT, encoding="utf-8")
    before_work, before_skill = snapshot(work), snapshot(installed.parent)
    command = [codex, "-c", 'approval_policy="never"', "exec", "--sandbox", "read-only",
               "--skip-git-repo-check", "--cd", str(work), "--json", "--color", "never",
               "--output-schema", str(work / "response.schema.json"),
               "--output-last-message", str(evidence / "result.json")]
    if model:
        command.extend(["--model", model])
    command.append("-")
    save_json(evidence / "command.json", command)
    with (evidence / "events.jsonl").open("w", encoding="utf-8") as out, \
         (evidence / "invocation.stderr.log").open("w", encoding="utf-8") as err:
        proc = subprocess.Popen(command, cwd=work, env=env, stdin=subprocess.PIPE,
                                stdout=out, stderr=err, text=True, start_new_session=True)
        try:
            proc.communicate(PROMPT, timeout=timeout)
        finally:
            stop_process(proc)
    if proc.returncode != 0:
        raise RuntimeError(f"codex exec exited {proc.returncode}; see invocation.stderr.log")
    if snapshot(work) != before_work or snapshot(installed.parent) != before_skill:
        raise ValueError("Invocation modified the read-only fixture or installed skill")
    events = [json.loads(line) for line in (evidence / "events.jsonl").read_text().splitlines() if line.strip()]
    result = json.loads((evidence / "result.json").read_text())
    verify_invocation(events, result, fixture, installed)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex", default="codex", help="Codex CLI executable (CI pins 0.159.2)")
    parser.add_argument("--live", action="store_true", help="also make one real model invocation")
    parser.add_argument("--auth-file", type=Path, help="explicit local auth.json to copy temporarily")
    parser.add_argument("--model", help="optional available model; otherwise use the CLI default")
    parser.add_argument("--timeout", type=int, default=180, help="live timeout in seconds (discovery max 30)")
    parser.add_argument("--output-dir", type=Path, help="new evidence directory; must not exist")
    args = parser.parse_args()
    if os.name != "posix":
        parser.error("Run on Linux, macOS, or WSL; native Windows is not covered")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if not args.live and (args.auth_file or args.model):
        parser.error("--auth-file and --model require --live")
    evidence = (args.output_dir or ROOT / "smoke-results" / secrets.token_hex(6)).resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    report = {"installation": "not_run", "discovery": "not_run", "invocation": "not_run",
              "e2e": "not_run", "requested_live": args.live}
    stage = "installation"
    exit_code = 1
    try:
        archive = ROOT / "tail-offloading.zip"
        check(ROOT, archive)  # Reject unsafe/unexpected ZIP paths before extraction.
        report["package_sha256"] = hashlib.sha256(archive.read_bytes()).hexdigest()
        codex = shutil.which(args.codex)
        if not codex:
            raise RuntimeError("Codex CLI not found; install it or pass --codex")
        report["codex_version"] = subprocess.check_output([codex, "--version"], text=True, timeout=10).strip()
        with tempfile.TemporaryDirectory(prefix="tail-smoke-") as temporary:
            sandbox = Path(temporary).resolve()
            state, work = sandbox / "codex", sandbox / "work"
            state.mkdir(mode=0o700)
            work.mkdir()
            with ZipFile(archive) as package:
                package.extractall(state / "skills")
            installed = state / "skills" / SKILL_NAME / "SKILL.md"
            validate(installed.parent)
            report["installation"] = "passed"
            # CODEX_HOME is used for its documented purpose, only in child processes.
            # Never modify the caller's home, config, skills, or login state.
            child_env = os.environ.copy()
            child_env["CODEX_HOME"] = str(state)
            for key in ("CODEX_API_KEY", "OPENAI_API_KEY"):
                child_env.pop(key, None)
            stage = "discovery"
            discovered = discover(codex, work, child_env, evidence, min(args.timeout, 30))
            save_json(evidence / "discovery.json", discovered)
            report["discovered_skill"] = verify_discovery(discovered, work, installed)
            report["discovery"] = "passed"
            if args.live:
                stage = "invocation"
                api_key = os.environ.get("CODEX_API_KEY")
                if args.auth_file:
                    # Copy only explicit auth, never a user's config/hooks/MCP setup.
                    with (state / "auth.json").open("xb") as dest:
                        os.chmod(dest.name, 0o600)
                        dest.write(args.auth_file.expanduser().read_bytes())
                elif api_key:
                    child_env["CODEX_API_KEY"] = api_key
                else:
                    report["invocation"] = "blocked"
                    raise RuntimeError("Live run requires --auth-file or CODEX_API_KEY; discovery alone is not E2E")
                invoke(codex, work, child_env, evidence, installed, args.model, args.timeout)
                report["invocation"] = report["e2e"] = "passed"
        exit_code = 0
    except KeyboardInterrupt:
        report[stage] = "interrupted"
        if args.live:
            report["e2e"] = "interrupted"
        report["error"] = "Smoke run interrupted; no success is claimed"
        exit_code = 130
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, BadZipFile,
            subprocess.SubprocessError) as exc:
        if report[stage] != "blocked":
            report[stage] = "failed"
        if args.live:
            report["e2e"] = "blocked" if report[stage] == "blocked" else "failed"
        report["error"] = str(exc)
    finally:
        save_json(evidence / "report.json", report)
        print(json.dumps(report, indent=2))
        print(f"Evidence: {evidence}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
