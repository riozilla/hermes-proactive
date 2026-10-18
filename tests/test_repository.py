"""Synthetic source-safety tests; these do not exercise a live Hermes installation."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from repo_common import allowed_path, public_files
from validate_repo import validate, valid_schedule
from check_public_content import audit, read_denylist, scan_text
from build_playbook import render
from build_release import build
from publish_github import main as publish_main, safe_git_environment, GENERIC_EMAIL, GENERIC_NAME


class PlanningTests(unittest.TestCase):
    def test_whole_repository(self):
        self.assertEqual(validate(ROOT), [])

    def test_playbook_is_current(self):
        self.assertEqual((ROOT / 'PLAYBOOK.md').read_text(), render(ROOT))

    def test_valid_numeric_cron(self):
        for value in ('*/10 * * * *', '5,20,35,50 * * * *', '10 10,14,18 * * *', '0 15 * * 5'):
            with self.subTest(value=value):
                self.assertTrue(valid_schedule(value))

    def test_invalid_numeric_cron(self):
        for value in ('* * * *', '60 * * * *', '0 24 * * *', '*/0 * * * *', '0 8 0 * *', '0 8 * 13 *', '0 8 * * 8', '0 8 * * FRI', '0 8 * * 5-2'):
            with self.subTest(value=value):
                self.assertFalse(valid_schedule(value))

    def test_paths_are_source_only(self):
        self.assertGreater(len(public_files(ROOT)), 30)
        for path in public_files(ROOT):
            self.assertTrue(allowed_path(path.relative_to(ROOT).as_posix()))


class ScannerTests(unittest.TestCase):
    def rules(self, value: str):
        return {rule for rule, _ in scan_text(value)}

    def test_generic_example_is_allowed(self):
        self.assertEqual(scan_text('Contact sample@example.invalid for a synthetic example.'), [])

    def test_non_example_email_flagged(self):
        value = 'synthetic' + '@' + 'mail-provider' + '.com'
        self.assertIn('non-example-email', self.rules(value))
        self.assertEqual(scan_text('author 0+synthetic@users.noreply.github.com'), [])
        self.assertEqual(scan_text('committer GitHub <noreply@github.com>'), [])
        self.assertIn('non-example-email', self.rules('synthetic' + '@' + 'github.com'))

    def test_github_token_pattern(self):
        value = 'gh' + 'p_' + 'x' * 36
        self.assertIn('github-token', self.rules(value))

    def test_aws_pattern(self):
        value = 'AK' + 'IA' + 'Z' * 16
        self.assertIn('aws-access-key', self.rules(value))

    def test_provider_pattern(self):
        value = 's' + 'k-' + 'q' * 35
        self.assertIn('provider-key', self.rules(value))

    def test_slack_pattern(self):
        value = 'xo' + 'xb-' + '123-' * 10
        self.assertIn('slack-token', self.rules(value))

    def test_private_key_pattern(self):
        value = '-----' + 'BEGIN RSA ' + 'PRIVATE KEY' + '-----'
        self.assertIn('private-key', self.rules(value))

    def test_credential_url_pattern(self):
        value = 'https' + '://synthetic:synthetic' + '@example.invalid/path'
        self.assertIn('credential-url', self.rules(value))

    def test_private_ip_pattern(self):
        value = '.'.join(['192', '168', '23', '9'])
        self.assertIn('private-ipv4', self.rules(value))

    def test_private_home_pattern(self):
        value = '/' + 'Users' + '/synthetic' + '/project'
        self.assertIn('personal-home-path', self.rules(value))

    def test_phone_pattern(self):
        value = '+' + '12345678901'
        self.assertIn('phone-number', self.rules(value))

    def test_assignment_pattern(self):
        value = 'API' + '_KEY=' + 'synthetic-value'
        self.assertIn('credential-assignment', self.rules(value))

    def test_placeholder_assignment_allowed(self):
        value = 'API' + '_KEY=' + '${EXAMPLE_VALUE}'
        self.assertEqual(scan_text(value), [])

    def test_denylist_boundaries(self):
        self.assertEqual(scan_text('caterpillar material', ('cat',)), [])
        self.assertIn('local-forbidden-term', {r for r, _ in scan_text('SyntheticPerson update', ('SyntheticPerson',))})

    def test_reports_do_not_include_match(self):
        value = 'gh' + 'p_' + 'x' * 36
        self.assertNotIn(value, repr(scan_text(value)))

    def test_forbidden_paths(self):
        for name in ('../README.md', '/README.md', '.env', 'private/setup.md',
                     'skills/proactive-ops/references/LOCAL-SETUP.md', 'docs/runtime.local.json', 'docs/picture.png'):
            with self.subTest(name=name):
                self.assertFalse(allowed_path(name))

    def test_template_path_allowed(self):
        self.assertTrue(allowed_path('skills/proactive-ops/references/LOCAL-SETUP.example.md'))

    def test_local_denylist_stays_external(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'forbidden-terms.txt'
            path.write_text('SyntheticPerson\n')
            with mock.patch.dict(os.environ, {'PUBLIC_REPO_DENYLIST_FILE': str(path)}):
                self.assertEqual(read_denylist(ROOT), ('SyntheticPerson',))

    def test_internal_denylist_rejected(self):
        with mock.patch.dict(os.environ, {'PUBLIC_REPO_DENYLIST_FILE': str(ROOT / 'README.md')}):
            with self.assertRaises(ValueError):
                read_denylist(ROOT)

    def test_unexpected_file_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'README.md').write_text('Generic source.')
            (root / '.env').write_text('Synthetic test only.')
            with self.assertRaises(ValueError):
                public_files(root)

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'README.md').write_text('Generic source.')
            try:
                (root / 'SOUL.additions.md').symlink_to(root / 'README.md')
            except OSError:
                self.skipTest('Symlink creation unavailable in this environment.')
            with self.assertRaises(ValueError):
                public_files(root)

    def test_current_source_scan(self):
        findings, _ = audit(ROOT)
        self.assertEqual(findings, [])


class ReleaseTests(unittest.TestCase):
    def test_archive_is_reproducible_and_has_no_git_metadata(self):
        first = build(ROOT)
        digest = hashlib.sha256(first.read_bytes()).hexdigest()
        second = build(ROOT)
        self.assertEqual(digest, hashlib.sha256(second.read_bytes()).hexdigest())
        with ZipFile(second) as archive:
            names = archive.namelist()
            self.assertEqual(len(names), len(public_files(ROOT)))
            self.assertTrue(all(n.startswith('hermes-proactive/') for n in names))
            self.assertFalse(any('/.git/' in n for n in names))
            self.assertFalse(any(n.endswith('/LOCAL-SETUP.md') for n in names))
            self.assertIsNone(archive.testzip())
            self.assertTrue(all(entry.date_time == (1980, 1, 1, 0, 0, 0) for entry in archive.infolist()))

    def test_publish_dry_run_has_no_external_commands(self):
        with mock.patch('publish_github.subprocess.run') as runner:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(publish_main([]), 0)
            runner.assert_not_called()

    def test_publish_rejects_owner_override(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                publish_main(['--repo', 'different-owner/name'])

    def test_generic_commit_identity_overrides_environment(self):
        with mock.patch.dict(os.environ, {'GIT_AUTHOR_NAME': 'SyntheticPerson', 'GIT_AUTHOR_EMAIL': 'synthetic@example.invalid'}):
            env = safe_git_environment()
            self.assertEqual(env['GIT_AUTHOR_NAME'], GENERIC_NAME)
            self.assertEqual(env['GIT_COMMITTER_NAME'], GENERIC_NAME)
            self.assertEqual(env['GIT_AUTHOR_EMAIL'], GENERIC_EMAIL)
            self.assertEqual(env['GIT_COMMITTER_EMAIL'], GENERIC_EMAIL)


    @unittest.skipUnless(shutil.which('git'), 'Git required for staged publication test')
    def test_publication_uses_new_snapshot_and_verifies_remote(self):
        import publish_github
        original_run = publish_github.run
        created = {}
        def fake_run(args, cwd, env, timeout=90):
            if args[:2] == ['git', 'push']:
                self.assertTrue(created.get('private_verified'))
                created['pushed'] = True
                return ''
            if args[0] != 'gh':
                return original_run(args, cwd, env, timeout)
            if args[1:3] == ['repo', 'create']:
                self.assertIn('--private', args)
                self.assertNotIn('--public', args)
                self.assertNotIn('--push', args)
                self.assertNotIn('--force', args)
                self.assertNotEqual(cwd, ROOT)
                self.assertFalse((cwd / 'dist').exists())
                created['sha'] = original_run(['git', 'rev-parse', 'HEAD'], cwd, env)
                return ''
            if 'user' in args:
                return 'example-owner'
            if any('/commits/main' in arg for arg in args):
                self.assertTrue(created.get('pushed'))
                return created['sha']
            created['private_verified'] = True
            return json.dumps({'private': True, 'html_url': 'https://github.com/example-owner/hermes-proactive'})
        with mock.patch('publish_github.run', side_effect=fake_run), mock.patch('publish_github.shutil.which', return_value='/synthetic/executable'):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(publish_main(['--publish', '--expected-owner', 'example-owner']), 0)
        self.assertTrue(created.get('pushed'))

    def test_public_flag_is_rejected(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                publish_main(['--public'])

    def test_wrong_account_prevents_creation(self):
        with mock.patch('publish_github.run', return_value='different-owner') as runner, mock.patch('publish_github.shutil.which', return_value='/synthetic/executable'):
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(publish_main(['--publish', '--expected-owner', 'example-owner']), 1)
        self.assertEqual(runner.call_count, 1)

    @unittest.skipUnless(shutil.which('git'), 'Git required for staged publication test')
    def test_unverified_private_visibility_blocks_upload(self):
        import publish_github
        original_run = publish_github.run
        external = []
        def fake_run(args, cwd, env, timeout=90):
            if args[:2] == ['git', 'push']:
                self.fail('Must not upload before private visibility is verified')
            if args[0] != 'gh':
                return original_run(args, cwd, env, timeout)
            external.append(args)
            if 'user' in args:
                return 'example-owner'
            if args[1:3] == ['repo', 'create']:
                return ''
            return json.dumps({'private': False})
        with mock.patch('publish_github.run', side_effect=fake_run), mock.patch('publish_github.shutil.which', return_value='/synthetic/executable'):
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(publish_main(['--publish']), 1)
        self.assertEqual(len(external), 3)

    @unittest.skipUnless(shutil.which('git'), 'Git required for staged publication test')
    def test_remote_creation_failure_is_not_overwritten_or_retried(self):
        import publish_github
        original_run = publish_github.run
        external = []
        def fake_run(args, cwd, env, timeout=90):
            if args[0] != 'gh':
                return original_run(args, cwd, env, timeout)
            external.append(args)
            if 'user' in args:
                return 'example-owner'
            raise RuntimeError('Synthetic creation failure')
        with mock.patch('publish_github.run', side_effect=fake_run), mock.patch('publish_github.shutil.which', return_value='/synthetic/executable'):
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(publish_main(['--publish']), 1)
        self.assertEqual(len(external), 2)
        self.assertFalse(any('delete' in args for args in external))

    @unittest.skipUnless(shutil.which('git'), 'Git required for synthetic history test')
    def test_removed_secret_still_detected_in_history(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env = safe_git_environment()
            def git(*args):
                subprocess.run(['git', *args], cwd=root, env=env, check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            git('-c', 'init.templateDir=', 'init', '-b', 'main')
            git('config', 'commit.gpgsign', 'false')
            git('config', 'core.hooksPath', str(root / '.git' / 'no-hooks'))
            (root / 'README.md').write_text('Synthetic historical value: ' + 'gh' + 'p_' + 'x' * 36)
            git('add', '.')
            git('commit', '-m', 'Synthetic initial fixture')
            (root / 'README.md').write_text('Generic replacement.')
            git('add', '.')
            git('commit', '-m', 'Synthetic clean replacement')
            findings, _ = audit(root, history=True)
            self.assertTrue(any('github-token' in item for item in findings))


if __name__ == '__main__':
    unittest.main()
