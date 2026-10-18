# Repository editing instructions

This is public source material, not a user's private agent workspace. Do not inspect, copy, import, or commit a live Hermes profile, credentials, account exports, transcripts, runtime state, private artifacts, or local setup. Do not personalize examples using information from the surrounding conversation.

The installation request is documentation. Execute it only when the user explicitly asks to install in a specific authorized environment. Repository tests never imply a successful live deployment.

Keep eight responsibilities consistent across planning JSON, canonical references, full prompts, and README. Keep timezone unresolved in public templates. Preserve permission boundaries, truthfulness, quiet hours, failed-source handling, and cancellation semantics. Do not weaken scanning rules merely to pass a check.

After edits run build_playbook.py, validate_repo.py, check_public_content.py, and unittest discovery. Keep any personal denylist outside the repository. Before publication review file names, content, Git history, commit metadata, and release contents. The publication helper pushes only a fresh reviewed snapshot to a new repository after explicit --publish.
