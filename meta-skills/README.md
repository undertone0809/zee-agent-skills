# Meta Skills

Meta skills help you create, evolve, evaluate, and package other Agent Skills.
They are for teams and individual builders who treat skills as living software,
not one-time prompts.

## 中文

### Why Meta Skills

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

### 适合什么时候用

当你发现某类 agent 行为值得复用、沉淀或系统性改进时，就适合使用 meta skills。

- 从真实会话中提炼一个新的 reusable workflow。
- 某个流程已经被多次重复执行，应该变成可发现、可加载的 Agent Skill。
- 现有 skill 触发不稳定、边界不清、输出不一致，或者经常被用户纠正。
- 一次失败、返工、review blocker 或成功经验暴露了可以长期复用的规则。
- 你想给 skill 增加 trigger eval、validation case、benchmark plan 或打包说明。
- 你想把“经验”变成可审阅、可测试、可迭代的工程资产。

### 常见用户场景

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

### 怎么用

安装 meta skills：

```bash
npx skills add Undertone0809/zee-agent-skills/meta-skills
```

然后在 Codex 或支持 Agent Skills 的运行环境里直接描述目标。你可以从两类入口开始：

1. 需要新 skill：使用 [`conversation-to-skill`](conversation-to-skill/SKILL.md)，从会话、SOP、团队流程或成功实践中提炼新 skill。
2. 需要优化旧 skill：使用 [`skill-optimizer`](skill-optimizer/SKILL.md)，从真实证据中诊断、patch、验证和 benchmark 现有 skill。

如果还不确定是创建还是优化，可以先让 agent 审视近期会话和已有 skill：它应该判断哪些经验适合创建新 skill，哪些问题应该回写到现有 skill。

## English

### Why Meta Skills

Agent Skills should not be static instructions that are written once and then left alone. Useful skills reveal their real boundaries through practice: missed triggers, unclear assumptions, brittle workflows, tool gaps, weak outputs, user corrections, and repeated failure modes.

The core idea behind meta skills is simple: practice makes perfect. Real work should produce evidence. Evidence should become failure classes, workflow patches, trigger evals, validation cases, and reviewable changes. That is how agent capability improves systematically over time.

Meta skills are not about writing longer prompts. They are a skill engineering loop:

```text
real tasks or conversations
-> observe wins, corrections, and failure modes
-> decide whether to create a new skill or improve an existing one
-> produce a reviewable skill change
-> add evals, trigger cases, and validation cases
-> validate again in future practice
```

### When To Use Meta Skills

Use meta skills when an agent workflow should become reusable, more reliable, easier to trigger, or easier to evaluate.

- Extract a new reusable workflow from a real conversation.
- Turn a repeated process into a discoverable Agent Skill.
- Improve an existing skill that misfires, under-triggers, over-triggers, or produces inconsistent outputs.
- Convert a failure, rework cycle, review blocker, or successful run into durable skill instructions.
- Add trigger evals, validation cases, benchmark plans, or packaging docs to a skill.
- Turn experience into an engineering asset that can be reviewed, tested, and improved.

### Common Scenarios

The most common workflow is optimizing Agent Skills from real practice:

```text
Look at the latest 30 Codex sessions. Considering the existing skills, are there any new workflows that should become conversation-to-skill outputs?
```

Use [`conversation-to-skill`](conversation-to-skill/SKILL.md) to identify reusable workflows from recent sessions and generate new skill packages.

```text
Look at the latest 30 Codex sessions. Considering the existing skills, which project skills need optimization?
```

Use [`skill-optimizer`](skill-optimizer/SKILL.md) to improve existing skills from traces, user corrections, failure classes, and validation results.

You can also use meta skills for narrower requests:

- “Turn this successful release workflow into a skill.”
- “This skill often mis-triggers; improve the description and trigger evals.”
- “Based on this failure, add validation cases to the existing skill.”
- “Package this skill so it is installable and evaluable.”

### How To Use

Install the meta-skills collection:

```bash
npx skills add Undertone0809/zee-agent-skills/meta-skills
```

Then describe the goal in Codex or another Agent Skills runtime. Start from one of two paths:

1. Create a new skill: use [`conversation-to-skill`](conversation-to-skill/SKILL.md) to extract a reusable workflow from a conversation, SOP, team process, or successful run.
2. Improve an existing skill: use [`skill-optimizer`](skill-optimizer/SKILL.md) to diagnose, patch, validate, and benchmark an existing skill from real evidence.

If you are not sure whether to create or optimize, ask the agent to review recent sessions against the existing skill set. It should separate new skill candidates from improvements that belong in current skills.

## Skills

- [`skill-creator`](skill-creator/SKILL.md): create new skills, refine existing
  skills, run evaluation loops, and package skill artifacts.
- [`conversation-to-skill`](conversation-to-skill/SKILL.md): turn a useful
  conversation or repeated workflow into a reusable skill package.
- [`skill-optimizer`](skill-optimizer/SKILL.md): improve, harden, benchmark, or
  refactor an existing skill from evidence, failures, traces, and user
  corrections.
