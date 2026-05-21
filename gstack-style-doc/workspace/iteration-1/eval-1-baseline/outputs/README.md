# migrate-pro

A database migration tool that analyzes SQL migration risks, estimates execution time, and handles rollback strategies.

## Features

- **Risk Analysis**: Scans migrations for potentially dangerous operations like table drops, column deletions, or schema changes that could cause data loss
- **Execution Time Estimation**: Predicts how long migrations will take based on table size, index complexity, and operation type
- **Rollback Strategies**: Automatically generates rollback scripts and validates their safety before execution
- **Dry Run Mode**: Preview migration effects without making actual changes
- **Multi-Database Support**: Works with PostgreSQL, MySQL, and SQLite

## Installation

```bash
npm install -g migrate-pro
```

Or install locally in your project:

```bash
npm install --save-dev migrate-pro
```

## Quick Start

```bash
# Initialize migrate-pro in your project
migrate-pro init

# Add a new migration
migrate-pro create add_users_table

# Analyze migration risks before running
migrate-pro analyze

# Run pending migrations
migrate-pro up

# Rollback last migration
migrate-pro down
```

## Configuration

Create a `migrate-pro.config.js` file in your project root:

```javascript
module.exports = {
  database: {
    client: 'postgresql',
    connection: {
      host: 'localhost',
      port: 5432,
      database: 'myapp',
      user: 'postgres',
      password: process.env.DB_PASSWORD
    }
  },
  migrations: {
    directory: './migrations',
    tableName: 'migrations'
  },
  analysis: {
    // Warn if estimated execution time exceeds 30 seconds
    maxExecutionTimeWarning: 30000,
    // Block migrations that would affect more than 1 million rows
    maxRowsAffected: 1000000,
    // Require rollback scripts for destructive operations
    requireRollbackForDestructiveOps: true
  }
};
```

## Risk Analysis

migrate-pro analyzes each migration for potential risks:

| Risk Level | Description | Examples |
|------------|-------------|----------|
| **Critical** | Operations that will cause data loss | `DROP TABLE`, `DROP COLUMN`, destructive type changes |
| **High** | Operations that may cause downtime or performance issues | Adding indexes on large tables, altering column types |
| **Medium** | Operations requiring caution | Adding nullable columns, creating new tables |
| **Low** | Generally safe operations | Adding indexes on small tables, creating views |

Example risk report:

```bash
$ migrate-pro analyze

Migration: 20240115120000_add_user_preferences.sql
Risk Level: HIGH

Issues Found:
  1. Adding index on 'users' table (estimated rows: 5,000,000)
     - Estimated time: 45 seconds
     - Recommendation: Run during low-traffic period

  2. Altering 'email' column type from VARCHAR(100) to VARCHAR(255)
     - Risk: Table rewrite required
     - Estimated time: 120 seconds

Rollback script: Valid (generated automatically)
```

## Execution Time Estimation

migrate-pro estimates migration execution time based on:

- Table row counts from database statistics
- Operation complexity (index creation, column alterations, etc.)
- Database hardware specifications (when available)
- Historical execution times from previous runs

```bash
$ migrate-pro estimate

Migration Estimates:
  001_create_users.sql           ~ 0.5s    (safe to run anytime)
  002_add_indexes.sql            ~ 45s     (run during maintenance window)
  003_migrate_user_data.sql      ~ 3m 20s  (run during maintenance window)
  004_add_foreign_keys.sql       ~ 12s     (safe to run anytime)

Total estimated time: ~4m 17s
```

## Rollback Strategies

migrate-pro handles rollback generation and validation:

### Automatic Rollback Generation

For common operations, migrate-pro can generate rollback scripts automatically:

```sql
-- Forward migration
CREATE TABLE user_profiles (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  bio TEXT
);

-- Generated rollback
DROP TABLE IF EXISTS user_profiles;
```

### Custom Rollback Scripts

For complex migrations, provide your own rollback:

```sql
-- migrate:up
ALTER TABLE orders ADD COLUMN status VARCHAR(20) DEFAULT 'pending';
UPDATE orders SET status = 'completed' WHERE completed_at IS NOT NULL;

-- migrate:down
UPDATE orders SET completed_at = NOW() WHERE status = 'completed';
ALTER TABLE orders DROP COLUMN status;
```

### Rollback Validation

Before executing a migration, migrate-pro validates that:

1. A rollback script exists for destructive operations
2. The rollback script is syntactically valid
3. The rollback can restore data integrity (where possible)

## CLI Reference

```bash
migrate-pro [command] [options]

Commands:
  init                    Initialize migrate-pro in the current directory
  create <name>           Create a new migration file
  up [n]                  Run n pending migrations (default: all)
  down [n]                Rollback n migrations (default: 1)
  status                  Show migration status
  analyze                 Analyze migration risks
  estimate                Estimate execution times
  validate                Validate migration files
  history                 Show migration execution history

Options:
  -c, --config <path>     Path to config file
  -e, --env <name>        Environment to use (default: development)
  --dry-run               Preview changes without executing
  --force                 Skip confirmation prompts
  -v, --verbose           Verbose output
  -h, --help              Show help
```

## Best Practices

1. **Always analyze before running**: Use `migrate-pro analyze` to catch potential issues early
2. **Test rollbacks**: Periodically verify that rollback scripts work as expected
3. **Keep migrations small**: Large migrations increase risk and execution time
4. **Run heavy migrations during maintenance windows**: Use the estimation feature to identify these
5. **Version control your migrations**: Track both forward and rollback scripts in git

## Example Workflow

```bash
# 1. Create a new migration
migrate-pro create add_order_status

# 2. Edit the generated file with your SQL
# migrations/20240115120000_add_order_status.sql

# 3. Analyze for risks
migrate-pro analyze

# 4. Check execution time estimate
migrate-pro estimate

# 5. Run in dry-run mode first
migrate-pro up --dry-run

# 6. Execute the migration
migrate-pro up

# 7. Verify the change
migrate-pro status
```

## License

MIT
