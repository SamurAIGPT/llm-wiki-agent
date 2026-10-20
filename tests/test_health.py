import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class HealthIndexSyncTest(unittest.TestCase):
    def test_encoded_links_match_files_and_preserve_real_sync_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tools = root / "tools"
            tools.mkdir()
            for name in ("__init__.py", "_utils.py", "health.py"):
                shutil.copyfile(Path(__file__).resolve().parents[1] / "tools" / name, tools / name)

            concepts = root / "wiki" / "concepts"
            concepts.mkdir(parents=True)
            for name in ("Café Guide.md", "Rate%20Guide.md", "C++Guide.md", "Plain.md", "Orphan.md"):
                (concepts / name).write_text("Real wiki content. " * 10, encoding="utf-8")
            links = ("Caf%C3%A9%20Guide.md", "Rate%2520Guide.md", "C++Guide.md", "Plain.md", "Deleted%20Page.md")
            (root / "wiki" / "index.md").write_text(
                "# Wiki Index\n" + "\n".join(f"- [Page](concepts/{link})" for link in links),
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, "tools/health.py", "--json"],
                cwd=root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True,
            )
            report = json.loads(result.stdout)
            self.assertEqual(report["total_pages"], 5)
            self.assertEqual(report["empty_files"], [])
            self.assertEqual(
                report["index_sync"],
                {
                    "in_index_not_on_disk": [str(Path("wiki/concepts/Deleted Page.md"))],
                    "on_disk_not_in_index": [str(Path("wiki/concepts/Orphan.md"))],
                },
            )
            self.assertEqual(report["log_coverage"], [])
