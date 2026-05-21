# migrate-pro

> "Database migrations are the #1 cause of production incidents in growing teams."
> — SRE Lead, $2B fintech company

Last quarter, we had 4 migration failures. The worst one locked our users table for 23 minutes during peak traffic. Rollback took 6 hours because we hadn't tested it. The problem wasn't our SQL—it was that we couldn't *see* the consequences before we ran the migration.

migrate-pro doesn't just run migrations. It gives you a pre-flight checklist with real numbers: lock times, row counts, rollback paths. You make the decision with eyes open.

## 30-Second Start

```bash
# Installation
npm install -g migrate-pro

# Connect to your database
mp init --database=postgresql://localhost/myapp

# Analyze pending migrations
mp plan --target=production
```

## Core Workflow: The Pre-Flight Check

You: `mp plan --migration=add_user_preferences`

mp:
- Detected: 1 table modification, 2 index creations
- Estimated execution time: 47s (based on 1.2M rows)
- [WARNING] `ALTER TABLE` requires `ACCESS EXCLUSIVE` lock for 12s
- [RISK] Adding non-nullable column without default value
- [BLOCKED] No rollback script detected for this migration

You: `mp generate-rollback --migration=add_user_preferences`

mp:
- Generated rollback script: `rollback_0034_add_user_preferences.sql`
- Syntax validated ✓
- Tested on snapshot: `test_db_2024_01_15` ✓
- Estimated rollback time: 8s

You: `mp approve --migration=add_user_preferences --reviewer=@sarah`

mp: Migration approved by @sarah. Queued for execution window: `2024-01-16 02:00 UTC`

Seven commands, end to end. This isn't a migration runner. It's a database change review system.

## Your Migration Team

| Command | Your Specialist | What They Do |
|---------|-----------------|--------------|
| `plan` | Site Reliability Engineer | Analyzes impact, estimates lock times, flags risks |
| `generate-rollback` | DBA | Creates tested rollback scripts automatically |
| `approve` | Tech Lead | Enforces review requirements, tracks sign-offs |
| `execute` | Production Engineer | Runs with monitoring, auto-rollback on failure |
| `status` | Observability Lead | Shows pending, running, and failed migrations |
| `history` | Auditor | Complete audit trail with timing and approvers |

## Risk Analysis: What We Detect

migrate-pro analyzes your SQL before it runs:

| Risk Level | Detection | Example |
|------------|-----------|---------|
| **BLOCKED** | Untested rollback | No rollback script found for destructive change |
| **HIGH** | Long table locks | `ALTER TABLE` on >1M rows without `CONCURRENTLY` |
| **MEDIUM** | Schema conflicts | Column name collision with existing index |
| **LOW** | Performance impact | Missing index on foreign key column |

You configure the rules. Your team decides what blocks a deployment.

## Why This Approach

You said: "We need a better migration tool."

migrate-pro said: "You're building a safety system for database changes."

Existing tools focus on *running* migrations. We focus on the *decision* to run them:

- **Not just execution time** — lock duration and concurrency impact
- **Not just up migrations** — rollback tested and ready before you start
- **Not just logs** — audit trail with reviewer attribution

Trade-off: migrate-pro adds 2-5 minutes to your deployment process. It prevents 2-4 hour outages. That's the bet.

## Configuration

```yaml
# migrate-pro.yml
risk_threshold: MEDIUM
require_rollback: true
require_approval_for:
  - lock_time > 10s
  - rows_affected > 100000

execution:
  dry_run_first: true
  auto_rollback_on_error: true
  notify_on_complete:
    - slack:#db-migrations
    - pagerduty:oncall
```

## Deeper Reading

- [Risk Detection Rules](docs/risk-rules.md)
- [Rollback Strategies](docs/rollback-patterns.md)
- [CI/CD Integration](docs/ci-cd.md)
- [Philosophy: Why Pre-Flight Beats Post-Mortem](docs/philosophy.md)

---

Fork it. Add your own risk detectors. Make it fit your team's safety culture.
