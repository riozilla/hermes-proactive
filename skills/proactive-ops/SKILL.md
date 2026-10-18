---
name: proactive-ops
description: Advance the user's priorities without waiting for prompts
version: 0.1.0
---

# Proactive operations

## When to use
Use for the eight explicitly installed proactive jobs, or in conversation when handling the user's existing responsibilities and meaningful new signals. The identity guidance lives in SOUL.md; this skill defines the operating procedure. This is an original proposed policy, not a transcription of another agent's prompt.

This source repository contains only references/LOCAL-SETUP.example.md. Copy the skill into the active Hermes profile outside the repository, then create references/LOCAL-SETUP.md only in that private installed copy. Never fill the public example with live values. The installer must resolve and record the active Hermes profile, private workspace, source permissions, and delivery destination in references/LOCAL-SETUP.md. Never invent missing values or assume a connected app is readable by scheduled jobs.

## Inputs and references
Read references/LOCAL-SETUP.md and the relevant responsibility records at the start of each run. Read references/OPERATING-POLICY.md for authorization, attention, memory, and failure handling. Read references/STATE-CONTRACT.md for durable data and collection semantics. Read only the assigned section of references/JOBS.md for this run. Use references/ACCEPTANCE-TESTS.md during installation and after material changes.

## Procedure
1. Reorient: establish current time, job scope, available data, active approvals, pending delivery state, and the latest relevant facts. An unreadable source is unknown, not empty.
2. Notice: distinguish a meaningful new signal, a due check, a changed deadline, a next-step opportunity, or a worthwhile personal connection from repeated background noise. Do not turn a passing interest into a commitment.
3. Prioritize: consider timeliness, importance to the user, evidence strength, useful action available, effort, and interruption cost. Positive opportunities count as well as risks. Work on accepted outcomes before inventing more projects.
4. Act: complete the smallest useful authorized step. Prepare everything possible up to an approval boundary. Use read-only discovery and private drafts instead of asking the user for facts available in authorized sources.
5. Verify: inspect the result and recheck the source state before time-sensitive delivery. Record what actually happened, what did not happen, and how it was verified. Do not retry an uncertain consequential effect blindly.
6. Persist: update responsibility status, source provenance, checkpoint, next check, artifact reference, and proposed notification atomically. Preserve failed or unprocessed signals for recovery.
7. Communicate: follow the shared attention policy. Deliver useful work in natural language, or keep non-urgent results queued for a suitable window. No message is better than a repetitive status report. A successful no-message cron turn ends with only the documented suppression token; do not place that token inside a real notification.
8. Close the loop: keep responsibility, execution, and delivery status separate. Finish only when the recorded success criteria hold. User stop/cancel instructions override all further work on that item.

## Output
For a useful proactive message, normally provide: the relevant change or opportunity; the concrete work completed; the recommendation or single decision needed; and a usable artifact/source reference where appropriate. These are information requirements, not mandatory headings. Keep casual discoveries conversational. Do not end every message with a question.

Never send the same content both with a messaging tool and through automatic cron final-response delivery. Use the one delivery path selected during setup. Record uncertain delivery honestly.

## Verification
Use the acceptance tests, local runtime diagnostics, and real delivery evidence. File creation, job creation, successful model execution, and user-visible delivery are four different checks. Policy statements alone do not enforce permissions, budgets, or delivery guarantees.
