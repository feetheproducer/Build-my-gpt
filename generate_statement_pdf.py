# Script to parse a bank statement docx and generate a monthly PDF
import argparse
from collections import defaultdict
from datetime import datetime
from typing import List, Tuple

from docx import Document
from dateutil import parser as date_parser
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak


Transaction = Tuple[datetime, str, float, str]

def parse_docx_tables(path: str) -> dict[str, List[Transaction]]:
    """Parse tables from the docx and group transactions by month."""
    doc = Document(path)
    months: dict[str, List[Transaction]] = defaultdict(list)
    for table in doc.tables:
        rows = table.rows
        if not rows:
            continue
        # Skip header row assuming standard header
        for row in rows[1:]:
            cells = [c.text.strip() for c in row.cells]
            if len(cells) < 4:
                continue
            date_text, desc, amount_text, ttype = cells[:4]
            try:
                date = date_parser.parse(date_text)
            except (ValueError, TypeError):
                continue
            amount = float(str(amount_text).replace('$', '').replace(',', ''))
            if ttype.lower().startswith('withdraw'):
                amount = -abs(amount)
            month_key = date.strftime('%B %Y')
            months[month_key].append((date, desc, amount, ttype))
    # Sort transactions per month
    for k in months:
        months[k].sort(key=lambda t: t[0])
    return dict(months)

def format_currency(value: float) -> str:
    return f"${value:,.2f}"


def build_pdf(transactions: dict[str, List[Transaction]], output: str, starting_balance: float = 0.0) -> None:
    doc = SimpleDocTemplate(output, pagesize=LETTER)
    styles = getSampleStyleSheet()
    elements = []
    balance = starting_balance
    sorted_months = sorted(transactions.keys(), key=lambda m: datetime.strptime(m, '%B %Y'))
    for i, month in enumerate(sorted_months):
        data = transactions[month]
        elements.append(Paragraph(f"\uD83D\uDCC5 {month}", styles['Heading1']))
        elements.append(Spacer(1, 12))
        table_data = [["Date", "Description", "Amount ($)", "Type"]]
        for date, desc, amount, ttype in data:
            balance += amount
            table_data.append([
                date.strftime('%m/%d/%Y'),
                desc,
                format_currency(abs(amount)),
                ttype
            ])
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Closing Balance: {format_currency(balance)}", styles['Normal']))
        if i < len(sorted_months) - 1:
            elements.append(PageBreak())
    doc.build(elements, onFirstPage=_add_page_number, onLaterPages=_add_page_number)

def _add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 9)
    page_num_text = f"Page {doc.page}"
    canvas.drawRightString(LETTER[0] - 40, 20, page_num_text)
    canvas.drawString(40, 20, "Play Runners Music Group LLC – Business Checking")
    canvas.restoreState()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate monthly PDF statements from a docx file")
    parser.add_argument('docx', help='Input .docx file')
    parser.add_argument('-o', '--output', default='output_statement.pdf', help='Output PDF file')
    parser.add_argument('-b', '--balance', type=float, default=0.0, help='Starting balance')
    args = parser.parse_args()

    months = parse_docx_tables(args.docx)
    build_pdf(months, args.output, args.balance)


if __name__ == '__main__':
    main()
