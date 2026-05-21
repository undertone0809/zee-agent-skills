# Evaluation Method

Skill Optimizer should be evaluated at three levels:

1. Trigger eval: should the optimizer skill activate for realistic optimization requests and avoid unrelated tasks?
2. Patch-quality eval: does it produce an evidence-based, safe, reviewable, useful improvement to a target skill?
3. Downstream-task eval: after the target skill is patched, does the target skill perform better on its own tasks?

For project-based or maintainer skills, add a fourth practical layer:

4. Behavior-habit eval: does the optimized skill make the next run handle the same class of uncertainty, risk, or user correction better, even when the original bug can no longer be reproduced?

A SkillsBench-style local eval can compare:

- `without_skill`: a naive assistant improvement
- `previous_skill`: the last optimizer version
- `candidate_skill`: the optimized version

Each task should include a target skill, a transcript or failure observation, expected durable changes, and a deterministic verifier.

Do not treat synthetic verifier scores as official model pass rates. Use them to catch regressions and blind spots before running full agent-harness evals.

## Failure-class cases

Many useful skill improvements come from transient incidents:

- a repo state that changed after the fix
- a one-off outage or partially completed release
- a user correction about abstraction level
- a UI or data-path bug that is hard to recreate later
- a stale memory or stale config assumption

Do not force these into exact reproduction tests. Convert them into failure-class cases:

```md
### Case: <failure class>

Input:
The kind of user request or run evidence that should trigger the improved behavior.

Given:
The ambiguity, stale state, partial evidence, or tempting shortcut.

Expected behavior:
The source-of-truth order, decision point, patch, validation, or handoff evidence the skill should produce.

Must not:
The shortcut that caused the observed failure.

Score:
1 point each for trigger/routing, source-of-truth order, shortcut avoidance, task completion, and reviewable proof.
```

The goal is not to preserve the incident forever. The goal is to preserve the working habit that prevents the next similar incident.

## Old/new comparison

When optimizing a target skill, compare the previous and candidate skill on the same cases whenever feasible:

- `old_skill`: current target skill before the patch
- `new_skill`: candidate target skill after the patch
- `without_skill`: optional naive baseline when measuring the value of having a skill at all

Report these separately:

- Trigger accuracy: did the right skill activate?
- Patch-quality coverage: did Skill Optimizer generate the right change set?
- Behavior-habit score: did the target skill check the right evidence and avoid the known bad path?
- Live outcome signal: did real follow-up work need fewer user corrections, less rework, or stronger handoff evidence?

Keep human rubric scoring explicit when deterministic checks are too weak. Strategic and operational skills often need reviewer judgment; keyword checks should support that review, not replace it.
