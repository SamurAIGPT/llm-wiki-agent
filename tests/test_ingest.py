import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, patch

from tools import ingest


class ConversionCollisionTests(unittest.TestCase):
    def test_existing_markdown_sibling_is_preserved_and_reported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "paper.pdf"
            output = source.with_suffix(".md")
            original = "Hand-written notes that must remain.\n"
            source.write_bytes(b"sample source")
            output.write_text(original, encoding="utf-8")

            markitdown = ModuleType("markitdown")
            converter_factory = Mock()
            markitdown.MarkItDown = converter_factory
            message = io.StringIO()

            with (
                patch.dict("sys.modules", {"markitdown": markitdown}),
                patch.object(ingest, "call_llm") as call_llm,
                redirect_stdout(message),
            ):
                ingest.ingest(str(source))
                self.assertEqual(output.read_text(encoding="utf-8"), original)
                self.assertTrue(source.exists())
                self.assertIn("already exists", message.getvalue())
                self.assertIn("leaving it unchanged", message.getvalue())
                self.assertNotIn("Ingesting:", message.getvalue())
                converter_factory.assert_not_called()
                call_llm.assert_not_called()

    def test_new_destination_is_written_by_converter(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "paper.pdf"
            source.write_bytes(b"sample source")
            output = source.with_suffix(".md")

            converter = Mock()
            converter.convert.return_value = SimpleNamespace(
                text_content="# Converted content\n"
            )
            markitdown = ModuleType("markitdown")
            markitdown.MarkItDown = Mock(return_value=converter)
            message = io.StringIO()

            with (
                patch.dict("sys.modules", {"markitdown": markitdown}),
                redirect_stdout(message),
            ):
                converted = ingest.convert_to_md(source)
                self.assertEqual(converted, output)
                self.assertEqual(
                    output.read_text(encoding="utf-8"), "# Converted content\n"
                )
                converter.convert.assert_called_once_with(str(source))


if __name__ == "__main__":
    unittest.main()
