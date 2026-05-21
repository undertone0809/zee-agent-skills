# Safety and Redaction Guide

When converting a conversation into a skill, the risk is not only doing the wrong task. The risk is making temporary or sensitive details durable.

## Remove or generalize

- credentials, tokens, API keys, private URLs
- private customer, patient, employee, student, or financial identifiers
- file paths tied to one local machine
- one-time dates, launch names, embargo details, and temporary exceptions
- organization-specific secrets or internal policies unless the package is private and approved
- instructions that bypass review, approval, compliance, or safety controls

## Preserve as generalized rules

- approval gates
- source-of-truth requirements
- review owners
- privacy constraints
- data retention and minimization
- escalation paths
- rollback or recovery behavior

## Placeholders

Use placeholders such as:

- `<CUSTOMER_NAME>`
- `<REPOSITORY>`
- `<POLICY_SOURCE>`
- `<APPROVER>`
- `<OUTPUT_CHANNEL>`
- `<DATA_SOURCE>`
