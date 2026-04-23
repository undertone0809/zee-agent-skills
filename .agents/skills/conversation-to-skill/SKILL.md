---
name: conversation-to-skill
description: >
  Turn the current conversation's workflow into a reusable agent skill. Use this
  whenever the user wants to capture today's task as a repeatable capability,
  says things like "turn this into a skill", "abstract this workflow", "make
  this reusable next time", or is clearly trying to productize a successful
  collaboration into a durable agent pattern. Also use it when a one-off task
  is really becoming a standing workflow and the agent should extract triggers,
  inputs, outputs, steps, and boundaries before writing a new skill.
---

# Conversation To Skill

This skill converts the work happening in the current conversation into a
reusable agent skill.

Its job is not just to write `SKILL.md`.
Its job is to decide what part of the conversation is actually worth
standardizing, separate the stable pattern from one-off details, and then turn
that pattern into a skill the agent can use again later.

## Use This Skill For

Use this skill when the user is trying to:

- turn the current task or workflow into a reusable skill
- capture a successful collaboration pattern so future runs can follow it
- standardize how a class of tasks should be handled
- extract a repeatable agent workflow from the current thread
- package a process, judgment framework, or execution sequence into an agent skill

Typical prompts:

- "Turn what we're doing into a skill."
- "I want this conversation to become an agent capability."
- "Make this reusable for next time."
- "Abstract this workflow into a Codex skill."
- "This should be a standard operating pattern, not a one-off chat."

## Do Not Use This Skill For

Do not use this skill when the user mainly wants:

- a summary of the conversation without creating a reusable skill
- immediate execution of the task with no abstraction step
- a skill generated from multiple unseen threads you cannot inspect
- a rigid template that blindly copies file paths, project names, or temporary constraints

If the conversation does not yet reveal a stable workflow, say that plainly and
help the user clarify the reusable part first.

## Core Principle

The skill should capture the repeatable value, not the accidental details.

A good abstraction preserves:

- the job to be done
- the trigger conditions
- the critical inputs and outputs
- the sequence of reasoning or execution
- the judgment criteria that make the workflow valuable
- the boundaries and non-goals

A bad abstraction copies:

- temporary filenames
- irrelevant project-specific paths
- incidental tools that happened to be used once
- order-of-operations that are not actually essential
- user wording that does not generalize

## Default Workflow

Follow this sequence unless the user already provided enough structure.

### 1. Extract The Candidate Skill From The Current Thread

Read the current conversation first.
Pull out the real workflow before asking the user to restate everything.

Capture:

- what the user was trying to achieve
- what sequence of steps the agent followed or should follow
- which tools or artifacts mattered
- what corrections or preferences the user introduced
- what output the user actually wanted
- what makes this reusable instead of one-off

### 2. Separate Stable Pattern From Incidental Context

Classify each detail into one of three buckets:

- **Core**: must stay because the skill breaks without it
- **Contextual**: useful examples or defaults, but not universal
- **Incidental**: this-thread noise that should not be baked into the skill

Useful heuristic:

- if the detail would still matter in six months on a different project, it is
  probably core
- if it only mattered because of this repository, filename, or user phrasing, it
  is probably contextual or incidental

### 3. Produce An Abstraction Brief Before Writing Files

Before generating the final skill, write a short abstraction brief for the user
to review.

Use this structure:

```markdown
## Skill Intent
- Name:
- Goal:
- Why this should exist:

## Trigger
- Use when:
- Do not use when:

## Inputs
- Required inputs:
- Optional inputs:

## Outputs
- Main deliverable:
- Secondary artifacts:

## Workflow
1. ...
2. ...
3. ...

## Judgment Rules
- What must stay true:
- What to avoid:

## Open Questions
- ...
```

If the conversation already settles these points, keep the brief short and move on.
If important gaps remain, ask only the minimum targeted questions needed.

### 4. Challenge Weak Abstractions

Do not act like a passive stenographer.
If the proposed skill is overfit, under-scoped, or missing the real judgment
logic, say so and correct it.

Common failure modes to call out:

- "This is a transcript, not a skill."
- "These instructions depend on this exact repo, but the user asked for a global skill."
- "The workflow says what to do, but not how to decide when a step is necessary."
- "The description would under-trigger because it only names one phrasing."

### 5. Decide The Skill Shape

Choose the smallest structure that preserves the capability.

Possible outputs:

- `SKILL.md` only, when the workflow is mostly reasoning and sequencing
- `SKILL.md` plus `references/`, when the skill needs domain-specific guidance
- `SKILL.md` plus `scripts/`, when repeated deterministic work should be bundled
- `SKILL.md` plus `evals/`, when the output is objectively testable and worth iterating on

Also decide whether the skill should be:

- **Global**: `~/.agents/skills/<skill-name>`
- **Project-local**: `<project-root>/.agents/skills/<skill-name>`

If the user wants Codex to discover a global skill immediately, also create:

- `~/.codex/skills/<skill-name>` as a symlink to the global skill directory

### 6. Write The Skill

When writing `SKILL.md`, include:

- frontmatter with `name` and a trigger-oriented `description`
- what the skill is for
- when to use it and when not to use it
- the default workflow
- output expectations
- edge cases and boundaries when they materially affect quality

Write the description a little aggressively so the host does not under-trigger it.
The description should mention both the capability and the contexts that should
cause the skill to be used.

### 7. Preserve Generality

Prefer instructions that explain why a step matters.
Avoid brittle mandates unless the workflow truly requires them.

Aim for a skill that can survive beyond this exact thread.

### 8. Close With A Clear Hand-off

After creating or revising the skill, report:

- the chosen skill name
- whether it is global or project-local
- the final path
- whether a Codex symlink was created
- what still needs evaluation, if anything

## Naming Guidance

Choose names that are short, clear, and capability-oriented.

Prefer names like:

- `conversation-to-skill`
- `workflow-standardizer`
- `task-to-playbook`

Avoid names that depend on this thread's temporary wording unless the user
explicitly wants that.

If updating an existing skill, preserve the existing directory name and frontmatter name
unless the user asked for a rename.

## Output Format

Unless the user wants files written immediately, start with:

1. a compact abstraction brief
2. the proposed skill name and placement
3. any risks of overfitting or under-specification

If the user asks to proceed, then write the files.

When the user already said "build it" or "just make it", go straight from the
brief into file creation in the same turn.

## Quality Bar

The resulting skill should make a future agent meaningfully better at the task.

That usually means it captures at least one of these:

- a reusable workflow
- a reusable decision framework
- a reusable artifact format
- a reusable boundary or escalation rule

If it captures none of those, it is probably not a real skill yet.
