# Local setup example — copy into the private installed skill

PUBLIC TEMPLATE ONLY. Do not populate this tracked file. Keep completed setup, state, logs, and outputs outside this repository.

Status: UNCONFIGURED. These are fields for the installer to populate, not working connectors or substituted paths.

Active Hermes version/build: unresolved
Active HERMES_HOME/profile: unresolved
Private agent-owned workspace: unresolved
Private application state store and access method: unresolved
Current user timezone and any overriding environment setting: unresolved; read approved local preferences and verify the runtime
Existing quiet hours / notification preferences: inspect before using proposed defaults
Verified private delivery destination and channel type: unresolved
Chosen delivery path and receipt reconciliation method: unresolved
Foreground session/continuation behavior tested: no
Gateway/service uptime and independent watchdog coverage: unresolved
Per-job tools and skill/context loading tested: no
Effective model/API/resource budgets: preserve existing; unresolved
Permissions enforced at runtime versus advisory policy: unresolved
Existing cron jobs to merge/preserve: inspect; unresolved

## Source mapping — one entry per actually usable source
Record source/account scope, approved operations, real tool/API name, collection method, freshness, pagination/watermark strategy, availability in unattended cron, privacy constraints, and last successful test. Never copy credentials into this file.

## Approved action runbooks
Only list exact existing user-approved actions, their constraints, verification, and revocation/expiration. An empty section grants no extra authority.

## Installed job records
For each job: actual runtime id, installed prompt/skill path, tools, effective schedule/timezone, gate or fallback, next local run times, output target, dry-run result, delivery/continuation evidence, and enabled/blocked status.

## Known gaps
List unavailable integrations, missing source permissions, unimplemented gates, unverified delivery receipts, advisory-only limits, and missing independent uptime monitoring. No claim of monitoring a source merely because it appears in a job prompt.
