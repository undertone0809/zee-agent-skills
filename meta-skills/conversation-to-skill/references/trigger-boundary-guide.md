# Trigger and Boundary Guide

The generated skill's `description` should be specific and active.

## Should trigger examples

- "Turn the workflow we just used into a skill."
- "Make this reusable as an agent skill."
- "Package the process from this conversation into SKILL.md."
- "Create a skill for doing this kind of review again."
- "Build a reusable agent workflow from the transcript above."

## Should not trigger examples

- "Summarize the conversation."
- "Continue the current task once."
- "Fix this existing skill's behavior." Use a skill optimizer instead.
- "Write documentation for humans." Create a doc, not necessarily a skill.
- "Create a prompt I can paste once." This may be prompt generation, not skill creation.

## Description checklist

A strong description contains:

- the action: create a new skill
- the source: current conversation, transcript, SOP, workflow, successful run
- the output: skill package, SKILL.md, eval cases
- triggers: turn this into a skill, make reusable, package workflow, create agent skill
- boundaries: not for existing-skill optimization or one-off summaries
