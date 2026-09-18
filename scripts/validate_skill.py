#!/usr/bin/env python3
"""Validate the portable structure of the tail-offloading skill."""

from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_FIELDS = ("name", "description")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_frontmatter(text: str) -> tuple[str, str]:
    """Return frontmatter and body using line-anchored delimiters."""
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("SKILL.md must start with YAML frontmatter")

    try:
        closing_index = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("SKILL.md frontmatter is not closed") from exc

    frontmatter = "\n".join(lines[1:closing_index])
    body = "\n".join(lines[closing_index + 1 :])
    return frontmatter, body


def parse_required_fields(frontmatter: str) -> dict[str, str]:
    """Extract non-empty required keys from actual frontmatter fields."""
    fields: dict[str, str] = {}
    pattern = re.compile(r"^(name|description):[ \t]*(\S.*)$")

    for line in frontmatter.splitlines():
        match = pattern.match(line)
        if match:
            fields[match.group(1)] = match.group(2).strip()

    return fields


def validate(root: Path) -> str:
    skill_path = root / "SKILL.md"
    if not skill_path.is_file():
        raise ValueError("SKILL.md is missing")

    text = skill_path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(text)
    fields = parse_required_fields(frontmatter)

    missing = [field for field in REQUIRED_FIELDS if field not in fields]
    if missing:
        raise ValueError(f"missing or empty frontmatter fields: {', '.join(missing)}")

    if fields["name"] != root.name:
        raise ValueError(f"skill name must match directory name: {root.name}")

    links = re.findall(r"\[[^\]]+\]\(([^)]+\.md)\)", body)
    if not links:
        raise ValueError("SKILL.md does not link to any Markdown references")

    missing_refs = [target for target in links if not (root / target).is_file()]
    if missing_refs:
        raise ValueError(f"missing referenced files: {', '.join(missing_refs)}")

    return f"OK: {root.name} ({len(links)} Markdown references checked)"


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    try:
        print(validate(root))
    except ValueError as exc:
        fail(str(exc))


if __name__ == "__main__":
    main()
