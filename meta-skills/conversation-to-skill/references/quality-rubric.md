# Conversation-to-Skill Quality Rubric

Score a generated skill across these dimensions.

## 1. Conversation evidence extraction

High quality: identifies goals, corrections, tools, steps, examples, outputs, and risk points from the conversation.

Low quality: summarizes the conversation without turning it into procedural knowledge.

## 2. Generalization

High quality: separates reusable workflow from one-off details and sensitive data.

Low quality: bakes in temporary details, names, dates, file paths, or customer-specific facts.

## 3. Discoverability

High quality: frontmatter description contains what the skill does, when to use it, near-synonym triggers, and boundaries.

Low quality: description is vague, keyword-only, or fails to mention likely user phrasings.

## 4. Workflow clarity

High quality: provides clear step order, decision rules, input requirements, and output format.

Low quality: gives high-level advice but no repeatable procedure.

## 5. Safety and privacy

High quality: redacts sensitive data and preserves approval, compliance, review, or source-of-truth boundaries.

Low quality: stores secrets, weakens approval gates, or omits regulated-domain constraints.

## 6. Evaluation readiness

High quality: includes realistic positive tests, negative trigger tests, edge cases, expected behavior, and must-not conditions.

Low quality: has no evals or only generic examples.

## 7. Package maintainability

High quality: uses a compact SKILL.md, direct references, optional scripts/templates when they save future work, and avoids deep reference chains.

Low quality: creates a giant prompt dump or scattered files with unclear loading paths.
