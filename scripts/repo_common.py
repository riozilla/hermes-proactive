"""Explicit public-source selection shared by validation, releases, and publishing."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_FILES = {
    '.gitattributes', '.gitignore', 'AGENTS.md', 'CHANGELOG.md', 'CONTRIBUTING.md',
    'INSTALL-PROMPT.md', 'LICENSE', 'PLAYBOOK.md', 'README.md', 'SECURITY.md',
    'SOUL.additions.md', 'SOURCE-NOTES.md', 'VERSION',
    'config.merge-fragment.yaml', 'jobs.planning-spec.json',
}
PUBLIC_DIRS = {'.github', 'docs', 'job-prompts', 'scripts', 'skills', 'tests'}
SKIP_DIRS = {'.git', 'dist', 'build', '__pycache__', '.pytest_cache', '.venv'}
SUFFIXES = {'.md', '.py', '.json', '.yaml', '.yml'}
BLOCKED_PARTS = {
    '.hermes', '.ssh', '.aws', '.gnupg', 'private', 'local', 'state', 'logs',
    'output', 'outputs', 'artifacts', 'backups', 'credentials', 'secrets',
}


def allowed_path(relative: str) -> bool:
    """Accept only a relative, generic public source path (not its contents)."""
    path = Path(relative)
    if path.is_absolute() or '..' in path.parts or not path.parts:
        return False
    if any(part.lower() in BLOCKED_PARTS for part in path.parts):
        return False
    if any(part.startswith('.env') for part in path.parts):
        return False
    if path.name == 'LOCAL-SETUP.md' or '.local.' in path.name.lower():
        return False
    if len(path.parts) == 1:
        return relative in PUBLIC_FILES
    return path.parts[0] in PUBLIC_DIRS and path.suffix in SUFFIXES


def public_files(root: Path = ROOT) -> list[Path]:
    """Reject unexpected files, symlinks and binaries; omit only build/tool state."""
    root = root.resolve()
    result: list[Path] = []

    def visit(directory: Path) -> None:
        for path in sorted(directory.iterdir()):
            if path.is_symlink():
                raise ValueError('Symlinks are not allowed in public source.')
            if path.is_dir():
                if path.name in SKIP_DIRS:
                    continue
                if directory == root and path.name not in PUBLIC_DIRS:
                    raise ValueError('Unexpected top-level directory; review locally.')
                if path.name.lower() in BLOCKED_PARTS:
                    raise ValueError('Private/runtime directory found; review locally.')
                visit(path)
                continue
            relative = path.relative_to(root).as_posix()
            if not allowed_path(relative):
                raise ValueError('Unexpected or private file found; review locally.')
            if path.stat().st_size > 1_000_000:
                raise ValueError('Oversized source file; review locally.')
            text = path.read_text(encoding='utf-8')
            if '\x00' in text:
                raise ValueError('Binary content is not allowed in public source.')
            result.append(path)

    visit(root)
    return sorted(result, key=lambda p: p.relative_to(root).as_posix())
