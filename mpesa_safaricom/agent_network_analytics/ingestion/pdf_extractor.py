"""
pdf_extractor.py

Extract agent transaction tables from CBK agent-banking PDF files
placed in data/cbk/.  Uses pdfplumber to pull text tables with
auto-dictated headers, then writes each page / table as a CSV file
into data/cbk so cbk_loader.py can ingest them.

Usage
-----
    python ingestion/pdf_extractor.py                   # all PDFs
    python ingestion/pdf_extractor.py --dir /path/to/cbk # specific dir
"""
import os
import glob
import logging
import argparse
from pathlib import Path

import pandas as pd
import pdfplumber

from sqlalchemy.engine import Engine, create_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_DIR = (Path(__file__).resolve().parents[1] / 'data' / 'cbk')


def extract_tables(pdf_path: str, out_dir: Path) -> list[Path]:
    """
    Extract every table found in *pdf_path* with pdfplumber and
    save each one as a CSV inside *out_dir*.

    Returns
    -------
    list[Path]
        Paths of written CSV files.
    """
    written = []
    stem = Path(pdf_path).stem

    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()
            if not tables:
                continue
            for tbl_idx, table in enumerate(tables, start=1):
                if not table or len(table) < 2:
                    continue
                # Find header row: first row with at least 3 non-empty cells
                header_row = None
                for i, row in enumerate(table):
                    non_empty = sum(1 for cell in row if cell and str(cell).strip())
                    if non_empty >= 3:
                        header_row = i
                        break
                if header_row is None or header_row + 1 >= len(table):
                    continue

                raw_headers = table[header_row]
                headers = [
                    str(h).strip().lower() if h else f'col_{i}'
                    for i, h in enumerate(raw_headers)
                ]
                # Deduplicate
                seen: dict[str, int] = {}
                clean_headers = []
                for h in headers:
                    count = seen.get(h, 0)
                    seen[h] = count + 1
                    clean_headers.append(f"{h}" if count == 0 else f"{h}_{count}")

                rows = table[header_row + 1:]
                df = pd.DataFrame(rows, columns=clean_headers)
                out_path = out_dir / f"{stem}_p{page_idx}_t{tbl_idx}.csv"
                df.to_csv(out_path, index=False)
                written.append(out_path)
                logger.info("Wrote %s (%d rows × %d cols)", out_path.name, len(df), len(clean_headers))

    return written


def run(directory: str | Path | None = None) -> None:
    """Extract tables from all PDFs in *directory* (default: data/cbk)."""
    src_dir = Path(directory) if directory else DEFAULT_DIR
    src_dir.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(glob.glob(str(src_dir / "*.pdf")))
    if not pdfs:
        logger.warning("No PDF files found in %s", src_dir)
        return

    all_written: list[Path] = []
    for pdf in pdfs:
        logger.info("Extracting %s ...", pdf)
        written = extract_tables(pdf, src_dir)
        all_written.extend(written)

    logger.info("Done. %d CSV files written from %d PDF files.",
                len(all_written), len(pdfs))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract tables from CBK PDF files")
    parser.add_argument("--dir", default=None, help="Directory containing PDFs (default: data/cbk)")
    args = parser.parse_args()
    run(args.dir)
