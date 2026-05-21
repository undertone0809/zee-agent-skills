# Meta Skills

[English](README.md)

Meta skills 用来创建、演进、评估和打包其他 Agent Skills。它们面向把 skill 当作长期工程资产维护的人，而不是把 skill 当成一次性 prompt 的人。

## Why Meta Skills

Agent Skill 不应该是写完就结束的静态说明。真正有用的 skill 会在一次次真实任务里暴露边界、失败模式、触发误差、工具假设和输出质量问题，然后通过工程化的方法持续迭代。

Meta skills 的核心观点是：practice makes perfect。把真实实践变成证据，把证据变成 failure class、workflow patch、trigger eval、validation case 和可审阅的 skill 变更，才能系统性提升 agent 的长期能力。

换句话说，meta skills 不是帮你写更长的 prompt，而是帮你建立一套 skill engineering loop：

```text
真实任务或会话
-> 观察成功经验、用户纠正和失败模式
-> 判断该创建新 skill 还是优化现有 skill
-> 产出可审阅的 skill 变更
-> 增加 eval / trigger case / validation case
-> 下一次实践继续验证和迭代
```

## 适合什么时候用

当你发现某类 agent 行为值得复用、沉淀或系统性改进时，就适合使用 meta skills。

- 从真实会话中提炼一个新的 reusable workflow。
- 某个流程已经被多次重复执行，应该变成可发现、可加载的 Agent Skill。
- 现有 skill 触发不稳定、边界不清、输出不一致，或者经常被用户纠正。
- 一次失败、返工、review blocker 或成功经验暴露了可以长期复用的规则。
- 你想给 skill 增加 trigger eval、validation case、benchmark plan 或打包说明。
- 你想把“经验”变成可审阅、可测试、可迭代的工程资产。

## 常见用户场景

最常见的用法是基于真实实践来优化 Agent Skill：

```text
看一下最近 30 个 Codex session，结合现有的 skills，有哪些新的需要 conversation-to-skill 吗？
```

使用 [`conversation-to-skill`](conversation-to-skill/SKILL.md) 从近期真实会话里识别可复用的新流程，并生成新的 skill package。

```text
看一下最近 30 个 Codex session，结合现有的 skills，哪些 project skill 需要优化吗？
```

使用 [`skill-optimizer`](skill-optimizer/SKILL.md) 从执行痕迹、用户纠正、失败模式和验证结果中找出现有 skill 的优化点。

也可以直接用于更具体的场景：

- “把这次成功的发布流程沉淀成一个 skill。”
- “这个 skill 经常误触发，帮我优化 description 和 trigger eval。”
- “基于这次失败，给现有 skill 加一组 validation cases。”
- “把这个 skill package 整理到可安装、可评估的状态。”

## 自迭代最佳实践

Meta skills 最有价值的使用方式，是把它们变成一个持续运行的 skill-maintenance loop。你不需要很重的人工流程；只要把真实 session 里的少量人工反馈系统性复盘，就足以持续提升 skill 质量。

在 Claude Code、Codex、OpenClaw，或者任何支持 scheduled work 的 agent runtime 里，创建两个每日自动化任务：

```text
看一下最近 30 个 Codex session，结合现有的 skills，有哪些新的需要 Conversation to Skill 吗？
```

使用 [`conversation-to-skill`](conversation-to-skill/SKILL.md) 把重复出现的成功 workflow、被用户纠正过的流程、逐渐稳定下来的 SOP，转成新的 skill package。

```text
看一下最近 30 个 Codex session，结合现有的 skills，哪些 project skill 需要优化吗 Skill Optimizer？
```

使用 [`skill-optimizer`](skill-optimizer/SKILL.md) 把用户纠正、执行失败、误触发、漏触发、弱输出和 validation gap，转成小而可审阅的 patch。

每份报告都应该包含：

- 每个建议背后的真实 session 证据。
- 这个建议是新 skill candidate，还是现有 skill patch。
- 对应的 failure class 或重复成功模式。
- 建议修改哪个 skill，以及怎么改。
- 用什么 eval、trigger case 或 validation case 证明这个改动有效。

这样你每天会收到两份报告：一份发现新的 skill 机会，一份发现已有 project skills 的优化点。人只需要 review 高信号建议，批准真正值得合入的 patch，然后让第二天的真实 session 继续验证 skill 是否变强。

## Skills

- [`skill-creator`](skill-creator/SKILL.md)：创建新 skill、优化已有 skill、运行评估循环，并打包 skill artifact。
- [`conversation-to-skill`](conversation-to-skill/SKILL.md)：把有价值的会话或重复流程转成可复用的 skill package。
- [`skill-optimizer`](skill-optimizer/SKILL.md)：基于证据、失败、执行痕迹和用户纠正，优化、加固、benchmark 或重构已有 skill。

## 安装

安装 meta-skills collection：

```bash
npx skills add Undertone0809/zee-agent-skills/meta-skills
```

CLI 可以让你安装全部 meta skills，也可以只选择需要的 skill。

## 怎么用

你可以从两类入口开始：

1. 需要新 skill：使用 [`conversation-to-skill`](conversation-to-skill/SKILL.md)，从会话、SOP、团队流程或成功实践中提炼新 skill。
2. 需要优化旧 skill：使用 [`skill-optimizer`](skill-optimizer/SKILL.md)，从真实证据中诊断、patch、验证和 benchmark 现有 skill。

如果还不确定是创建还是优化，可以先让 agent 审视近期会话和已有 skill：它应该判断哪些经验适合创建新 skill，哪些问题应该回写到现有 skill。
