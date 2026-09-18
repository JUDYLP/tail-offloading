# Work contracts and escalation reports

Read this reference when creating a subagent task, retrying a failed work unit, or escalating it to a stronger model.

## Subagent work contract

```text
Work unit: <short name>
Tier: <small | mid | strong>
Attempt: <1-5>

Objective:
<one concrete outcome>

Inputs and scope:
- <specific files, data, URLs, or prior artifacts>
- May change: <exact paths or resources>
- Must not change: <boundaries and external side effects>

Deliverable:
<file, patch, structured findings, or command result>

Success evidence:
<test command, schema, invariant, or review checklist>

Prior evidence:
<only facts needed from earlier attempts; omit on attempt 1>

On failure:
Return the exact error, what you tried, artifacts created, likely failure class,
and the smallest useful next step. Do not silently broaden scope.
```

## Attempt ledger

```text
Attempt <n>
- Approach:
- Observable result:
- Failure class: implementation | environment | missing input | ambiguity | permission | external dependency
- New evidence:
- Next change:
```

An attempt without a changed method or new evidence should not be run.

## Escalation bundle

```text
Escalated work unit: <name>
Original objective: <objective>
Reason for escalation: <five attempts reached or early-escalation condition>

What is known:
- <verified fact>

Attempts:
1. <approach -> result>
2. <approach -> result>
...

Artifacts and exact errors:
- <paths, diffs, logs, commands, error text>

Uncertainty:
- <what still needs stronger reasoning>

Requested decision:
<diagnose, redesign, implement, or identify a true blocker>
```

## Retry and escalation guidance

Use a retry for a plausible execution mistake that can be tested with a materially different approach. Escalate immediately for ambiguous requirements, architecture decisions, conflicting constraints, unsafe operations, or repeated evidence of the same external blocker.

If the failure is caused by missing authorization or unavailable external state, return it to the primary agent. A stronger model cannot solve an absent permission, credential, service, or user decision.
