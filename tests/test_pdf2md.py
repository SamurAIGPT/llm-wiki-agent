import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tools import pdf2md


class OutputPathDisplayTests(unittest.TestCase):
    def test_checkout_output_uses_relative_display(self):
        output = pdf2md.REPO_ROOT / "raw" / "papers" / "example.md"

        self.assertEqual(
            pdf2md.display_output_path(output),
            str(Path("raw") / "papers" / "example.md"),
        )

    def test_absolute_output_outside_checkout_completes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "input.pdf"
            input_path.write_bytes(b"")
            output_path = pdf2md.REPO_ROOT.parent / "absolute-output-test.md"
            output = io.StringIO()

            arguments = [
                "pdf2md.py",
                str(input_path),
                "--output",
                str(output_path),
                "--backend",
                "marker",
            ]
            with (
                patch.object(pdf2md.sys, "argv", arguments),
                patch.dict(
                    pdf2md.BACKENDS,
                    {"marker": lambda _source, destination: destination},
                ),
                redirect_stdout(output),
            ):
                pdf2md.main()

        displayed = output.getvalue()
        self.assertIn(f"  Output:  {output_path}", displayed)
        self.assertIn(f"python tools/ingest.py {output_path}", displayed)
        self.assertTrue(output_path.is_absolute())


if __name__ == "__main__":
    unittest.main()
