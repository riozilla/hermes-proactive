"""Validate custom planning data, job consistency, links, and generated content."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote
from repo_common import ROOT, PUBLIC_FILES, public_files
from build_playbook import render

EXPECTED_JOBS = {
    'change-radar', 'preflight', 'daily-preparation', 'progress-worker',
    'curiosity', 'evening-closure', 'coverage-health', 'weekly-friction',
}


def valid_schedule(expression: str) -> bool:
    """Validate the numeric five-field subset used here; not a cron interpreter."""
    fields = expression.split()
    if len(fields) != 5:
        return False
    for field, (low, high) in zip(fields, [(0, 59), (0, 23), (1, 31), (1, 12), (0, 7)]):
        for part in field.split(','):
            pieces = part.split('/')
            if len(pieces) > 2:
                return False
            if len(pieces) == 2:
                if not pieces[1].isdigit() or not 1 <= int(pieces[1]) <= high - low + 1:
                    return False
            base = pieces[0]
            if base == '*':
                continue
            nums = base.split('-')
            if len(nums) > 2 or any(not n.isdigit() for n in nums):
                return False
            values = [int(n) for n in nums]
            if any(not low <= n <= high for n in values):
                return False
            if len(values) == 2 and values[0] > values[1]:
                return False
    return True


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    try:
        paths = public_files(root)
    except (OSError, UnicodeError, ValueError) as exc:
        return [str(exc)]
    names = {p.relative_to(root).as_posix() for p in paths}
    if not PUBLIC_FILES.issubset(names):
        errors.append('One or more required top-level public files are missing.')
    try:
        spec = json.loads((root / 'jobs.planning-spec.json').read_text(encoding='utf-8'))
        if spec['format'] != 'proactive-ops-planning-spec-v1-NOT-HERMES-NATIVE-IMPORT':
            errors.append('Planning format must remain explicitly non-native.')
        if spec['timezone'] != '{{USER_TIMEZONE}}':
            errors.append('Public planning data must not contain a personal timezone.')
        if spec['enabled_by_default'] is not False or spec['requires_installation_schema_check'] is not True:
            errors.append('Planning data must be disabled and require schema verification.')
        if spec['skill'] != 'proactive-ops':
            errors.append('Unexpected skill name.')
        jobs = spec['jobs']
        if len(jobs) != 8 or {j['id'] for j in jobs} != EXPECTED_JOBS:
            errors.append('Exactly the eight expected responsibilities are required.')
        canonical = (root / 'skills/proactive-ops/references/JOBS.md').read_text(encoding='utf-8')
        common = canonical.split('## Common prompt — prepend to EVERY job\n\n', 1)[1].split('\n---', 1)[0].strip()
        for job in jobs:
            job_id = job['id']
            if not valid_schedule(job['schedule']):
                errors.append(f'{job_id}: invalid proposed schedule.')
            if job['gate'] and not job['fallback']:
                errors.append(f'{job_id}: a gated job requires a fallback.')
            if job['fallback'] is not None and not valid_schedule(job['fallback']):
                errors.append(f'{job_id}: invalid fallback schedule.')
            expected_path = f'job-prompts/{job_id}.md'
            if job['prompt_file'] != expected_path:
                errors.append(f'{job_id}: unexpected prompt path.')
                continue
            section = canonical.split(f'## {job_id}\n', 1)[1].split('\n---', 1)[0]
            specific = section.split('**Job-specific prompt:**\n\n', 1)[1].strip()
            expected = f"# {job['name']}\n\n{common}\n\n{specific}\n"
            actual = (root / expected_path).read_text(encoding='utf-8')
            if actual != expected:
                errors.append(f'{job_id}: full prompt and canonical definition differ.')
            if f"`{job['schedule']}`" not in section or job['budget'] not in section:
                errors.append(f'{job_id}: planning metadata and canonical definition differ.')
            if job['fallback'] and f"`{job['fallback']}`" not in section:
                errors.append(f'{job_id}: fallback and canonical definition differ.')
        actual_prompts = {p.stem for p in (root / 'job-prompts').glob('*.md')}
        if actual_prompts != EXPECTED_JOBS:
            errors.append('Unexpected or missing prompt files.')
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        errors.append(f'Planning/canonical document validation failed: {type(exc).__name__}.')

    for path in paths:
        if path.suffix != '.md':
            continue
        # Inspect inline relative document links (not fenced code examples).
        text = re.sub(r'```.*?```', '', path.read_text(encoding='utf-8'), flags=re.S)
        for target in re.findall(r'\]\(([^)\s]+)\)', text):
            if '://' in target or target.startswith(('#', 'mailto:')):
                continue
            rel = unquote(target.split('#', 1)[0])
            destination = (path.parent / rel).resolve()
            if not destination.is_relative_to(root.resolve()) or not destination.exists():
                errors.append(f'{path.relative_to(root)}: broken or escaping relative link.')
    try:
        if (root / 'PLAYBOOK.md').read_text(encoding='utf-8') != render(root):
            errors.append('PLAYBOOK.md is stale; run scripts/build_playbook.py.')
    except (OSError, ValueError):
        errors.append('Cannot generate or read PLAYBOOK.md.')
    return errors


if __name__ == '__main__':
    failures = validate()
    if failures:
        for error in failures:
            print('FAIL:', error, file=sys.stderr)
        raise SystemExit(1)
    print('PASS: eight jobs, schedules, full prompts, public paths, links, and playbook.')
