import os
import unittest
from summarizer import simple_summarize, chunk_file, summarize_file

class TestSummarizer(unittest.TestCase):
    SAMPLE_TEXT = (
        "This is a test document. It contains several sentences. "
        "The summarizer should pick important sentences. "
        "This sentence is less important. Another important point is here."
    )

    def test_simple_summarize_limit(self):
        summary = simple_summarize(self.SAMPLE_TEXT, max_sentences=2)
        self.assertLessEqual(len(summary.split('. ')), 2)

    def test_chunk_file(self):
        path = 'sample.txt'
        with open(path, 'w') as f:
            f.write('abc' * 100)
        chunks = list(chunk_file(path, 50))
        self.assertTrue(all(len(c) <= 50 for c in chunks))
        os.remove(path)

    def test_summarize_file(self):
        path = 'sample_long.txt'
        with open(path, 'w') as f:
            f.write(self.SAMPLE_TEXT * 10)
        summary = summarize_file(path, chunk_size=100)
        self.assertIsInstance(summary, str)
        os.remove(path)

if __name__ == '__main__':
    unittest.main()
