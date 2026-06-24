# codex-insights

Analyze local Codex sessions and generate a Claude Code `/insights`-style usage
report for Codex.

## Skill

- [`codex-insights`](SKILL.md): build evidence-backed reports from local Codex
  history, including usage patterns, friction points, and workflow opportunities
  for new skills, skill optimization, automations, or repo docs.

## Install

```bash
npx skills add Undertone0809/zee-agent-skills/codex-insights
```

## Direct Analyzer

The skill includes a read-only helper script:

```bash
python3 scripts/codex_insights.py --limit 30 --out /tmp/codex-insights
```

It writes `report.md`, `summary.json`, and `sessions.json` under the output
directory.

