import importlib.util
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "build_package.py"
SPEC = importlib.util.spec_from_file_location("build_package", MODULE_PATH)
build_package = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(build_package)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.archive = self.root / "package.zip"
        for name in build_package.PACKAGE_FILES:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"source: {name}\n", encoding="utf-8")
        build_package.build(self.root, self.archive)

    def test_roundtrip_and_reproducible_build(self):
        build_package.check(self.root, self.archive)
        first = self.archive.read_bytes()
        build_package.build(self.root, self.archive)
        self.assertEqual(first, self.archive.read_bytes())

    def test_changed_source_is_rejected(self):
        (self.root / "SKILL.md").write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "contents differ"):
            build_package.check(self.root, self.archive)

    def test_missing_file_is_rejected(self):
        with ZipFile(self.archive) as package:
            contents = {name: package.read(name) for name in package.namelist()}
        del contents["tail-offloading/references/example.md"]
        with ZipFile(self.archive, "w") as package:
            for name, data in contents.items():
                package.writestr(name, data)
        with self.assertRaisesRegex(ValueError, "manifest differs.*example.md"):
            build_package.check(self.root, self.archive)

    def test_extra_file_is_rejected(self):
        with ZipFile(self.archive, "a") as package:
            package.writestr("tail-offloading/agents/openai.yaml", "stale")
        with self.assertRaisesRegex(ValueError, "manifest differs.*openai.yaml"):
            build_package.check(self.root, self.archive)

    def test_changed_archive_is_rejected(self):
        with ZipFile(self.archive) as package:
            contents = {name: package.read(name) for name in package.namelist()}
        contents["tail-offloading/SKILL.md"] = b"changed"
        with ZipFile(self.archive, "w") as package:
            for name, data in contents.items():
                package.writestr(name, data)
        with self.assertRaisesRegex(ValueError, "contents differ"):
            build_package.check(self.root, self.archive)


if __name__ == "__main__":
    unittest.main()
