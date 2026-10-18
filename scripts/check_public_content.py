"""Heuristic public-source/history audit. Reports rule IDs, never matched values."""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from repo_common import ROOT, allowed_path, public_files

PATTERNS = {
    'private-key': r'-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----',
    'github-token': r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{25,})\b',
    'aws-access-key': r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
    'google-api-key': r'\bAIza[A-Za-z0-9_-]{30,}\b',
    'provider-key': r'\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{24,}\b',
    'slack-token': r'\bxox[baprs]-[A-Za-z0-9-]{15,}\b',
    'jwt': r'\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b',
    'credential-url': r'https?://[^\s/:]+:[^\s/@]+@',
    'private-ipv4': r'(?<![\w.])(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})(?![\w.])',
    'personal-home-path': r'/(?:Users|home)/[A-Za-z0-9][A-Za-z0-9_.-]*/',
    'phone-number': r'(?<!\w)\+[1-9]\d{9,14}(?!\w)',
}
EMAIL = re.compile(r'\b[A-Za-z0-9.!#$%&*+/=?^_`{|}~-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b')
ASSIGNMENT = re.compile(
    r'''(?im)^\s*["']?(?:[A-Z0-9_]*(?:TOKEN|SECRET|PASSWORD|API_KEY|PRIVATE_KEY))["']?\s*[:=]\s*["']?([^\s"'#,;]+)'''
)


def allowed_example_domain(domain: str) -> bool:
    domain = domain.lower()
    return domain in {'example.com', 'example.org', 'example.net', 'example.invalid', 'localhost.invalid'} or domain.endswith(('.example', '.invalid'))


def allowed_email(address: str, domain: str) -> bool:
    # GitHub's own no-reply addresses appear in commit metadata (email-hiding authors and
    # web-created commits signed by GitHub). They reveal no personal mailbox.
    if domain.lower() == 'users.noreply.github.com' or address.lower() == 'noreply@github.com':
        return True
    return allowed_example_domain(domain)


def scan_text(text: str, denylist: tuple[str, ...] = ()) -> list[tuple[str, int]]:
    findings: list[tuple[str, int]] = []
    for rule, pattern in PATTERNS.items():
        for match in re.finditer(pattern, text):
            findings.append((rule, text.count('\n', 0, match.start()) + 1))
    for match in EMAIL.finditer(text):
        if not allowed_email(match.group(0), match.group(1)):
            findings.append(('non-example-email', text.count('\n', 0, match.start()) + 1))
    for match in ASSIGNMENT.finditer(text):
        value = match.group(1)
        if not (value.startswith(('<', '${', '{{')) or value.lower() in {'null', 'none', 'false', 'unresolved'}):
            findings.append(('credential-assignment', text.count('\n', 0, match.start()) + 1))
    for term in denylist:
        # Boundary-aware for word-like edges; do not print the private term.
        left = r'(?<!\w)' if term[0].isalnum() else ''
        right = r'(?!\w)' if term[-1].isalnum() else ''
        for match in re.finditer(left + re.escape(term) + right, text, re.I):
            findings.append(('local-forbidden-term', text.count('\n', 0, match.start()) + 1))
    return sorted(set(findings))


def read_denylist(root: Path = ROOT) -> tuple[str, ...]:
    filename = os.environ.get('PUBLIC_REPO_DENYLIST_FILE')
    if not filename:
        return ()
    path = Path(filename).expanduser().resolve()
    if path.is_relative_to(root.resolve()):
        raise ValueError('A local forbidden-term list must be outside the repository.')
    return tuple(line.strip() for line in path.read_text(encoding='utf-8').splitlines()
                 if line.strip() and not line.lstrip().startswith('#'))


def git_output(root: Path, *args: str) -> bytes:
    result = subprocess.run(['git', '-C', str(root), *args], capture_output=True, timeout=60)
    if result.returncode:
        raise ValueError('Git history inspection failed; no private command output was printed.')
    return result.stdout


def audit(root: Path = ROOT, history: bool = False, denylist: tuple[str, ...] = ()) -> tuple[list[str], int]:
    findings: list[str] = []
    paths = public_files(root)
    for index, path in enumerate(paths, 1):
        relative = path.relative_to(root).as_posix()
        for rule, line in scan_text(relative + '\n' + path.read_text(encoding='utf-8'), denylist):
            findings.append(f'public-file-{index}: {rule} at text line {line}')
    count = len(paths)
    if history:
        if git_output(root, 'rev-parse', '--show-toplevel').decode().strip() != str(root.resolve()):
            raise ValueError('History audit must run at this repository root.')
        objects = git_output(root, 'rev-list', '--objects', '--all').decode('utf-8').splitlines()
        seen: set[str] = set()
        for entry in objects:
            oid, _, name = entry.partition(' ')
            if name:
                for rule, line in scan_text(name, denylist):
                    findings.append(f'history-path: {rule} at text line {line}')
            if oid in seen:
                continue
            seen.add(oid)
            kind = git_output(root, 'cat-file', '-t', oid).decode().strip()
            if kind not in {'blob', 'commit', 'tag'}:
                continue
            if kind == 'blob' and name and not allowed_path(name):
                findings.append('history-blob: unexpected/private file path')
            raw = git_output(root, 'cat-file', '-p', oid)
            try:
                text = raw.decode('utf-8')
            except UnicodeError:
                findings.append('history-object: non-text data requires review')
                continue
            if '\x00' in text:
                findings.append('history-object: binary data requires review')
            for rule, line in scan_text(text, denylist):
                findings.append(f'history-{kind}: {rule} at text line {line}')
            count += 1
    return findings, count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--history', action='store_true', help='Also scan reachable Git history and metadata.')
    args = parser.parse_args()
    try:
        findings, count = audit(history=args.history, denylist=read_denylist())
    except (OSError, UnicodeError, ValueError, subprocess.SubprocessError) as exc:
        print(f'FAIL: audit could not complete ({type(exc).__name__}); inspect locally.', file=sys.stderr)
        return 1
    if findings:
        print('\n'.join('FAIL: ' + f for f in findings), file=sys.stderr)
        return 1
    print(f'PASS: {count} public files/history objects checked; no flagged content found.')
    print('Heuristic check only; manual privacy review is still required.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
