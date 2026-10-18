"""Publish a reviewed fresh snapshot to a NEW PRIVATE GitHub repository, only by opt-in."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from repo_common import ROOT, public_files
from validate_repo import validate
from check_public_content import audit, read_denylist

GENERIC_NAME = 'Hermes Proactive contributors'
GENERIC_EMAIL = 'contributors@example.invalid'


def run(args: list[str], cwd: Path, env: dict[str, str], timeout: int = 90) -> str:
    """Do not relay external stdout/stderr that could include private diagnostics."""
    result = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError(f'{args[0]} command failed; inspect the account locally before retrying. '
                           'A remote may already exist. No private command output was printed.')
    return result.stdout.strip()


def safe_git_environment() -> dict[str, str]:
    # Leave credential resolution to GitHub CLI/Git; do not inspect credential files.
    env = os.environ.copy()
    for name in list(env):
        if name.startswith(('GIT_AUTHOR_', 'GIT_COMMITTER_', 'GIT_CONFIG_', 'GIT_TRACE')) or name in {
            'GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY',
            'GIT_ALTERNATE_OBJECT_DIRECTORIES', 'GH_DEBUG',
        }:
            env.pop(name, None)
    env.update({
        'GIT_AUTHOR_NAME': GENERIC_NAME, 'GIT_AUTHOR_EMAIL': GENERIC_EMAIL,
        'GIT_COMMITTER_NAME': GENERIC_NAME, 'GIT_COMMITTER_EMAIL': GENERIC_EMAIL,
        'GH_PROMPT_DISABLED': '1', 'GH_HOST': 'github.com',
    })
    return env


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', default='hermes-proactive', help='New repository name in the authenticated user account.')
    parser.add_argument('--publish', action='store_true', help='Explicitly create and push the PRIVATE repository.')
    parser.add_argument('--expected-owner', help='Refuse to publish unless the authenticated login matches this account.')
    args = parser.parse_args(argv)
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,99}', args.repo):
        parser.error('Use a simple repository name without an owner, slash, or spaces.')
    if args.expected_owner and not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]{0,38}', args.expected_owner):
        parser.error('Use a valid GitHub login for --expected-owner.')
    denylist = read_denylist()
    errors = validate()
    findings, _ = audit(denylist=denylist)
    if errors or findings:
        print('FAIL: local validation/audit failed. Nothing was published.', file=sys.stderr)
        return 1
    if not args.publish:
        print(f'DRY RUN: validated public source for a new PRIVATE repository named {args.repo}.')
        print('No GitHub authentication, network call, commit, or publication was attempted.')
        print('Use --publish to create a fresh generic-identity snapshot and publish it.')
        return 0
    if not shutil.which('gh') or not shutil.which('git'):
        print('Git and GitHub CLI are required; authenticate with gh auth login.', file=sys.stderr)
        return 1
    env = safe_git_environment()
    try:
        owner = run(['gh', 'api', '--hostname', 'github.com', 'user', '--jq', '.login'], ROOT, env)
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]{0,38}', owner):
            raise RuntimeError('Could not resolve an unambiguous authenticated account.')
        if args.expected_owner and owner.lower() != args.expected_owner.lower():
            raise RuntimeError('Authenticated account does not match --expected-owner; nothing was created.')
        full_name = f'{owner}/{args.repo}'
        print(f'Publishing new PRIVATE repository: {full_name}')
        with tempfile.TemporaryDirectory(prefix='hermes-proactive-publish-') as directory:
            stage = Path(directory) / 'source'
            stage.mkdir()
            for source in public_files():
                target = stage / source.relative_to(ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read_bytes())
            errors = validate(stage)
            findings, _ = audit(stage, denylist=denylist)
            if errors or findings:
                raise RuntimeError('Staged source failed validation. Nothing was published.')
            run(['git', '-c', 'init.templateDir=', 'init', '-b', 'main'], stage, env)
            run(['git', 'config', 'user.name', GENERIC_NAME], stage, env)
            run(['git', 'config', 'user.email', GENERIC_EMAIL], stage, env)
            run(['git', 'config', 'commit.gpgsign', 'false'], stage, env)
            run(['git', 'config', 'core.hooksPath', str(stage / '.git' / 'no-hooks')], stage, env)
            run(['git', 'add', '--', '.'], stage, env)
            staged_paths = set(run(['git', 'ls-files'], stage, env).splitlines())
            expected_paths = {p.relative_to(stage).as_posix() for p in public_files(stage)}
            if staged_paths != expected_paths:
                raise RuntimeError('Git staging differs from the reviewed source; inspect global ignore settings.')
            run(['git', 'commit', '-m', 'Initial proactive operations pack for private review'], stage, env)
            findings, _ = audit(stage, history=True, denylist=denylist)
            if findings:
                raise RuntimeError('Fresh Git history failed review. Nothing was published.')
            expected_sha = run(['git', 'rev-parse', 'HEAD'], stage, env)
            # Create empty and verify PRIVATE visibility BEFORE uploading any files.
            # gh refuses an existing name. Never overwrite, force-push, or delete.
            run(['gh', 'repo', 'create', full_name, '--private', '--source', str(stage),
                 '--remote', 'origin', '--description',
                 'A privacy-conscious proactive operations pack for Hermes Agent: prompts, eight jobs, policies, and validation.'],
                stage, env, timeout=180)
            metadata = json.loads(run(['gh', 'api', '--hostname', 'github.com', f'repos/{full_name}'], stage, env))
            if metadata.get('private') is not True:
                raise RuntimeError('Remote is not verified PRIVATE. No files were uploaded; inspect before retrying.')
            run(['git', 'push', 'origin', 'main'], stage, env, timeout=180)
            metadata = json.loads(run(['gh', 'api', '--hostname', 'github.com', f'repos/{full_name}'], stage, env))
            actual_sha = run(['gh', 'api', '--hostname', 'github.com', f'repos/{full_name}/commits/main', '--jq', '.sha'], stage, env)
            if metadata.get('private') is not True or actual_sha != expected_sha:
                raise RuntimeError('Upload attempted but private visibility/commit verification failed; inspect before retrying.')
            print('Verified PRIVATE visibility and matching remote main-branch commit.')
            print('This helper never changes visibility. Any public release requires your separate review and action.')
            print(metadata['html_url'])
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
