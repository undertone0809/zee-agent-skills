---
name: conversation-to-skill
description: Create a new Agent Skill from the current conversation, observed workflow, user corrections, examples, files, and requirements. Use this when the user asks to turn a conversation, repeated workflow, SOP, prompt pattern, successful run, or team process into a reusable skill package. Do not use this to optimize an existing skill; use a skill optimizer for patches to existing skills.
---

# Conversation to Skill

## Mission

Turn a useful conversation into a reusable Agent Skill.

This skill extracts durable procedure from the current conversation, separates reusable workflow from one-off context, and produces a new skill package that another agent can discover, load, and use later.

The output should be practical: a `SKILL.md`, optional reference files, optional scripts/templates, realistic examples, and evaluation cases. Prefer a small, focused skill over a large prompt dump.

## What this skill creates

Create a new skill when the conversation contains a process that should be repeated later. The process may come from a successful task, a partially corrected run, a user-described SOP, or a reusable prompt pattern.

A good generated skill includes:

- clear YAML frontmatter with `name` and `description`
- a concise mission and scope
- specific trigger language in the description
- required inputs and assumptions
- a step-by-step workflow
- decision rules and failure handling
- output format or template
- safety, privacy, and approval boundaries
- examples and evaluation cases
- optional references, templates, fixtures, or scripts when they save future effort

## Boundaries

Use this skill for creating a first version of a new skill.

Do not use this skill when the user primarily wants to improve an existing skill. In that case, hand off to a skill optimizer or produce a patch workflow instead of creating a new skill from scratch.

Do not copy the conversation verbatim into the generated skill. Convert the conversation into general instructions. Remove secrets, credentials, private identifiers, one-time file paths, temporary deadlines, and other ephemeral details unless the user explicitly wants a private/team-specific skill and the information is safe to store.

## Core workflow

### 1. Establish the creation target

Identify the likely new skill from the conversation.

Capture:

- target skill name
- user intent
- domain and operating context
- expected users
- repeated task or workflow
- current conversation evidence
- available files or artifacts
- missing information

If the target is ambiguous, infer the most likely skill and state the assumption. Ask a clarifying question only when choosing the wrong target would substantially change the skill.

### 2. Build an evidence ledger

Extract evidence from the conversation before writing the skill.

Use this structure:

```md
## Evidence ledger

| Evidence from conversation | Durable meaning | Skill instruction implied |
|---|---|---|
| ... | ... | ... |
```

Look for:

- user goals and success criteria
- tools used
- step order
- decisions and thresholds
- user corrections
- preferred output format
- examples of good and bad results
- repeated phrases that should trigger the skill
- failure modes or risk points
- approval requirements
- external systems, files, or templates

### 3. Separate reusable rules from one-off context

Classify each extracted detail:

- **Reusable workflow rule**: encode in the new skill.
- **User/team preference**: encode only if the skill is intended for that user/team.
- **Domain requirement**: encode when required for safety, compliance, or correctness.
- **One-off instruction**: do not encode as a default; mention only as an example if useful.
- **Sensitive detail**: redact or generalize.
- **Open question**: list as an assumption or TODO.

The generated skill should preserve the process, not the accidentals of the single conversation.

### 4. Choose the skill architecture

Keep the skill focused.

Use a single `SKILL.md` when the workflow is short. Add reference files when the skill needs supporting material, such as a rubric, style guide, checklist, schema, examples, or domain adapter. Add scripts only when deterministic code will reduce repeated work, such as parsing files, validating outputs, packaging artifacts, or checking schemas.

Recommended package structure:

```text
skill-name/
├── SKILL.md
├── references/
│   ├── checklist.md
│   ├── output-template.md
│   └── rubric.md
├── scripts/
│   └── helper.py
└── examples/
    └── example-input.md
```

Avoid deep reference chains. Files referenced by the skill should be one level away from `SKILL.md` whenever possible.

### 5. Write discovery metadata

The `description` is the main trigger surface. It must say both what the skill does and when to use it.

Include natural language triggers, near-synonyms, and contexts where the user may not explicitly say “skill.” Also include boundaries that prevent obvious misfires.

Good description pattern:

```yaml
description: Use this skill to [task]. Use when the user asks to [trigger phrase], [near synonym], or [context]. Do not use when [near-miss boundary].
```

### 6. Draft the SKILL.md

Use imperative instructions. Be concise but complete.

A generated `SKILL.md` should usually contain:

```md
---
name: skill-name
description: ...
---

# Skill Name

## Mission

## When to use this skill

## Inputs

## Workflow

## Decision rules

## Output format

## Safety and privacy

## Failure handling

## Validation cases
```

Add or remove sections based on the actual workflow. Do not include empty boilerplate sections.

### 7. Add examples and evals

Create realistic test prompts for the new skill.

Include:

- should-trigger prompts
- should-not-trigger prompts
- at least three task eval cases when the skill has verifiable behavior
- one edge case or failure case
- expected behavior and “must not” behavior

For subjective skills, use a rubric instead of brittle exact assertions.

### 8. Apply domain adapters only when needed

If the conversation implies a specialized or regulated domain, add a compact domain adapter. Keep the core workflow general and put domain-specific constraints in a reference file.

Useful adapters include:

- software and AI workflows
- healthcare operations
- legal and compliance
- finance and accounting
- research and knowledge work
- education and training
- customer support and sales
- HR and people operations
- operations and supply chain
- creative, brand, and content
- document and data processing

Read `references/domain-adapter-patterns.md` when the skill’s domain has safety, quality, or source-of-truth requirements that should not be guessed from the current conversation alone.

### 9. Redact and generalize

Before finalizing, remove:

- API keys, tokens, passwords, credentials
- private personal data unless essential and safe
- non-public customer, patient, employee, or financial identifiers
- temporary file paths and local machine details
- one-time calendar dates or project names that should not become defaults
- instructions to bypass safety, review, or policy controls

Replace sensitive details with placeholders or generalized language.

### 10. Final response format

When the environment supports file creation, provide the generated skill package. Otherwise, provide the skill content and a file tree.

Use this response structure:

```md
## Conversation-to-skill result

Target skill:
Scope:
Main reusable workflow:
One-off details excluded:
Assumptions:

## Files created or proposed

...

## SKILL.md

...

## Eval cases

...

## Trigger tests

Should trigger:
...

Should not trigger:
...
```

If the user asked for a complete package, include a downloadable zip when possible.

## Quality checklist

Before finishing, verify:

- The skill is not just a transcript summary.
- The description contains strong trigger phrases.
- The skill has a clear workflow and output format.
- Reusable rules are separated from one-off details.
- Sensitive information is removed or generalized.
- Safety and approval boundaries are explicit.
- The skill is focused enough to be loaded only when useful.
- Eval cases test both normal behavior and edge cases.
- Should-not-trigger examples include realistic near misses.
- Optional reference files are directly referenced from `SKILL.md`.
