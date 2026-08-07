import sys
from pathlib import Path

current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
src_dir = current_dir / "src"
if src_dir.exists() and str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import os
from src.extractor import Extractor
from src.mockshell_generator import MockShellGenerator
from src.exporter import Exporter
from src.sap_reader import SAPReader


def process_sap(file_path, output_dir, selected_tables=None):
    print(f"--- Processing: {file_path.name} ---")
    try:
        reader = SAPReader(str(file_path))
        text = reader.read()

        if not text:
            print(f"Warning: No text could be extracted from {file_path.name}.")
            return

        extractor = Extractor(text)
        tlfs = extractor.extract_tlfs()

        if not tlfs:
            print(f"No TLF patterns found in {file_path.name}.")
            return

        print(f"Extracted {len(tlfs)} raw TLF candidate patterns.")

        generator = MockShellGenerator(tlfs)
        templates = generator.generate_templates(selected_tables=selected_tables)

        exporter = Exporter(templates)
        word_file = exporter.export_to_word(filename=f"MockShells_{file_path.stem}.docx")

        print(f"Success! Mock shells saved to: {os.path.basename(word_file)}")

    except Exception as e:
        print(f"An unexpected error occurred while processing {file_path.name}: {e}")


def main():
    base_dir = Path(__file__).resolve().parent
    input_dir = base_dir / "input"
    output_dir = base_dir / "output"

    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)

    files = [f for f in input_dir.iterdir() if f.suffix.lower() in ('.pdf', '.docx')]

    if not files:
        print(f"No SAP documents found in: {input_dir}")
        return

    for f in files:
        process_sap(f, output_dir)


if __name__ == "__main__":
    main()
