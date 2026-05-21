# Eval Guide

Conversation-to-skill evals should test whether the generated skill works as a reusable artifact, not whether it merely resembles the source conversation.

## Required eval types

### 1. Creation-quality eval

Given a source conversation, check whether the generated skill includes:

- specific name and description
- durable workflow
- inputs and outputs
- decision rules
- safety/privacy boundaries
- validation cases

### 2. Trigger eval

Create should-trigger and should-not-trigger prompts.

Good should-trigger prompts include:

- direct requests: "turn this workflow into a skill"
- indirect requests: "make this reusable"
- domain-specific phrasings
- prompts that omit the word "skill" but clearly ask for a reusable agent workflow

Good should-not-trigger prompts include near misses:

- summarize the conversation
- continue the task once
- optimize an existing skill
- write a normal SOP for humans
- create a one-off prompt without reusable packaging

### 3. Downstream-use eval

After generating the skill, test whether another agent could use it on a fresh task. This can be checked manually or with deterministic assertions for structured outputs.

## Suggested scoring dimensions

- evidence extraction
- reusable-vs-one-off separation
- skill structure
- trigger description
- workflow clarity
- safety/privacy
- eval cases
- domain adapter use
- maintainability
