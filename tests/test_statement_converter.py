import os
import unittest
from statement_converter import extract_tables, _group_by_month, convert_statement
from docx import Document

class TestStatementConverter(unittest.TestCase):
    def setUp(self):
        self.docx_path = 'sample_statement.docx'
        doc = Document()
        table = doc.add_table(rows=1, cols=3)
        cells = table.rows[0].cells
        cells[0].text = '2024-01-01'
        cells[1].text = 'Opening'
        cells[2].text = '100'
        row = table.add_row().cells
        row[0].text = '2024-01-15'
        row[1].text = 'Purchase'
        row[2].text = '-20'
        row = table.add_row().cells
        row[0].text = '2024-02-05'
        row[1].text = 'Deposit'
        row[2].text = '50'
        doc.save(self.docx_path)

    def tearDown(self):
        if os.path.exists(self.docx_path):
            os.remove(self.docx_path)
        if os.path.exists('out.pdf'):
            os.remove('out.pdf')

    def test_extract_and_group(self):
        rows = extract_tables(self.docx_path)
        grouped = _group_by_month(rows)
        self.assertIn('2024-01', grouped)
        self.assertIn('2024-02', grouped)

    def test_convert_statement(self):
        convert_statement(self.docx_path, 'out.pdf')
        self.assertTrue(os.path.exists('out.pdf'))

if __name__ == '__main__':
    unittest.main()
