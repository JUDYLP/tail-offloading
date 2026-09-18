# Example: repository inventory with bounded escalation

Use this example to see the routing policy applied to a realistic task. It is illustrative, not a required fixed sequence.

## Request

Inventory a repository, identify every CI workflow, and return a table containing each workflow name, trigger, and referenced secret. Do not modify the repository.

## Initial contract

```text
Work unit: inventory CI workflows
Tier: small
Attempt: 1

Objective:
Return a complete table of CI workflow files, triggers, and referenced secrets.

Inputs and scope:
- Read only .github/workflows/
- May change: nothing
- Must not change: repository files, settings, secrets, or workflow runs

Deliverable:
A Markdown table with source paths and line references.

Success evidence:
Every YAML file under .github/workflows/ appears exactly once, and every
${{ secrets.NAME }} reference found by a repository search appears in the table.

On failure:
Return the exact error, attempted command, partial results, likely failure class,
and the smallest useful next step.
```

## Attempt ledger

```text
Attempt 1
- Approach: enumerate workflow files with the preferred search command
- Observable result: command unavailable in the worker environment
- Failure class: environment
- New evidence: repository is readable, but the preferred command is missing
- Next change: use the platform file-listing API and inspect each YAML file

Attempt 2
- Approach: enumerate files through the platform API and inspect each result
- Observable result: inventory and secret-reference search both pass
- Failure class: none
- New evidence: all five workflow files and three secret references are accounted for
- Next change: return the verified table
```

## Why escalation was not needed

The second attempt changed method, stayed read-only, and had a deterministic completeness check. Escalating after the first environment failure would have cost more without improving the decision.

## Early-escalation variation

If inspection revealed that a workflow deploys to production and the user asked the worker to rewrite its permissions, stop small-model retries. Production permissions are security-sensitive and require stronger review plus explicit authorization before modification.
