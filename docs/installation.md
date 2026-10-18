# Installation guide

## Before installation

Read [INSTALL-PROMPT.md](../INSTALL-PROMPT.md), [SECURITY.md](../SECURITY.md), and the [operating policy](../skills/proactive-ops/references/OPERATING-POLICY.md). The pack is not an executable installer and its JSON is not a native import. It must be adapted to the installed Hermes version.

The target deployment needs a working Hermes installation, already authorized useful sources, a private destination, and an agent-owned writable workspace. Each responsibility may start with a supported subset of sources. Do not request new broad account access just to complete a checklist.

## Recommended agent-assisted path

Make the public files available locally or attach [PLAYBOOK.md](../PLAYBOOK.md). Review and send the installation prompt. It tells Hermes to inventory existing capabilities, back up affected configuration privately, merge overlapping jobs, implement only necessary local components, and report verified outcomes.

Reading a file is not approval to act. A browsing or code-review session should not execute the installation request unless the user explicitly submits it.

## Ordered rollout

1. **Inventory.** Establish version, active profile, identity loading, supported scheduling schema, existing jobs, sources, budgets, and delivery behavior. Keep this inventory private.
2. **Create private installed copies.** Install `skills/proactive-ops/` into the actual profile outside this public checkout. In that installed copy, copy `references/LOCAL-SETUP.example.md` to `references/LOCAL-SETUP.md` and populate it locally. Put all state, logs, outputs, and backups outside the repository.
3. **Merge identity and authority.** Merge SOUL additions without erasing unrelated instructions or weakening existing safeguards. Review shared notification defaults and locally resolve `{{USER_TIMEZONE}}`.
4. **Implement minimum state.** Reuse an appropriate existing store or implement the custom transaction-safe contract. Connect only authorized read-only collection. No database implementation is supplied by this pack.
5. **Validate a small surface first.** Test no-change, time-only triggers, duplicate signals, interrupted processing, permissions, and quiet hours with synthetic data. Test one private canary; mark reply continuation pending until a real user reply occurs.
6. **Register and enable.** Attach full prompts plus the operating skill. Create paused where supported; otherwise finish validation before registering an enabled job. Use fallback schedules where cheap gates are absent. Enable only tested coverage, record actual job IDs, and merge existing overlaps.
7. **Review after seven days.** Judge useful outcomes, missed material signals, duplicates, and foreground responsiveness—not how frequently the agent speaks.

## Configuration

[config.merge-fragment.yaml](../config.merge-fragment.yaml) contains a proposed merge fragment. Check supported keys and the effect of global settings on unrelated jobs. Prefer per-job continuation for the new responsibilities when possible. Preserve model/provider settings and budgets. A comment containing a timezone placeholder does not configure a timezone.

The public [planning file](../jobs.planning-spec.json) carries schedules, fallbacks, and prompt paths. Resolve all local values before translating it through the supported Hermes tools. Do not patch internal job JSON or databases.

## Required private completion report

Record actual modified paths and backups, job IDs, effective schedules and next local runs, enabled/blocked status, supported sources, test observations, available delivery evidence, and remaining gaps. Separate “configured,” “tested,” and “operational.” Do not publish this report or attach it to a public issue without creating and reviewing a synthetic reproduction.

## Rollback

Use supported job controls to pause only the installed job IDs. Prevent queued work from sending after cancellation and reconcile in-flight work separately. Restore the prior identity/configuration from private backups only after reviewing later edits; do not overwrite new user changes. Remove the installed skill only after dependent jobs are paused. Apply the user's retention policy to private state and artifacts; never delete original source records as part of rollback.

An unresolved interrupted action is not proof that nothing happened. Check the actual outcome before retrying or declaring a clean rollback.
