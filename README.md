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

## Related work

This skill belongs to an active family of model-routing and subagent-orchestration projects. It is provider-neutral and centers a portable work contract plus an evidence-bearing attempt ceiling.

- [claude-router](https://github.com/vimoxshah/claude-router) uses model-pinned lanes, reuses worker context, and escalates failed implementation with logs.
- [pi-sub-agent](https://github.com/wquguru/skills/tree/main/skills/pi-sub-agent) keeps orchestration and independent verification in the strong model while sending well-specified execution to cheaper external models.
- [subagent-driven-development](https://github.com/obra/superpowers/tree/main/skills/subagent-driven-development) uses compact task briefs, file-backed progress, and staged review.
- [model-hierarchy-skill](https://github.com/zscole/model-hierarchy-skill) provides a simple complexity-to-model-tier classifier.
- [agent-router](https://github.com/seslak/agent-router) separates workflow, specialist choice, model ranking, and outcome logging in a local MCP service.

## License

MIT
