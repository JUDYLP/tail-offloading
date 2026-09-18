import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_skill.py"
SPEC = importlib.util.spec_from_file_location("validate_skill", MODULE_PATH)
validate_skill = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validate_skill)


class FrontmatterTests(unittest.TestCase):
    def test_requires_line_anchored_closing_delimiter(self):
        malformed = """---
name: tail-offloading
description: value containing --- characters
# no closing delimiter
## Body
---
"""
        with self.assertRaisesRegex(ValueError, "frontmatter is not closed"):
            validate_skill.parse_frontmatter(malformed)

    def test_comments_do_not_satisfy_required_fields(self):
        frontmatter = """name: tail-offloading
# description: commented out
metadata: description: nested text
"""
        fields = validate_skill.parse_required_fields(frontmatter)
        self.assertEqual(fields, {"name": "tail-offloading"})

    def test_empty_values_do_not_satisfy_required_fields(self):
        fields = validate_skill.parse_required_fields(
            "name: tail-offloading\ndescription:   "
        )
        self.assertEqual(fields, {"name": "tail-offloading"})

    def test_valid_skill_passes(self):
        with tempfile.TemporaryDirectory(prefix="tail-offloading-test-") as tmp:
            root = Path(tmp) / "tail-offloading"
            (root / "references").mkdir(parents=True)
            (root / "references" / "guide.md").write_text("guide", encoding="utf-8")
            (root / "SKILL.md").write_text(
                """---
name: tail-offloading
description: Route bounded work.
---

Read [the guide](references/guide.md).
""",
                encoding="utf-8",
            )
            self.assertTrue(validate_skill.validate(root).startswith("OK:"))


if __name__ == "__main__":
    unittest.main()
