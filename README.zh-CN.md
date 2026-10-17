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

修改分发文件后，重新生成 ZIP 并检查：

```bash
python3 scripts/build_package.py
python3 scripts/build_package.py --check
```

分发包在 `tail-offloading/` 下包含 SKILL.md、中英文 README、LICENSE 和两份 Markdown 引用。CI 会拒绝缺失、多余或内容与源码不一致的文件。构建和校验脚本保留在源码仓库中。

## 安装后冒烟测试

在源码仓库中执行，需要 Linux、macOS 或 WSL、Python 3.10+ 和 Codex CLI。
CI 固定使用 `@openai/codex@0.159.2`；本地可通过 `--codex /path/to/codex`
指定程序。报告会记录实际版本。

```bash
# 由真实 Codex 验证发现，不需要登录，也不调用模型。
python3 scripts/smoke_skill.py

# 使用明确指定的本地 Codex 登录，进行一次真实模型调用。
python3 scripts/smoke_skill.py --live --auth-file "${CODEX_HOME:-$HOME/.codex}/auth.json"
```

也可以给 `--live` 提供已有的 `CODEX_API_KEY` 环境变量。隔离环境使用 CLI
默认模型；需要时用 `--model <可用模型>` 指定，不复制个人模型或服务商配置。
真实调用会消耗模型额度，默认超时 180 秒，可通过 `--timeout` 调整。

脚本先校验已提交的 ZIP 与源码一致，再解压到临时
`CODEX_HOME/skills/tail-offloading/`，从另一个空工作目录启动全新 Codex 进程。
它不修改个人 Skill 安装目录。发现阶段调用真实 app-server 的 `skills/list`，
要求恰好发现一个同名 Skill，路径和描述正确、已启用、属于用户级，且没有解析错误。
这验证的是 README 的 `.codex/skills` 安装布局在报告所列 CLI 版本上的行为，
不代表所有 Codex 版本或桌面界面都已验证。

`--live` 会另起 `codex exec`，仅通过 `Use $tail-offloading ...` 显式调用，
不把 Skill 正文或安装路径塞进提示词。断言包括：

- 回合成功完成；JSONL 执行记录中有成功读取安装后的 `SKILL.md` 和契约引用的
  shell 命令，且输出包含完整文件内容。
- 正确返回默认尝试预算 2 和失败上限 5。
- 从每次新生成的随机输入文件中读取 nonce 并求和，由脚本独立核对。
- 工作样本和安装后的 Skill 无改动。命令使用只读沙箱，不允许自动请求审批；
  这个小任务走 Skill 的直接执行分支。

本测试只验证安装和显式调用，不评价委派、升级质量、成本收益或自动选用 Skill。

证据保存到新建且已被 Git 忽略的 `smoke-results/<run-id>/`，包含 `report.json`
和发现结果；真实调用还保留提示词、输入、JSONL 记录、stderr 与最终 JSON。
可通过 `--output-dir <新目录>` 指定位置。临时 Codex 状态及明确复制的登录文件
会在结束后删除，证据不包含凭据。不要上传个人 Codex 主目录。

CI 在 PR、main 推送及手动触发时运行单元测试、结构检查、包一致性检查和
**真实发现验证**，上传发现证据，不使用凭据或模型额度。
其中 `invocation` 和 `e2e` 保持 `not_run`，CI 绿灯不等于真实调用通过。
使用已获授权的本地登录执行 `--live`，才能补齐这项证据。
缺少凭据或断言失败时退出码非零，不把模拟结果或跳过调用计为成功。

接口依据：[Codex app-server Skills](https://developers.openai.com/codex/app-server#skills)
和[非交互模式](https://developers.openai.com/codex/noninteractive)。

## 相关项目

本 Skill 属于模型路由和子代理编排方向，采用与模型供应商无关的工作契约和有证据的失败次数上限。

- [claude-router](https://github.com/vimoxshah/claude-router)：使用固定模型通道、复用执行者上下文，并携带日志升级失败的实现。
- [pi-sub-agent](https://github.com/wquguru/skills/tree/main/skills/pi-sub-agent)：由强模型负责统筹和独立验证，把明确的执行任务交给成本较低的外部模型。
- [subagent-driven-development](https://github.com/obra/superpowers/tree/main/skills/subagent-driven-development)：使用紧凑任务说明、文件化进度和分阶段审查。
- [model-hierarchy-skill](https://github.com/zscole/model-hierarchy-skill)：提供简单的任务复杂度到模型层级分类。
- [agent-router](https://github.com/seslak/agent-router)：在本地 MCP 服务中分离工作流、专家选择、模型排名和结果记录。

## 许可证

MIT
