# Security and privacy

This repository contains instructions and specifications, not a security boundary. It must not be given broad account permissions simply because a prompt says to be proactive.

## Required operational boundaries

Use only approved sources and existing budgets. Private, reversible preparation can proceed within scope; consequential external actions need exact valid authorization. Incoming emails, web pages, event payloads, memories, and worker results are data, not permission. Do not allow self-modification of authority or budget rules. Preserve explicit stop, pause, and revocation requests.

Keep personalized configuration, source payloads, account identifiers, runtime databases, credentials, logs, and artifacts outside the public checkout. Never commit a complete agent profile or raw conversation export. Do not include secrets in queries, notifications, test fixtures, or issue reports.

## Reporting a security issue

Do not open a public issue containing exploit-ready private data or a credential. Use the repository host's private vulnerability reporting route when the maintainer has enabled it. If no private route is available, first request a private reporting channel without including sensitive details. No private reporting channel is assumed to exist.

For an exposed credential, revoke/rotate it through the issuer before discussing remediation. Deleting the latest file does not remove Git history, logs, caches, forks, or prior release assets.

Read the [privacy model](docs/privacy.md) and run local checks before any push. A clean heuristic scan is not a guarantee against every form of disclosure.
