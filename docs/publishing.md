# Publish privately for review

The supplied helper creates a **new private repository only** in the authenticated user's account. It does not update an existing repository, push pre-existing history, change repository visibility, or run Hermes. It has no public-publication option. A later public release is a separate decision and action by the owner.

## Prerequisites

Install Git, Python 3.10+, and [GitHub CLI](https://cli.github.com/). Authenticate locally through GitHub CLI's normal browser-based flow. Never paste a token into this repository or a chat transcript. Connecting a read-only integration in another application does not authenticate your local CLI.

```bash
gh auth login --hostname github.com --git-protocol https --web --scopes workflow
gh auth setup-git --hostname github.com
python3 scripts/validate_repo.py
python3 scripts/check_public_content.py
python3 -m unittest discover -s tests -v
```

The additional `workflow` scope is for uploading the included GitHub Actions validation file; it is not a request to execute Hermes. See [GitHub OAuth scopes](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps).

## Preview, then create the private repository

```bash
python3 scripts/publish_github.py
python3 scripts/publish_github.py --publish --expected-owner YOUR_GITHUB_LOGIN
```

Replace `YOUR_GITHUB_LOGIN` with the account that should own the repository. The first command performs only local validation and makes no network calls. The explicit `--publish` command resolves the authenticated account and refuses an expected-owner mismatch. It prepares a fresh temporary Git repository containing only reviewed, allowlisted source, then checks its history.

The helper creates `hermes-proactive` with `gh repo create --private`, **without pushing files yet**. It reads the remote metadata and requires `private: true` before uploading. After the push it verifies private visibility again and checks that the remote main-branch commit matches the prepared snapshot. An existing repository is not overwritten, made public, force-pushed, or deleted.

To choose a different new repository name:

```bash
python3 scripts/publish_github.py --repo another-repository-name --publish --expected-owner YOUR_GITHUB_LOGIN
```

Generic contributor identity is used for commit metadata; the GitHub account remains the repository owner. The snapshot excludes prior Git history, private local settings, generated release archives, and runtime data. The helper never changes visibility. Concurrent changes made by another authorized account cannot be prevented by this helper; both visibility checks must pass before it reports success.

If creation or upload fails, inspect the account before retrying: an empty or partially uploaded private repository may already exist. The helper does not delete or overwrite a remote to recover automatically. A timeout is not proof that nothing happened.

## Review and future changes

Review the README, full playbook, job prompts, source notes, security policy, and all source/history checks while private. The owner may make a separate manual public-release decision after review. Do not publish installation reports, private configuration, runtime databases, original conversation attachments, or private diagnostics in issues, releases, or Actions artifacts.

Use reviewed commits and pull requests for later changes. The initial fresh-history helper is not an update or history-rewriting tool.

## Official command references

- [Repository creation and private visibility](https://cli.github.com/manual/gh_repo_create)
- [Browser-based CLI authentication](https://cli.github.com/manual/gh_auth_login)
- [Configure Git to use GitHub CLI authentication](https://cli.github.com/manual/gh_auth_setup-git)
