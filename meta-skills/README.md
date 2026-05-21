# Meta Skills

This folder is the maintained source for the meta-level skills used to create,
extract, and improve other Agent Skills.

## Skills

- [`skill-creator`](skill-creator/SKILL.md): create new skills, refine existing
  skills, run evaluation loops, and package skill artifacts.
- [`conversation-to-skill`](conversation-to-skill/SKILL.md): turn a useful
  conversation or repeated workflow into a reusable skill package.
- [`skill-optimizer`](skill-optimizer/SKILL.md): improve, harden, benchmark, or
  refactor an existing skill from evidence, failures, traces, and user
  corrections.

## Install Locally

Codex loads user skills from `~/.agents/skills`. Link these source directories
there:

```bash
mkdir -p ~/.agents/skills

ln -sfn /Users/zeeland/projects/zee-agent-skills/meta-skills/skill-creator \
  ~/.agents/skills/skill-creator
ln -sfn /Users/zeeland/projects/zee-agent-skills/meta-skills/conversation-to-skill \
  ~/.agents/skills/conversation-to-skill
ln -sfn /Users/zeeland/projects/zee-agent-skills/meta-skills/skill-optimizer \
  ~/.agents/skills/skill-optimizer
```

If older links exist under `~/.codex/skills`, remove them so there is only one
source of truth:

```bash
rm -f ~/.codex/skills/skill-creator \
  ~/.codex/skills/conversation-to-skill \
  ~/.codex/skills/skill-optimizer
```
