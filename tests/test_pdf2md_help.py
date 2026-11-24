"""Help must work without conversion dependencies or a UTF-8 console."""

import os
from pathlib import Path
import subprocess
import sys
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "pdf2md.py"


class PdfHelpTests(unittest.TestCase):
    def test_help_with_common_console_encodings(self):
        for encoding in ("cp1252", "ascii", "utf-8"):
            for flag in ("--help", "-h"):
                with self.subTest(encoding=encoding, flag=flag):
                    result = subprocess.run(
                        [sys.executable, "-S", str(SCRIPT), flag],
                        env={**os.environ, "PYTHONIOENCODING": encoding},
                        capture_output=True,
                    )
                    self.assertEqual(0, result.returncode, result.stderr.decode(encoding, errors="replace"))
                    self.assertEqual(b"", result.stderr)
                    output = result.stdout.decode(encoding)
                    self.assertIn("Convert PDF/arXiv to Markdown for raw/", output)
                    self.assertIn("--backend {auto,arxiv2md,marker,pymupdf4llm}", output)
                    self.assertIn("Inputs:", output)
                    self.assertIn("Examples:", output)
                    self.assertIn("python tools/pdf2md.py paper.pdf --backend marker", output)


if __name__ == "__main__":
    unittest.main()
