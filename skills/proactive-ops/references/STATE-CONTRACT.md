# State contract — custom implementation specification

This is a proposed application data model, NOT a Hermes built-in schema or native job-import format. Reuse an existing suitable private task store rather than creating a conflicting second source of truth. Otherwise implement a small transaction-safe SQLite database under the agent-owned workspace. Do not query or patch Hermes's internal state database directly for these records.

## Minimum records
**Responsibility:** stable id; explicit/confirmed/candidate classification; domain; desired outcome; acceptance criterion; source reference and source timestamp; owner; status; priority rationale; due_at with original timezone; next_action; next_check_at; required_authorization reference; last_verified_at; checkpoint; artifact references; completion evidence; created_at/updated_at; cancelled_at where applicable.

**Signal:** stable source id and event/version id or content fingerprint; event time; observed_at; affected responsibility ids; minimal relevant payload/reference; status pending/claimed/processed/failed; lease owner and expiry; retry time; processing result. A source collection cursor and signal processing cursor are different things.

**Delivery:** idempotency key; responsibility and source version; reason; proposed content/artifact reference; urgency; eligible_after; status proposed/reserved/attempted/delivered/unverified/failed/suppressed; target; runtime run reference; acknowledgement/message reference; timestamps. User-read status stays unknown unless the platform supplies it.

**Source health:** source id; approved scope; connector/tool route; last successful freshness watermark; degraded_since; failure signature; next_retry; incident id; notification history. Missing data is not a healthy empty response.

**Attention:** private destination; timezone/quiet hours; per-local-day unsolicited reservations/deliveries; most recent unsolicited delivery; per-topic suppression; explicit reminders; pause scopes. Count shared slots atomically across jobs; release a slot only when delivery failure is certain, not merely unknown.

**Preferences:** durable confirmed references and bounded candidate observations. Use Hermes's existing memory mechanism for stable facts; this record need not duplicate it.

## Collection and cheap gates
High-frequency gates are useful only after real source collectors work. A timestamped feed file does not collect email or calendar changes by itself. Either configure source-specific authenticated events, or poll approved APIs with pagination and appropriate freshness checks. Record exactly which collectors exist and their costs in LOCAL-SETUP.md.

Use stable event/version ids or content fingerprints; counts alone miss edited meetings and replaced content. Persist collected signals and the collection cursor together. Do not discard a signal or advance its processed marker until the agent has durably committed its outcome. Use expiring claims so interrupted runs can recover; never hold a database transaction open during a model call.

A gate must also wake for a due next_check_at, an undelivered eligible result, a relevant time window crossed (even with unchanged source content), or a new/changed coverage failure. Unchanged sources alone are not a sufficient reason to skip a time-sensitive task. Tests must cover these cases.

A clean no-work gate can emit the documented Hermes skip result. A collector failure must not emit a false no-work verdict. Persist the incident and route recovery/escalation appropriately. No secrets in stdout, logs, or model context.

If a functioning cheap gate cannot be implemented with already approved capabilities, install the published lower-frequency fallback and clearly disclose its detection latency. Do not claim an event-driven monitor or a no-model-cost poll exists merely because a prompt describes it.

## Execution, delivery, and concurrency
Use atomic responsibility claims so radar and project workers cannot start the same step. Use a unique delivery key across jobs. Before sending time-sensitive content, verify the relevant source and cancellation state again. Let one defined delivery path transmit the result; do not combine automatic cron delivery and a manual messaging call for the same content.

Reconcile delivery using supported runtime history/adapter evidence. No direct edits to Hermes internal tables. Distinguish prepared, attempted, delivered, and read. If the platform cannot support stronger guarantees, disclose the limitation rather than promising exactly-once delivery.

After a restart, inspect stale claims and execution state. Private/idempotent work may be retried after reconciliation. Effects with ambiguous external outcomes must be checked before another attempt. Process cancelled and changed commitments before generating reminders.

## Retention
Keep only evidence needed to operate the accepted responsibilities, with links rather than copied source bodies where possible. Follow the user's existing retention policy. Stage cleanup of obsolete agent-owned records for the approved retention process; never erase source messages, original documents, or audit evidence to make the system appear tidy.
