import sys
from pathlib import Path
from typing import List

import pandas as pd
from docx import Document
import fitz  # PyMuPDF
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle


def load_transactions(docx_path: Path) -> List[pd.DataFrame]:
    """Parse tables from the docx file into a list of DataFrames."""
    doc = Document(str(docx_path))
    months = []
    for table in doc.tables:
        headers = [cell.text.strip() for cell in table.rows[0].cells]
        rows = [[cell.text.strip() for cell in row.cells] for row in table.rows[1:]]
        df = pd.DataFrame(rows, columns=headers)
        months.append(df)
    return months


def compute_balances(months: List[pd.DataFrame], starting_balance: float = 0.0) -> List[pd.DataFrame]:
    """Add running balance column to each month."""
    balance = starting_balance
    processed = []
    for df in months:
        df = df.copy()
        df['Amount'] = df['Amount'].astype(float)
        if 'Type' in df.columns:
            debit_mask = df['Type'].str.contains('debit', case=False)
            df.loc[debit_mask, 'Amount'] *= -1
        df['Balance'] = balance + df['Amount'].cumsum()
        balance = df['Balance'].iloc[-1]
        processed.append(df)
    return processed


def draw_month(c: canvas.Canvas, df: pd.DataFrame, title: str, page_width: int, page_height: int):
    c.setFont('Helvetica-Bold', 12)
    c.drawString(0.5 * inch, page_height - 0.75 * inch, 'Play Runners Music Group LLC')
    c.drawString(0.5 * inch, page_height - inch, title)
    data = [['Date', 'Description', 'Amount', 'Type', 'Balance']]
    for _, row in df.iterrows():
        data.append([
            row['Date'],
            row['Description'],
            f"{row['Amount']:.2f}",
            row['Type'],
            f"{row['Balance']:.2f}",
        ])
    table = Table(data, colWidths=[1.2 * inch, 3 * inch, 1 * inch, 1 * inch, 1.2 * inch])
    style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (2, 1), (4, -1), 'RIGHT'),
    ])
    table.setStyle(style)
    table.wrapOn(c, page_width - inch, page_height - 2 * inch)
    table_height = table._height
    table.drawOn(c, 0.5 * inch, page_height - 1.25 * inch - table_height)


def generate_pdf(months: List[pd.DataFrame], output_path: Path):
    c = canvas.Canvas(str(output_path), pagesize=letter)
    width, height = letter
    for i, df in enumerate(months):
        if i:
            c.showPage()
        month_name = pd.to_datetime(df['Date'].iloc[0]).strftime('%B %Y')
        draw_month(c, df, f'Statement for {month_name}', width, height)
    c.save()


def main():
    if len(sys.argv) < 3:
        print('Usage: python statement_converter.py <transactions.docx> <output.pdf> [starting_balance]')
        return
    docx_path = Path(sys.argv[1])
    output_pdf = Path(sys.argv[2])
    starting_balance = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0

    months = load_transactions(docx_path)
    months = compute_balances(months, starting_balance)
    generate_pdf(months, output_pdf)
    print(f'Created {output_pdf}')


if __name__ == '__main__':
    main()
