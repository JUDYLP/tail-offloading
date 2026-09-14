---
name: tail-offloading
description: Route bounded, low-risk, easily verified work to smaller or cheaper subagents, then escalate persistent failures to a stronger model. Use for substantial tasks with separable routine work; skip tiny, tightly coupled, or primarily architectural tasks.
---

# Tail Offloading

Use model tiers as an execution hierarchy. The primary agent owns decomposition, routing, integration, and final verification. Subagents produce bounded artifacts; they do not redefine the task or declare the overall job complete.

## Decide whether to delegate

Delegate a work unit to the lowest-cost available model when all of these are true:

- its inputs, output, and boundaries can be stated precisely;
- it can run independently without editing the same files as another active worker;
- correctness can be checked cheaply with a command, schema, diff, or focused review;
- failure is reversible and has low impact.

Good candidates include repository inventory, targeted searches, extraction and classification, repetitive edits, formatting, test execution, documentation drafts, and implementation from an already approved design.

Keep work with the primary or a stronger model when it requires architecture, ambiguous product judgment, cross-cutting reasoning, security or privacy judgment, destructive operations, final synthesis, or acceptance of the completed result.

Do not delegate merely to create activity. Estimate total cost as worker setup,
context transfer, execution, retries, result return, and primary-agent
verification. If that total is likely to exceed direct execution, do the work
directly. A cheaper token price does not help when a worker needs substantially
more turns.

## Create a work contract

Before spawning a subagent, give it a compact contract containing:

1. one objective;
2. exact inputs, files, and allowed scope;
3. constraints and actions it must not take;
4. the required deliverable;
5. the command or evidence that proves success;
6. the current attempt number and what previous attempts established.

Pass only the context the worker needs. Prefer a fresh or minimally forked
context for the first routine dispatch. Put large briefs, logs, and reports in
files and send paths plus a compact summary instead of pasting them into every
message.

Resume the same worker for materially different retries so it retains local
context; send only the new evidence and changed instruction. Use a fresh,
stronger worker on escalation and provide the failure bundle so it does not
repeat discovery.

Prefer read-only workers for search, inventory, review, and diagnosis. Grant
write scope only to implementation workers whose allowed paths and validator
are explicit.

When two or more work units are independent, run them concurrently within the environment's agent limit. Serialize overlapping edits and dependent steps.

For copy-ready contracts and escalation reports, read [references/contracts.md](references/contracts.md).

## Apply the five-attempt policy

Allow at most five unsuccessful small-model attempts for one work unit. Budget
two attempts by default. Continue through attempts three to five only while the
work remains cheap, each round produces new evidence, and success still has a
clear deterministic check.

- Count an attempt only after the worker performs the requested work and returns an observable result or failure.
- Require each retry to change the hypothesis, method, input, or validation step. Never repeat an identical attempt.
- Keep a short attempt ledger: approach, evidence, failure class, and next change.
- End the retry loop immediately on success, a stable external blocker, missing authorization, or a condition that requires stronger judgment.
- Escalate after two failed validations when the next retry lacks a specific new
  hypothesis or when retry overhead is approaching the cost of stronger-model
  execution.
- Escalate before attempt five when the task proves ambiguous, cross-cutting,
  security-sensitive, destructive, or architecturally coupled.

After five unsuccessful attempts, stop assigning the same work unit to the same model tier. Send a failure bundle to a stronger available model or return it to the primary agent. The bundle must contain the contract, attempt ledger, relevant diffs or artifacts, exact errors, and remaining uncertainty.

The five-attempt limit is a ceiling, not a target. Do not spend five attempts on a blocker that cannot change.

## Choose model tiers

Use capabilities exposed by the current environment rather than assuming particular model names exist.

- Small/cheap tier: deterministic, local, repetitive, and cheaply verifiable execution.
- Mid tier: implementation that needs moderate reasoning or recovery from a novel error.
- Strong tier: planning, ambiguity resolution, architecture, failure diagnosis after bounded retries, and final review.

If the environment cannot select a model per subagent, still use the same contracts and retry policy; delegate only when parallelism or context isolation provides a clear benefit.

## Integrate and verify

Treat every subagent result as a candidate contribution.

1. Check the deliverable against the original contract.
2. Inspect the diff or artifact for scope creep and conflicts.
3. Run the stated validator or an equivalent independent check.
4. Integrate only verified work.
5. Use a stronger model for final review when multiple work units interact or the overall result carries material risk.

Report the model-routing decisions only when they help the user understand cost, latency, a failure, or an escalation. Preserve normal approval and permission boundaries; delegation never expands authority.
