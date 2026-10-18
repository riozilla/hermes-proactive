# Public repository privacy model

## What belongs here

Generic instructions, original implementation specifications, synthetic examples, public references, and development tools. No user profile, private conversation, employer, location, account identifiers, device inventory, actual schedule, booking, private project, or live configuration is required.

## What stays outside

Completed LOCAL-SETUP.md, personalized identity, environment files, credentials, session cookies, OAuth material, connector exports, original source messages, screenshots, runtime databases, logs, artifacts, backups, and incident reports. The .gitignore is defense in depth, not a guarantee: force-added or already tracked files are still publishable.

Use a separate private installed profile and workspace. Do not run the personalized system out of this public checkout. The repository's default policy and proposed schedule values are design examples, not a user profile.

## Checks included

`scripts/check_public_content.py` checks public file paths, common credential formats, credential-like assignments, non-example email addresses, private IPv4 literals, personalized home paths, and optional locally supplied forbidden terms. It reports rule IDs, not matched values. `--history` inspects reachable Git blobs and commit/tag content; it does not make an unsafe existing remote safe.

An optional `PUBLIC_REPO_DENYLIST_FILE` may point to a UTF-8 file **outside the repository**, with one literal personal term per line. It is read locally and never copied into the release, logged, or committed. Do not put real personal terms in tests, CI variables, issues, or public suppression lists. Matches use word boundaries for word-like terms to avoid accidental substrings.

The release builder uses an explicit source allowlist, rejects symlinks and unexpected source files, validates the repository, and omits Git metadata. The publication helper creates a new temporary repository from that reviewed source snapshot with generic author/committer identity. It never pushes the checkout's existing history or reads Hermes credentials.

## Limits

Pattern matching cannot recognize every secret or personal fact. A passing scan is not proof that arbitrary future changes are safe. Review file names, prose, examples, URLs, commit messages, images, metadata, issue text, release notes, and account attribution. GitHub ownership/activity remains publicly associated with the publishing account; generic commit identity does not anonymize the account.

A CI scan runs after content reaches GitHub. It helps flag later regressions but cannot prevent an initial disclosure. Run local checks before committing or pushing, and keep GitHub secret scanning/push protection enabled where available.

## After an exposure

Revoke or rotate exposed credentials first through the issuer. Stop further publication. Review all branches, tags, artifacts, Actions logs, issues, and releases; deleting a file in a new commit does not remove old versions. Use the host's supported incident and history-remediation process. Copies and forks may remain. Do not paste the secret into a bug report or this repository's scanner configuration.
