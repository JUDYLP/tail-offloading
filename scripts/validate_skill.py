#!/usr/bin/env python3
"""Validate the portable structure of the tail-offloading skill."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    skill_path = root / "SKILL.md"

    if not skill_path.is_file():
        fail("SKILL.md is missing")

    text = skill_path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail("SKILL.md must start with YAML frontmatter")

    try:
        _, frontmatter, body = text.split("---", 2)
    except ValueError:
        fail("SKILL.md frontmatter is not closed")

    required = ("name:", "description:")
    missing = [field[:-1] for field in required if field not in frontmatter]
    if missing:
        fail(f"missing frontmatter fields: {', '.join(missing)}")

    name_match = re.search(r"(?m)^name:\s*([^\s]+)\s*$", frontmatter)
    if not name_match or name_match.group(1) != root.name:
        fail(f"skill name must match directory name: {root.name}")

    links = re.findall(r"\[[^\]]+\]\(([^)]+\.md)\)", body)
    if not links:
        fail("SKILL.md does not link to any Markdown references")

    missing_refs = [target for target in links if not (root / target).is_file()]
    if missing_refs:
        fail(f"missing referenced files: {', '.join(missing_refs)}")

    print(f"OK: {root.name} ({len(links)} Markdown references checked)")


if __name__ == "__main__":
    main()
