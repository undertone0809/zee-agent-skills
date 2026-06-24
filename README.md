# Zee Skills

[中文](README.zh-CN.md)

Zee Skills is a collection of Agent Skills for turning repeated work into
reusable agent capability.

The repo is built around a simple operating belief: skills improve through
practice. Real tasks expose what a skill can do, where it breaks, how it should
trigger, what evidence it needs, and what output quality looks like. Good skill
maintenance turns those observations into clearer instructions, validation
cases, evals, examples, and packaging.

```text
practice
-> evidence
-> skill change
-> eval or validation case
-> better next run
```

## What Is In This Repo

- [`meta-skills`](meta-skills/README.md): create, extract, optimize, evaluate,
  and package Agent Skills.
- [`flomo-skills`](flomo-skills/README.md): search, create, edit, export, and
  analyze flomo memos.
- [`codex-insights`](codex-insights/README.md): generate Claude Code
  `/insights`-style usage reports from local Codex session history.
- [`gstack-style-doc`](gstack-style-doc/README.md): generate technical docs in
  a gstack-inspired style.
- [`screenshot`](screenshot/README.md): capture desktop, app, window, region, or
  full-screen screenshots.

Open a folder README for the detailed skill list and usage notes.

## Why This Repo Exists

Most agent workflows start as messy practice: a successful session, a corrected
answer, a repeated repo operation, a strong review pattern, or a useful research
habit. Those workflows should not stay trapped in one conversation.

This repo is a place to make those patterns durable:

- capture repeated workflows as installable skills
- improve existing skills from real execution traces and user corrections
- add trigger tests and validation cases so skill behavior is reviewable
- keep domain-specific knowledge close to the workflow that uses it
- package skills so another agent can discover and apply them later

The meta-skills collection is the center of that loop. Use it when you want to
turn recent practice into new skills or improve project skills from real
evidence.

## Self-Iteration

The best way to improve Agent Skills is not to wait for a large manual review.
Use a small amount of human feedback, captured from real sessions, and turn it
into a daily skill-maintenance loop.

In Claude Code, Codex, OpenClaw, or any agent runtime that supports scheduled
work, create two recurring automation tasks:

```text
Look at the latest 30 Codex sessions. Considering the existing skills, are there
any new workflows that should become Conversation to Skill outputs?
```

```text
Look at the latest 30 Codex sessions. Considering the existing skills, which
project skills need optimization with Skill Optimizer?
```

This gives you two reports every day:

- new skill candidates that should be extracted from repeated practice
- existing skills that should be patched, clarified, evaluated, or benchmarked

The reports should be evidence-based. A good report links each recommendation
to actual sessions, user corrections, repeated workflow patterns, failure
classes, missing triggers, or validation gaps. The human only needs to review
the high-signal recommendations and approve the patches that matter.

This creates a lightweight but scientific self-iteration loop:

```text
daily sessions
-> automated skill review reports
-> small human feedback
-> Conversation to Skill or Skill Optimizer patches
-> better skills for tomorrow's sessions
```

## Install

Install the folder you want:

```bash
npx skills add Undertone0809/zee-agent-skills/meta-skills
npx skills add Undertone0809/zee-agent-skills/flomo-skills
npx skills add Undertone0809/zee-agent-skills/codex-insights
npx skills add Undertone0809/zee-agent-skills/gstack-style-doc
npx skills add Undertone0809/zee-agent-skills/screenshot
```

For folders that contain multiple skills, such as `meta-skills` and
`flomo-skills`, the CLI can let you choose one skill, several skills, or all
skills in that folder.

## Common Workflows

Create a new skill from real practice:

```text
Look at the latest 30 Codex sessions. Considering the existing skills, are there
any new workflows that should become skills?
```

Improve existing skills from usage evidence:

```text
Look at the latest 30 Codex sessions. Considering the existing skills, which
project skills need optimization?
```

Install one collection for a focused domain:

```bash
npx skills add Undertone0809/zee-agent-skills/meta-skills
```

## Repository Conventions

- Top-level folders are the maintained skill collections.
- Each collection has its own `README.md`.
- Use folder-level install commands, not the repo root install command, for
  nested collections.
- Prefer small, focused skills with clear triggers, workflows, boundaries,
  examples, and validation cases.
