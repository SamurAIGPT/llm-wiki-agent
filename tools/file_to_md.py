import argparse
from tqdm import tqdm
from pathlib import Path
from markitdown import MarkItDown


def convert_directory_to_md(input_dir: Path, delete_source: bool = False, overwrite: bool = False):
    """
    Converts all non-Markdown files in a directory tree to Markdown.

    Safety: an output path is never silently overwritten. If a sibling ``.md``
    with the same stem already exists the file is skipped (unless ``overwrite``
    is set), the source is never deleted on a skip, and the run reports the
    skip explicitly so data loss cannot pass unnoticed.

    :param input_dir: Path
        The Path object pointing to the directory to process.
    :param delete_source: bool = False
        Whether to delete the original source files after a successful
        conversion. Defaults to False.
    :param overwrite: bool = False
        Whether to overwrite an already-existing ``<stem>.md`` output.
        Defaults to False.
    """

    md = MarkItDown(enable_plugins=False)

    # get list of files to convert
    files_to_process = [f for f in input_dir.rglob('*') if f.is_file()]

    if not files_to_process:
        print(f"No files found in {input_dir}!")
        return

    skipped_collision = 0
    converted = 0

    for file_path in tqdm(files_to_process, desc="Converting Files"):
        # skip hidden files and existing markdown files (as conversion sources)
        if file_path.name.startswith('.') or file_path.suffix.lower() == '.md':
            print(f"Skipping conversion of {file_path.name}")
            continue

        # derive the output path from the source stem
        output_path = file_path.with_suffix(".md")

        # guard the output side: never silently overwrite a sibling .md.
        # The source is NOT deleted on a collision, so both the pre-existing
        # markdown and the original file survive.
        if output_path.exists() and not overwrite:
            tqdm.write(
                f"SKIPPED: '{output_path.name}' already exists; "
                f"not overwriting '{file_path.name}'."
            )
            skipped_collision += 1
            continue

        try:
            # convert
            result = md.convert(str(file_path))
            # save to .md
            output_path.write_text(result.text_content, encoding="utf-8")
            # optional remove original file (only after a successful write)
            if delete_source:
                file_path.unlink()
            tqdm.write(f"Converted: {file_path.name}")
            converted += 1
        except Exception as e:
            tqdm.write(f"FAILED: Could not convert '{file_path.name}'. Reason: {e}")

    # summary so skipped collisions are visible at the end of the run
    print("-" * 40)
    print(f"Converted: {converted}")
    print(f"Skipped (output exists): {skipped_collision}")
    print("-" * 40)


def main(args):
    # set Paths
    input_path = Path(args.input_dir).resolve()
    print("-" * 40)
    print(f"Input Directory: {input_path}")
    print(f"Overwrite existing .md: {args.overwrite}")
    print("-" * 40)

    # execute
    try:
        convert_directory_to_md(input_path, args.delete_source, args.overwrite)
        print("\nConversion process complete.")
    except FileNotFoundError:
        print(f"\nError: Input directory not found at {input_path}")
    except Exception as e:
        print(f"\nAn unexpected error occurred during execution: {e}")


if __name__ == "__main__":
    """Command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert all non-Markdown files in a directory to Markdown."
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        help="The path to the directory containing files to convert."
    )
    parser.add_argument(
        "--delete_source",
        action="store_true",
        help="Whether to delete the original source files after conversion."
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite an already-existing <stem>.md output. "
             "Without this flag, collisions are skipped and logged."
    )
    args = parser.parse_args()

    main(args)
