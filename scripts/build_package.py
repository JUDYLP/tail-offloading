#!/usr/bin/env python3
"""Build or check the distribution ZIP using an explicit source manifest."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from zipfile import BadZipFile, ZIP_DEFLATED, ZipFile, ZipInfo


PACKAGE_FILES = (
    "LICENSE",
    "README.md",
    "README.zh-CN.md",
    "SKILL.md",
    "references/contracts.md",
    "references/example.md",
)
PREFIX = "tail-offloading/"


def source_contents(root: Path) -> dict[str, bytes]:
    return {PREFIX + name: (root / name).read_bytes() for name in PACKAGE_FILES}


def build(root: Path, archive: Path) -> None:
    contents = source_contents(root)
    with ZipFile(archive, "w", compression=ZIP_DEFLATED) as package:
        for name, data in contents.items():
            info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = ZIP_DEFLATED
            package.writestr(info, data)


def check(root: Path, archive: Path) -> None:
    expected = source_contents(root)
    with ZipFile(archive) as package:
        names = package.namelist()
        if len(names) != len(set(names)):
            raise ValueError("duplicate ZIP entries")
        missing = sorted(expected.keys() - set(names))
        extra = sorted(set(names) - expected.keys())
        if missing or extra:
            raise ValueError(f"package manifest differs: missing={missing}, extra={extra}")
        changed = [name for name, data in expected.items() if package.read(name) != data]
        if changed:
            raise ValueError(f"package contents differ: {', '.join(changed)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="check without rewriting the ZIP")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    archive = root / "tail-offloading.zip"
    try:
        if args.check:
            check(root, archive)
        else:
            build(root, archive)
    except (OSError, ValueError, BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"OK: {'checked' if args.check else 'built'} {archive.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
