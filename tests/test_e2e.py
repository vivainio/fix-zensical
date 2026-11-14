"""Build the demo book with the tool applied and check the site carries the assets."""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@unittest.skipUnless(shutil.which("zensical"), "zensical not installed")
class DemoBookTest(unittest.TestCase):
    def test_build_includes_reading_tools(self):
        with tempfile.TemporaryDirectory() as t:
            repo = Path(t)
            shutil.copy(ROOT / "zensical.toml", repo)
            shutil.copytree(ROOT / "docs", repo / "docs", ignore=shutil.ignore_patterns("assets"))
            r = subprocess.run([sys.executable, "-m", "fix_zensical.cli", "--repo", str(repo)],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            b = subprocess.run(["zensical", "build", "--clean"], cwd=repo, capture_output=True, text=True)
            self.assertEqual(b.returncode, 0, b.stdout + b.stderr)
            site = repo / "site"
            for name in ("reading-tools.css", "reading-tools.js"):
                self.assertTrue((site / "assets/reading-tools" / name).is_file(), name)
            html = (site / "diagrams/index.html").read_text()
            self.assertIn("assets/reading-tools/reading-tools.js", html)
            self.assertIn("assets/reading-tools/reading-tools.css", html)
            self.assertIn('class="mermaid"', html)


if __name__ == "__main__":
    unittest.main()
