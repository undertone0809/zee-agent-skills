---
name: "codex-insights"
description: "Use when the user asks for Claude Code /insights-like reporting for Codex, wants to analyze recent Codex sessions, audit usage patterns, find repeated workflows, identify friction points, or decide which skills/automations should be created or improved from local Codex history. This skill builds evidence-backed reports from local Codex session files instead of guessing from memory."
---

# Codex Insights

Generate an evidence-backed Codex usage report from local Codex history. Treat
this as the Codex version of Claude Code's `/insights`: it analyzes how Codex is
being used, not just the current repository.

## What to produce

Default to a concise Markdown report with these sections:

1. **Current Fact**: what data sources were found, the time window, and how many
   sessions were analyzed.
2. **Usage Patterns**: recurring task families, repositories, languages, and
   interaction shapes.
3. **Friction Points**: repeated failures, blocked states, excessive retries,
   repeated corrections, or unclear handoffs.
4. **Workflow Opportunities**: skills, scripts, README updates, automations, or
   CLAUDE/AGENTS instruction changes that would remove repeated work.
5. **Evidence**: concrete session ids, file paths, timestamps, commands, or
   short sanitized excerpts that support each recommendation.

If the user asks for a quick summary, keep the report short and put the top
recommendations first. If they ask for a deep audit, include the JSON artifact
path and enough evidence for follow-up inspection.

## Data sources

Look for Codex history in this order:

- `$CODEX_HOME` if set, otherwise `~/.codex`
- `state_*.sqlite`
- `session_index.jsonl`
- `sessions/**/*.jsonl`
- `archived_sessions/**/*.jsonl`
- `memories/MEMORY.md` and `memories/rollout_summaries/` only when the user
  asks to connect the report to durable memory or prior audits

Do not read unrelated browser cookies, keychains, shell histories, or project
secrets. Codex insight reports should explain local behavior, not extract
private credentials.

## Use the bundled analyzer first

Prefer the bundled analyzer for the first pass:

```bash
python3 <path-to-skill>/scripts/codex_insights.py --limit 30 --out /tmp/codex-insights
```

Useful options:

```bash
python3 <path-to-skill>/scripts/codex_insights.py --codex-home ~/.codex --limit 100 --out /tmp/codex-insights
python3 <path-to-skill>/scripts/codex_insights.py --cwd /Users/zeeland/projects/rudder-oss --limit 30 --out /tmp/codex-insights-rudder
python3 <path-to-skill>/scripts/codex_insights.py --since 2026-06-01 --out /tmp/codex-insights-june
```

The script writes:

- `report.md`: a Markdown report you can quote or refine.
- `sessions.json`: normalized session records and evidence snippets.
- `summary.json`: aggregate counts and source metadata.

After the script runs, read `report.md` and inspect `sessions.json` only for
claims that need stronger evidence.

## Analysis discipline

- Build a real cohort before judging patterns. Do not infer "latest 30" from
  filenames alone if sqlite or index metadata is available.
- Collapse obvious child/reviewer/subagent sessions under a parent workflow
  when spawn-edge metadata is available. If it is unavailable, say so and avoid
  overclaiming.
- Separate raw session counts from root workflow counts. A fanout-heavy review
  task can create many sessions without meaning the user needs a new skill.
- Prefer current local evidence over memory summaries. Memory is useful for
  context, but the report should say when a fact is memory-derived rather than
  freshly verified.
- Distinguish Codex-first findings from Claude Code behavior. Do not describe a
  Codex skill as a native slash command unless the user is explicitly asking
  for a conceptual analogy.
- Redact tokens, API keys, bearer headers, cookies, passwords, and long random
  secrets in excerpts.

## Recommendation rules

Classify each recommendation as one of:

- `new-skill`: a repeated multi-step workflow is not covered by an existing
  skill and would benefit from reusable instructions or scripts.
- `skill-optimization`: an existing skill triggered or should have triggered,
  but repeated corrections show it needs clearer instructions, evals, or helper
  scripts.
- `automation`: the workflow is scheduled, repetitive, and has stable inputs or
  check criteria.
- `repo-doc`: the issue is local project knowledge that belongs in README,
  AGENTS.md, CLAUDE.md, or equivalent repo instructions.
- `no-op`: the pattern is one-off, already covered, or not worth encoding.

Be conservative about new skills. Recommend one only when the evidence shows a
recurring workflow with stable trigger conditions and reusable execution steps.

## When the user wants implementation

If the user asks to create or update a skill based on the report:

1. Use `skill-creator` or `conversation-to-skill` when available.
2. Preserve the evidence trail from this report in the new skill's eval prompts
   or README notes where appropriate.
3. Keep report artifacts out of commits unless the user asks to save them.

## Output template

Use this shape unless the user asks otherwise:

```markdown
# Codex Insights

Data window: <dates or latest N>
Sources: <paths>
Analyzed: <raw sessions> sessions, <root workflows if known> root workflows

## Current Fact
...

## Usage Patterns
...

## Friction Points
...

## Workflow Opportunities
...

## Evidence
...

Artifacts:
- <report path>
- <json path>
```

