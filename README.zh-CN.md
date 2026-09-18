# Tail Offloading

[English](README.md) | **简体中文**

一个用于 Codex 的任务分流 Skill：把常规、低风险且容易验证的工作交给更小或成本更低的子代理，同时让更强的主模型负责规划、整合与最终验收。

## 项目介绍

**Tail Offloading（尾部任务卸载）** 会把边界清楚、容易验收、失败可回滚的重复工作交给成本更低的子代理；主代理始终负责拆解任务、确定边界、整合结果和最终验收。

它的目标不是尽可能多地启动子代理，而是在质量可控的前提下，减少高档模型处理检索、整理、格式化、模板化修改和既定方案落地等工作的时间与 Token 消耗。

每个子任务都要带一份简短契约：目标、输入、允许修改的范围、交付物和可验证的成功条件。低成本模型默认最多尝试两次；每次失败必须改变方法并记录证据。五次是绝对上限，而不是必须用完的额度。

达到上限，或者任务出现需求歧义、跨模块耦合、安全风险、架构判断等信号时，Skill 会把完整的失败记录、日志和已有产物交给更强的模型处理，避免从头重复排查。

适合分派的工作包括：

- 仓库盘点与针对性检索
- 信息抽取、分类和格式整理
- 可批量验证的修改
- 测试执行与文档初稿
- 按照已经确定的设计完成实现

架构决策、产品判断、权限与安全、破坏性操作以及最终结论，应保留给主代理或更强模型。

## 安装

将本仓库复制到 Codex Skills 目录，最终路径应为：

```text
~/.codex/skills/tail-offloading/SKILL.md
```

安装后启动一个新的 Codex 任务，让系统重新发现 Skill。

## 使用

可以显式调用：

```text
使用 $tail-offloading 实现这个计划。把重复、独立的工作交给成本最低且能力足够的子代理，记录每次尝试，在持续失败时升级模型，并验证最终整合结果。
```

对于包含可分离常规工作的复杂任务，它也可以被自动选择。

## 设计原则

- 只分派边界精确、能够低成本验证的工作。
- 给每个执行者一份简洁契约和最少必要上下文。
- 路由成本必须包含启动、上下文传递、重试和验证。
- 重试时继续使用同一执行者；升级时把失败材料交给更强的新执行者。
- 检索、盘点和审查任务优先采用只读权限。
- 并行执行相互独立的任务，串行处理重叠修改。
- 不重复执行完全相同的失败尝试。
- 五次是失败尝试的上限，不是目标。
- 所有子代理结果都必须经过验证才能整合。

工作契约和升级模板见 [工作契约](references/contracts.md)，完整示例见 [分流示例](references/example.md)。

## 结构验证

运行：

```bash
python3 scripts/validate_skill.py
```

该检查会验证 SKILL.md 的 frontmatter、目录名称以及 Markdown 引用是否完整。GitHub Actions 也会在 Pull Request 和推送到主分支时自动执行。

## 相关项目

本 Skill 属于模型路由和子代理编排方向，采用与模型供应商无关的工作契约和有证据的失败次数上限。

- [claude-router](https://github.com/vimoxshah/claude-router)：使用固定模型通道、复用执行者上下文，并携带日志升级失败的实现。
- [pi-sub-agent](https://github.com/wquguru/skills/tree/main/skills/pi-sub-agent)：由强模型负责统筹和独立验证，把明确的执行任务交给成本较低的外部模型。
- [subagent-driven-development](https://github.com/obra/superpowers/tree/main/skills/subagent-driven-development)：使用紧凑任务说明、文件化进度和分阶段审查。
- [model-hierarchy-skill](https://github.com/zscole/model-hierarchy-skill)：提供简单的任务复杂度到模型层级分类。
- [agent-router](https://github.com/seslak/agent-router)：在本地 MCP 服务中分离工作流、专家选择、模型排名和结果记录。

## 许可证

MIT
