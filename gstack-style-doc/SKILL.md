---
name: gstack-style-doc
description: Generate technical documentation in the style of garrytan/gstack - featuring hook-first narrative, reasoning transparency, specific metrics, and conversational tone. Use when user asks for "gstack style README", detailed technical docs with reasoning, or wants to write docs like gstack.
version: 1.0.0
---

# GStack Style Documentation Generator

Generate technical documentation inspired by [garrytan/gstack](https://github.com/garrytan/gstack) - a style that combines personal narrative, transparent reasoning, and strategic detail density.

## What Makes GStack Style Unique

### 1. Hook-First Narrative
Start with something that grabs attention:
- A provocative quote that frames the problem
- A personal story that establishes stakes
- A surprising statistic or observation

**Example from gstack:**
```markdown
> "Don't type code. Just don't."
> — Andrej Karpathy, $7.3B in AI infrastructure

I wanted to find out how.
```

### 2. Show Your Reasoning
Don't just describe what the tool does—show *how you thought about building it*:
- "You said X. The agent said Y."
- "This is not A. This is B."
- Contrast with alternatives to clarify positioning

**Example:**
```markdown
You said "daily briefing app." The agent said "you're building a chief of staff AI."

You said "refactor this function." The agent said "this is a 3-file change with tests."

[AUTO-FIXED] 2 issues. [ASK] Race condition → you approve fix.

Eight commands, end to end. That is not a copilot. That is a team.
```

### 3. Specific Numbers Signal Precision
Use exact metrics to build credibility:
- "600K+ lines, 10-20K/day"
- "~100ms per command"
- "35% tests, 20-45 forcing questions"

### 4. Progressive Disclosure Structure
```
Hook/Story → Quick Start (30s) → Core Workflows → Feature Table → Philosophy
```

### 5. Conversational Friction
Include moments of direct address:
- "Don't like it? Say 'stop suggesting'"
- "Fork it. Improve it. Make it yours."
- Self-aware asides about limitations

### 6. Role Personification
Present features as roles/responsibilities:
```markdown
| Command | Your Specialist | Description |
|---------|-----------------|-------------|
| /office-hours | YC Office Hours | Get strategic product advice |
| /ship | Staff Engineer | End-to-end implementation |
```

## Document Template

```markdown
# [Project Name]

> [Provocative quote that frames the problem]

[Personal story: what problem you faced, why it matters]

[Stats/credibility: "X hours saved", "Y production incidents prevented"]

## 30-Second Start

```bash
# Installation
npm install -g [tool]

# First command
[tool] init
```

## Core Workflow

### [Workflow Name: The Core Value Proposition]

You: `[initial command]`

[Tool]:
- [Specific output with metrics]
- [Detection/analysis result]
- [Decision point for user]

You: `[follow-up command]`

[Tool]: [Result with reasoning]

[Key insight/summary statement contrasting with alternatives]

## Feature Overview

| Command | Your [Role] | What They Do |
|---------|-------------|--------------|
| /cmd1 | [Title] | [One-line description] |
| /cmd2 | [Title] | [One-line description] |

## Why This Approach

[Reasoning section: why you chose this design over alternatives]
[Trade-offs acknowledged openly]

## Deeper Reading

- [Link to detailed docs]
- [Link to philosophy/approach doc]
```

## Usage Examples

### Example 1: CLI Tool

**User request:** "Write a gstack-style README for a database migration tool"

**Output approach:**
```markdown
# dbmate-pro

> "Database migrations are the #1 cause of production incidents."
> — SRE, Fortune 500 company

Last year, we had 3 production migration failures. The last one took 4 hours
to roll back and cost us $50K in downtime. The problem wasn't our migration
tool—it was the *decision process* before running migrations.

dbmate-pro doesn't just run migrations. It lets you *see* the consequences
before you press enter.

## 30-Second Start

```bash
npm install -g dbmate-pro
dbp init        # Scans your DB, builds change profile
dbp status      # Green = safe, red = needs review
```

## Core Workflow: The Pre-Flight Check

You: `dbp plan --to=production`

dbp:
- Detected: 3 tables will be modified
- Estimated lock time: 4.2s (based on 2.3M rows)
- [WARNING] Column type change: varchar(255) → text requires table rewrite
- [BLOCKED] No rollback script detected

You: `dbp generate-rollback`

dbp: Generated 3 rollback scripts, syntax-checked ✓

You: `dbp approve`

dbp: Migration logged, awaiting execution window

Eight commands, end to end. This isn't a CLI tool. It's a database change
review system.

## Your Migration Team

| Command | Your Specialist | Description |
|---------|-----------------|-------------|
| plan | Site Reliability Engineer | Estimates impact, detects risks |
| approve | Tech Lead | Enforces review requirements |
| execute | DBA | Runs with monitoring & rollback ready |
```

### Example 2: Library/Package

**User request:** "Write gstack-style docs for a React form library"

**Output approach:**
```markdown
# form-surge

> "Form validation is easy. Form UX is hard."

We built 47 forms last year. Each one had slightly different validation logic,
error messages, and async submission handling. Our users complained about
the inconsistency. Our developers complained about the boilerplate.

form-surge doesn't give you validation functions. It gives you *form behavior
patterns* that your team can reuse.

## 30-Second Start

```bash
npm install form-surge
```

```tsx
import { useForm } from 'form-surge'

function CheckoutForm() {
  const form = useForm({
    schema: checkoutSchema,
    mode: 'optimistic-with-rollback'
  })
  // Form behavior, not just validation
}
```

## Core Pattern: Optimistic with Rollback

You said: "Submit button should show loading state."

form-surge said: "You're building a distributed transaction with UI feedback."

```tsx
const form = useForm({
  schema: checkoutSchema,
  mode: 'optimistic-with-rollback',
  onSubmit: async (data) => {
    // UI updates immediately (optimistic)
    // If failed, auto-rollback with toast notification
    // Success: confirm and clear
  }
})
```

Result: 12 lines vs 67 lines in our old approach. 100% consistent UX.

## Behavior Patterns

| Pattern | Your Use Case | What You Get |
|---------|---------------|--------------|
| `optimistic-with-rollback` | E-commerce checkout | Immediate feedback, auto-recovery |
| `draft-save` | Long forms | Auto-save to localStorage |
| `field-level-validation` | Real-time search | Debounced validation, no jank |
```

## When to Use This Style

**Good fits:**
- Developer tools and CLI utilities
- Libraries with strong opinions
- Products with distinct workflows
- Documentation where you want to teach *approach*, not just API

**Not ideal for:**
- Simple utility libraries (overkill)
- Enterprise documentation requiring formal tone
- API reference docs (use this for guides/tutorials instead)

## Anti-Patterns to Avoid

1. **Don't fake the personal story** - If you don't have one, use a hypothetical user story instead
2. **Don't force metrics** - If you don't have real numbers, describe the impact qualitatively
3. **Don't over-narrate** - The "conversation" format works for 2-3 turns, then switch to direct documentation
4. **Don't forget the practical** - Hook draws them in, but clear usage examples keep them

## Tips for Maximum Impact

1. **Start with the strongest hook** - The quote or observation that made you build this
2. **Show the "aha" moment** - The workflow example should demonstrate your unique insight
3. **Use contrast strategically** - "Not X, but Y" is powerful when accurate
4. **End with philosophy** - Give readers something to think about after the how-to
5. **Link to depth** - The README is the hook; detailed docs are where depth lives
