# Validation: source integrity versus a live deployment

## Repository checks

```bash
python3 scripts/validate_repo.py
python3 scripts/check_public_content.py
python3 -m unittest discover -s tests -v
python3 scripts/build_release.py
```

Once the source has Git history, optionally inspect reachable history too:

```bash
python3 scripts/check_public_content.py --history
```

Structural validation checks the eight planned jobs, five-field numeric schedules, required fallbacks, generic timezone, prompt-to-planning consistency, local documentation links, and the generated playbook. Public-content checks are a heuristic defense, not a formal security proof. Unit tests use synthetic data only.

The GitHub workflow repeats source checks and tests with read-only repository permissions. It does not receive personal denylist terms or run an agent against real accounts. It also does not test a Hermes runtime.

## Runtime acceptance

Follow the [18 acceptance scenarios](../skills/proactive-ops/references/ACCEPTANCE-TESTS.md) in the private deployment. They cover no-change, time-only triggers, useful preparation, deduplication, edits, late cancellation, interrupted processing, unknown sends, expired authorization, untrusted content, approval boundaries, shared quiet hours, revocation, delivery continuation, artifact access, foreground responsiveness, resource limits, and effective timezone.

Use synthetic data for dangerous or private cases. One benign private canary is authorized only when the user submits the installation request. A reply test remains pending until a real user response is observed. Record what was measured, not what the instructions say should happen.

## Seven-day quality review

Evaluate useful outcomes completed without another prompt, decision-ready preparations, welcomed discoveries, missed material signals, duplicate or stale notices, unsupported success claims, and foreground delays. Use explicit feedback before assumptions from silence. Report uninstrumented measures as unknown.

Success is more useful initiative with less user effort—not a larger number of notifications.
