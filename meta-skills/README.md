# Meta Skills

[中文](README.zh-CN.md)

Meta skills help you create, evolve, evaluate, and package other Agent Skills.
They are for builders who treat skills as living software, not one-time
prompts.

## Why Meta Skills

Agent Skills should not be static instructions that are written once and then
left alone. Useful skills reveal their real boundaries through practice: missed
triggers, unclear assumptions, brittle workflows, tool gaps, weak outputs, user
corrections, and repeated failure modes.

The core idea behind meta skills is simple: practice makes perfect. Real work
should produce evidence. Evidence should become failure classes, workflow
patches, trigger evals, validation cases, and reviewable changes. That is how
agent capability improves systematically over time.

Meta skills are not about writing longer prompts. They are a skill engineering
loop:

```text
real tasks or conversations
-> observe wins, corrections, and failure modes
-> decide whether to create a new skill or improve an existing one
-> produce a reviewable skill change
-> add evals, trigger cases, and validation cases
-> validate again in future practice
```

## When To Use Meta Skills

Use meta skills when an agent workflow should become reusable, more reliable,
easier to trigger, or easier to evaluate.

- Extract a new reusable workflow from a real conversation.
- Turn a repeated process into a discoverable Agent Skill.
- Improve an existing skill that misfires, under-triggers, over-triggers, or
  produces inconsistent outputs.
- Convert a failure, rework cycle, review blocker, or successful run into
  durable skill instructions.
- Add trigger evals, validation cases, benchmark plans, or packaging docs to a
  skill.
- Turn experience into an engineering asset that can be reviewed, tested, and
  improved.

## Common Scenarios

The most common workflow is optimizing Agent Skills from real practice:

```text
Look at the latest 30 Codex sessions. Considering the existing skills, are there
any new workflows that should become conversation-to-skill outputs?
```

Use [`conversation-to-skill`](conversation-to-skill/SKILL.md) to identify
reusable workflows from recent sessions and generate new skill packages.

```text
Look at the latest 30 Codex sessions. Considering the existing skills, which
project skills need optimization?
```

Use [`skill-optimizer`](skill-optimizer/SKILL.md) to improve existing skills
from traces, user corrections, failure classes, and validation results.

You can also use meta skills for narrower requests:

- "Turn this successful release workflow into a skill."
- "This skill often mis-triggers; improve the description and trigger evals."
- "Based on this failure, add validation cases to the existing skill."
- "Package this skill so it is installable and evaluable."

## Self-Iteration Best Practice

Meta skills are most valuable when they run as a recurring skill-maintenance
loop. You do not need heavy manual process. A small amount of human feedback,
captured from real sessions, is enough when it is reviewed systematically.

In Claude Code, Codex, OpenClaw, or any agent runtime that supports scheduled
work, create two daily automation tasks:

```text
Look at the latest 30 Codex sessions. Considering the existing skills, are there
any new workflows that should become Conversation to Skill outputs?
```

Use [`conversation-to-skill`](conversation-to-skill/SKILL.md) to turn repeated
successful workflows, corrected procedures, and emerging SOPs into new skill
packages.

```text
Look at the latest 30 Codex sessions. Considering the existing skills, which
project skills need optimization with Skill Optimizer?
```

Use [`skill-optimizer`](skill-optimizer/SKILL.md) to turn user corrections,
execution failures, missed triggers, weak outputs, and validation gaps into
small reviewable patches.

Each report should include:

- the session evidence behind each recommendation
- whether the recommendation is a new-skill candidate or an existing-skill patch
- the failure class or repeated success pattern
- the suggested skill change
- the eval, trigger case, or validation case that would prove the change works

With those two reports, the human feedback loop stays small: review the
recommendations, approve the high-signal patches, and let the next day's
sessions test whether the skills improved.

## Skills

- [`skill-creator`](skill-creator/SKILL.md): create new skills, refine existing
  skills, run evaluation loops, and package skill artifacts.
- [`conversation-to-skill`](conversation-to-skill/SKILL.md): turn a useful
  conversation or repeated workflow into a reusable skill package.
- [`skill-optimizer`](skill-optimizer/SKILL.md): improve, harden, benchmark, or
  refactor an existing skill from evidence, failures, traces, and user
  corrections.

## Install

Install the meta-skills collection:

```bash
npx skills add Undertone0809/zee-agent-skills/meta-skills
```

The CLI can let you install all meta skills or only the ones you need.

## How To Use

Start from one of two paths:

1. Create a new skill: use
   [`conversation-to-skill`](conversation-to-skill/SKILL.md) to extract a
   reusable workflow from a conversation, SOP, team process, or successful run.
2. Improve an existing skill: use
   [`skill-optimizer`](skill-optimizer/SKILL.md) to diagnose, patch, validate,
   and benchmark an existing skill from real evidence.

If you are not sure whether to create or optimize, ask the agent to review
recent sessions against the existing skill set. It should separate new skill
candidates from improvements that belong in current skills.
