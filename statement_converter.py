"""Convert tabular statements from .docx files into monthly PDF reports."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime
from typing import Iterable, List

from docx import Document
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas


DateRow = List[str]


def _parse_date(value: str) -> datetime | None:
    """Try parsing a date from common formats."""
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            continue
    return None


def extract_tables(path: str) -> List[DateRow]:
    """Extract rows from all tables in a docx file."""
    document = Document(path)
    rows: List[DateRow] = []
    for table in document.tables:
        for row in table.rows:
            cells = [c.text.strip() for c in row.cells]
            if any(cells):
                rows.append(cells)
    return rows


def _group_by_month(rows: Iterable[DateRow]) -> dict[str, List[DateRow]]:
    """Group table rows by month extracted from the first column."""
    grouped: dict[str, List[DateRow]] = defaultdict(list)
    for row in rows:
        if not row:
            continue
        dt = _parse_date(row[0])
        if not dt:
            continue
        key = dt.strftime("%Y-%m")
        grouped[key].append(row)
    return grouped


def _amount_from_cell(value: str) -> float:
    """Convert an amount string to float, ignoring currency symbols."""
    try:
        cleaned = value.replace(",", "").replace("$", "").strip()
        return float(cleaned)
    except ValueError:
        return 0.0


def draw_pdf(rows: Iterable[DateRow], output: str) -> None:
    """Render grouped rows to a PDF with running balances."""
    grouped = _group_by_month(rows)
    c = canvas.Canvas(output, pagesize=LETTER)
    width, height = LETTER
    balance = 0.0

    for month in sorted(grouped.keys()):
        y = height - 50
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, f"Statement for {month}")
        y -= 30
        c.setFont("Helvetica", 10)
        c.drawString(50, y, "Date")
        c.drawString(150, y, "Description")
        c.drawRightString(400, y, "Amount")
        c.drawRightString(500, y, "Balance")
        y -= 20

        for row in grouped[month]:
            if y < 50:
                c.showPage()
                y = height - 50
            date = row[0]
            desc = row[1] if len(row) > 1 else ""
            amount = _amount_from_cell(row[2]) if len(row) > 2 else 0.0
            balance += amount
            c.drawString(50, y, date)
            c.drawString(150, y, desc[:40])
            c.drawRightString(400, y, f"{amount:,.2f}")
            c.drawRightString(500, y, f"{balance:,.2f}")
            y -= 15
        c.showPage()

    c.save()


def convert_statement(docx_path: str, pdf_path: str) -> None:
    """High level helper to read a docx file and create a PDF statement."""
    rows = extract_tables(docx_path)
    draw_pdf(rows, pdf_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a docx statement to PDF")
    parser.add_argument("input", help="Input .docx file")
    parser.add_argument("-o", "--output", default="statement.pdf", help="Output PDF path")
    args = parser.parse_args()
    convert_statement(args.input, args.output)


if __name__ == "__main__":
    main()
