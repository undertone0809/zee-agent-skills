# Query Strategy

This file explains how `flomo-analysis-studio` should use `flomo-local-api` without turning the analysis into a memo dump.

## Core rule

Start broad, form a hypothesis, then gather just enough evidence to either support or weaken that hypothesis.

The job is not "read everything." The job is "extract the few memo clusters that best explain the user's current pattern."

## Working model

Think in four layers:

1. summary layer: what themes dominate each time window
2. hypothesis layer: what pattern might explain those themes
3. evidence layer: which memos actually support or challenge that pattern
4. interpretation layer: what the pattern means for the user now

If you skip layer 2, the rest becomes random querying.

## Default sequence

### Step 1. Broad summary pass

Start with:

```bash
python3 "$SCRIPT" summarize --days 30
python3 "$SCRIPT" summarize --days 90
python3 "$SCRIPT" summarize --days 365
```

Use these to answer:

- what is loud right now
- what has stayed stable for a quarter
- what feels structural over a year

At this stage, capture only 2-4 candidate themes. More than that usually means the analysis is still too close to the raw notes.

### Step 2. Name the hypothesis before querying

Convert the summaries into one of these hypothesis types:

- repeated conflict: "the user keeps wanting two incompatible things"
- repeated pursuit: "the user keeps returning to the same topic with energy"
- repeated emotional hook: "the same trigger or self-judgment keeps grabbing attention"
- repeated avoidance: "the user keeps understanding something without changing behavior"
- repeated identity signal: "the same values or style show up across domains"

If you cannot name the hypothesis in one sentence, do not start targeted queries yet.

### Step 3. Targeted evidence pass

Use `query` for one of three jobs only:

- confirm a pattern
- challenge a pattern
- collect 3-6 sharp evidence memos

Examples:

```bash
python3 "$SCRIPT" query --keyword "焦虑" --days 90 --limit 8 --format markdown
python3 "$SCRIPT" query --keyword "产品" --days 180 --limit 8 --format markdown
python3 "$SCRIPT" query --tag "Proj/rudder" --days 365 --limit 10 --format markdown
```

Good targeted query strategy:

- 1 query for the main theme
- 1 query for the likely tension
- 1 query for a counter-signal or alternative explanation

Bad targeted query strategy:

- 8 keyword searches because the summary looked interesting
- many near-duplicate tags
- huge limits that produce note overload

### Step 4. Tag pass when structure matters

If the user's taxonomy itself reveals something, run `tags`.

Examples:

```bash
python3 "$SCRIPT" tags --roots-only --limit 20 --format markdown
python3 "$SCRIPT" tags --query "self" --limit 20 --format markdown
python3 "$SCRIPT" tags --query "Proj" --limit 20 --format markdown
```

Use this when asking:

- what domains dominate their attention
- whether they organize around projects, emotions, people, or ideas
- whether their tag system is coherent, fragmented, or overgrown

Do not treat tags as truth. Treat them as a second signal next to memo bodies.

## Lens-specific query recipes

### Overview

Default:

```bash
python3 "$SCRIPT" summarize --days 30
python3 "$SCRIPT" summarize --days 90
python3 "$SCRIPT" summarize --days 365
```

Then add 1-2 queries only if one theme needs proof.

Good targets:

- most repeated project or topic
- most obvious contradiction
- one cluster that feels newly active

### ACT lens

Look for emotional hooks, rumination loops, self-judgment, or "I know this but..." patterns.

Query directions:

- emotion keywords that recur in the summary
- the repeated decision or situation that keeps reappearing
- tags around self, emotion, work conflict, or relationships if those dominate

Goal of the evidence pass:

- identify the hook
- identify the fused belief
- find at least one note where the user still knows what matters

### Compounding flywheel

Look for topics the user revisits with energy over long windows.

Query directions:

- repeated project or craft keywords
- tags for project families, domains, or learning systems
- evidence that something keeps returning across 90 and 365 days

Goal of the evidence pass:

- separate obligation from intrinsic pull
- find overlap between interest, persistence, and usefulness

### Action guide

Look for notes that repeat the same unresolved tradeoff.

Query directions:

- repeated question wording
- repeated "should I" or "whether" style indecision
- the project or life area where analysis seems to be replacing movement

Goal of the evidence pass:

- show what needs action rather than more interpretation
- find the smallest live experiment that would reduce uncertainty

### Blind spots

This lens needs the highest evidence bar.

Query directions:

- a contradiction that appears across windows
- repeated insight with no changed behavior
- repeated justification or excuse language

Goal of the evidence pass:

- get evidence from multiple memos or time windows for each blind spot
- avoid building a blind spot on one spicy line

### MBTI-style reading

This lens depends less on topic and more on language pattern.

Query directions:

- summaries across 30, 90, 365 for dominant concerns
- tags that reveal how the user structures life and work
- targeted queries only when you need more examples of decision language

Goal of the evidence pass:

- observe attention style, decision style, and structure preference
- get enough samples to support one hypothesis and one alternative

## Time comparison logic

Use these defaults:

- 30 days for what is alive now
- 90 days for what has stabilised into a pattern
- 365 days for what looks structural

Interpretation rules:

- 30 + 90 but not 365: recent activation
- 30 + 90 + 365: structural pattern
- 365 but not 30: fading or deprioritised pattern
- 30 only: possible short-term weather, not yet identity

When the recent window sharply disagrees with the long window, that contrast is often more useful than the dominant topic list.

## Evidence standard

Strong claim:

- repeated memo evidence across time windows
- or a memo cluster plus tag structure pointing the same way

Medium claim:

- repeated evidence inside one window
- or multiple related memos around the same project or conflict

Weak claim:

- one or two memos
- vague wording with no pattern repetition

Always weaken the language when evidence is weak.

## Interpretation heuristics

Use these moves often:

- topic -> pressure: what demand or desire is this topic carrying?
- repetition -> importance: what keeps returning even when the user has many other things to write about?
- contradiction -> leverage: if this contradiction were resolved, what would change?
- language -> stance: is the user framing life as exploration, control, duty, identity, mastery, belonging, or escape?

## Common mistakes

- querying too early
- treating a summary theme as an insight
- quoting large memo chunks instead of extracting the pattern
- over-weighting the latest dramatic note
- ignoring counter-evidence that weakens the story
