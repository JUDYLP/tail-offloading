# Tail Offloading

**English** | [简体中文](README.zh-CN.md)

A Codex skill for routing routine, low-risk, easily verified work to smaller or cheaper subagents while keeping planning, integration, and final verification with a stronger model.

## Overview

Tail Offloading delegates repetitive work with clear boundaries, cheap validation, and reversible failure to lower-cost subagents. The primary agent remains responsible for decomposition, scope, integration, and final acceptance.

The goal is not to launch as many subagents as possible. The goal is to reduce the time and tokens spent by stronger models on repository inventory, targeted search, extraction, formatting, repetitive edits, test execution, documentation drafts, and implementation from an already approved design—without giving up verification.

Every delegated work unit receives a compact contract containing its objective, inputs, allowed scope, deliverable, and observable success criteria. A lower-cost worker gets two attempts by default. Every retry must change the method and add evidence. Five failed attempts are an absolute ceiling, not a quota.

Escalation happens earlier when the work becomes ambiguous, cross-cutting, security-sensitive, destructive, architecturally coupled, or blocked by missing authority. The stronger model receives the work contract, attempt ledger, exact errors, and existing artifacts so it does not repeat discovery from scratch.

Architecture, product judgment, permissions and security, destructive operations, and final conclusions remain with the primary agent or a stronger model.

## Install

Copy this repository into your Codex skills directory so that the resulting path is:

```text
~/.codex/skills/tail-offloading/SKILL.md
```

Start a new Codex task after installation so the skill can be discovered.

## Use

Invoke it explicitly:

```text
Use $tail-offloading to implement this plan. Send repetitive, isolated work to the lowest-cost capable agents, keep an attempt ledger, escalate persistent failures, and verify the integrated result.
```

It can also be selected automatically for substantial tasks that contain separable routine work.

## Design principles

- Delegate only work with precise boundaries and cheap validation.
- Give each worker one compact contract and minimal context.
- Count setup, context transfer, retries, and verification in routing cost.
- Resume the same worker for retries; escalate to a fresh stronger worker with a failure bundle.
- Prefer read-only workers for search, inventory, and review.
- Parallelize independent work; serialize overlapping edits.
- Never repeat an identical failed attempt.
- Treat five attempts as a ceiling rather than a target.
- Verify every contribution before integration.

See [work contracts and escalation templates](references/contracts.md) and the [worked routing example](references/example.md).

## Validate

Run:

```bash
python3 scripts/validate_skill.py
```

The check validates SKILL.md frontmatter, the skill directory name, and referenced Markdown files. GitHub Actions runs the same check on pull requests and pushes to the default branch.

After changing packaged files, rebuild the distribution ZIP and check it:

```bash
python3 scripts/build_package.py
python3 scripts/build_package.py --check
```

The package contains SKILL.md, both READMEs, LICENSE, and the two Markdown references under `tail-offloading/`. CI rejects missing, extra, or changed package contents. Build and validation scripts remain in the source repository.

## Installed-skill smoke test

Run from a source checkout on Linux, macOS, or WSL with Python 3.10+ and the
Codex CLI installed. CI pins `@openai/codex@0.159.2`; `--codex /path/to/codex`
selects another local executable, and each report records its version.

```bash
# Real Codex discovery, no login or model call required.
python3 scripts/smoke_skill.py

# One real model call using an explicitly selected local Codex login.
python3 scripts/smoke_skill.py --live --auth-file "${CODEX_HOME:-$HOME/.codex}/auth.json"
```

Alternatively, `--live` accepts an existing `CODEX_API_KEY` environment variable.
The isolated run uses the CLI's default model; pass `--model <available-model>`
if needed. It does not copy your model/provider configuration. Live runs consume
model quota and have a 180-second timeout, configurable with `--timeout`.

The script checks the committed ZIP against source, extracts it into a temporary
`CODEX_HOME/skills/tail-offloading/`, and starts a fresh Codex process in a separate
empty directory. It never installs into your real skills directory. Discovery uses
the actual app-server `skills/list` endpoint and requires exactly one enabled
user skill with the expected name, installation path, and description, with no
discovery errors. This tests the README's `.codex/skills` layout on the recorded
CLI version; it does not claim support for every Codex release or desktop UI.

With `--live`, a new `codex exec` process receives `Use $tail-offloading ...`,
without the skill body or installation path in the prompt. The test requires:

- A successful turn and successful shell reads of the installed `SKILL.md` and
  its contract reference, including their contents in the JSONL trace.
- The skill's default attempt budget (2) and failure ceiling (5) in the result.
- The correct nonce and sum from a fresh random input file, checked independently.
- No changes to the fixture or installed skill. Commands run in a read-only
  sandbox with approvals disabled; the tiny task uses the skill's direct path.

This is an installation/explicit-invocation smoke test. It does not evaluate
delegation, escalation quality, cost savings, or automatic skill selection.

Evidence goes to a new ignored `smoke-results/<run-id>/` directory: `report.json`,
discovery metadata and, for live runs, the prompt, fixture, JSONL trace, stderr,
and final JSON. `--output-dir <new-directory>` selects a different location.
The temporary Codex state (including any explicitly copied auth file) is deleted;
credentials are never included in evidence. Do not upload your Codex home.

CI runs unit tests, structural/package checks, and **real discovery only**, on
pull requests, main pushes, and manual workflow dispatch. It uploads discovery
evidence without credentials or model cost. `invocation` and `e2e` remain
`not_run`; a green CI run is not a live E2E pass. Run `--live` locally with an
authorized login to obtain that evidence. Missing credentials or any failed
assertion exits nonzero; no mock result or skipped live run counts as success.

Protocol references: [Codex app-server skills](https://developers.openai.com/codex/app-server#skills)
and [non-interactive mode](https://developers.openai.com/codex/noninteractive).

## Related work

This skill belongs to an active family of model-routing and subagent-orchestration projects. It is provider-neutral and centers a portable work contract plus an evidence-bearing attempt ceiling.

- [claude-router](https://github.com/vimoxshah/claude-router) uses model-pinned lanes, reuses worker context, and escalates failed implementation with logs.
- [pi-sub-agent](https://github.com/wquguru/skills/tree/main/skills/pi-sub-agent) keeps orchestration and independent verification in the strong model while sending well-specified execution to cheaper external models.
- [subagent-driven-development](https://github.com/obra/superpowers/tree/main/skills/subagent-driven-development) uses compact task briefs, file-backed progress, and staged review.
- [model-hierarchy-skill](https://github.com/zscole/model-hierarchy-skill) provides a simple complexity-to-model-tier classifier.
- [agent-router](https://github.com/seslak/agent-router) separates workflow, specialist choice, model ranking, and outcome logging in a local MCP service.

## License

MIT
