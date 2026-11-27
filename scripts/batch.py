"""Process every PDF in a folder.  Usage: python batch.py sample_data"""
import argparse
import json
import sys
from pathlib import Path

import requests

from src.export import save_excel
from src.llm import DEFAULT_MODEL
from src.pipeline import process_file


def main():
    parser = argparse.ArgumentParser(description="Extract invoice data from PDFs")
    parser.add_argument("folder", help="folder that contains PDF files")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--out", default="output")
    args = parser.parse_args()

    files = sorted(p for p in Path(args.folder).glob("*")
                   if p.suffix.lower() == ".pdf")
    if not files:
        sys.exit(f"No PDF files found in {args.folder}")

    results = []
    for number, path in enumerate(files, 1):
        print(f"[{number}/{len(files)}] {path.name} ...", flush=True)
        try:
            result = process_file(path.name, path, args.model)
        except requests.RequestException as error:
            sys.exit(f"Could not use Ollama: {error}\n"
                     f"Check that Ollama is running and run: ollama pull {args.model}")
        print(f"    {result['status']}")
        results.append(result)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "invoices.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    save_excel(results, out / "invoices.xlsx")
    print(f"Done. Reports saved in the '{out}' folder.")


if __name__ == "__main__":
    main()
