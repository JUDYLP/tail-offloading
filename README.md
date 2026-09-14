# Tail Offloading

A Codex skill for routing routine, low-risk work to smaller or cheaper subagents while keeping planning, integration, and final verification with a stronger model.

## 中文介绍

**Tail Offloading（脏活累活外包）** 是一个给 Codex 使用的任务分流
Skill。它把边界清楚、容易验收、失败可回滚的重复工作交给成本更低的
子代理；主代理始终负责拆解任务、确定边界、整合结果和最终验收。

它的目标不是尽可能多地启动子代理，而是在质量可控的前提下，减少高档
模型处理检索、整理、格式化、模板化修改和已有方案落地等工作的时间与
Token 消耗。

每个子任务都要带一份简短契约：目标、输入、允许修改的范围、交付物和
可验证的成功条件。低成本模型默认最多尝试两次；每次失败必须改变方法
并记录证据。五次是绝对上限，而不是必须用完的额度。达到上限，或任务
出现需求歧义、跨模块耦合、安全风险、架构判断等信号时，Skill 会把完整
的失败记录、日志和已有产物交给更强的模型处理，避免从头重复排查。

适合的工作包括：仓库盘点、针对性检索、信息抽取和分类、格式整理、
可批量验证的修改、测试执行、文档初稿，以及已确定设计下的实现。涉及
架构、产品判断、权限与安全、破坏性操作和最终结论的工作，应保留给主
代理或更强模型。

The skill adds a bounded escalation rule: a small-model work unit may make at most five evidence-bearing attempts. Every retry must change the approach. Earlier escalation is required when the task becomes ambiguous, cross-cutting, sensitive, destructive, or blocked by missing authority.

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
- Prefer read-only workers and file-based handoffs where possible.
- Parallelize independent work; serialize overlapping edits.
- Never repeat an identical failed attempt.
- Treat five attempts as a ceiling rather than a quota.
- Verify every contribution before integration.

## Related work

This skill belongs to an active family of model-routing and subagent-orchestration
projects. It is intentionally provider-neutral and centers a portable work
contract plus an evidence-bearing five-attempt ceiling.

- [claude-router](https://github.com/vimoxshah/claude-router) uses model-pinned
  lanes, reuses worker context, and escalates failed implementation with logs.
- [pi-sub-agent](https://github.com/wquguru/skills/tree/main/skills/pi-sub-agent)
  keeps orchestration and independent verification in the strong model while
  sending well-specified execution to cheaper external models.
- [subagent-driven-development](https://github.com/obra/superpowers/tree/main/skills/subagent-driven-development)
  uses compact task briefs, file-backed progress, and staged review.
- [model-hierarchy-skill](https://github.com/zscole/model-hierarchy-skill)
  provides a simple complexity-to-model-tier classifier.
- [agent-router](https://github.com/seslak/agent-router) separates workflow,
  specialist choice, model ranking, and outcome logging in a local MCP service.

## License

MIT
