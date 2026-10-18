"""Build a reproducible text-only source archive after structure/privacy checks."""
from __future__ import annotations

import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo
from repo_common import ROOT, public_files
from validate_repo import validate
from check_public_content import audit, read_denylist


def build(root: Path = ROOT) -> Path:
    errors = validate(root)
    findings, _ = audit(root, denylist=read_denylist(root))
    if errors or findings:
        raise ValueError('Source validation/audit failed; run the local checks for rule IDs.')
    version = (root / 'VERSION').read_text(encoding='utf-8').strip()
    if not version or any(c not in '0123456789.' for c in version):
        raise ValueError('Invalid release version.')
    destination = root / 'dist'
    if destination.is_symlink():
        raise ValueError('Release destination must not be a symlink.')
    destination.mkdir(exist_ok=True)
    target = destination / f'hermes-proactive-{version}.zip'
    files = public_files(root)
    with ZipFile(target, 'w', compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            relative = 'hermes-proactive/' + path.relative_to(root).as_posix()
            info = ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
    with ZipFile(target) as archive:
        if archive.testzip() is not None or len(archive.infolist()) != len(files):
            raise ValueError('Release archive integrity check failed.')
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    (destination / 'SHA256SUMS').write_text(f'{digest}  {target.name}\n', encoding='utf-8')
    return target


if __name__ == '__main__':
    try:
        archive = build()
    except (OSError, ValueError) as exc:
        raise SystemExit(str(exc))
    print(f'Built {archive.name}; no Git history or private runtime data included.')
