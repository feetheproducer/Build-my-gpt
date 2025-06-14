import os
import json
import unittest

from questionnaire import load_questions, administer_quiz


class TestQuestionnaire(unittest.TestCase):
    def setUp(self):
        self.qfile = 'sample_questions.json'
        data = [
            {"prompt": "Capital of France?", "answer": "Paris"},
            {"prompt": "2+2?", "answer": "4", "options": ["3", "4", "5"]},
        ]
        with open(self.qfile, 'w') as f:
            json.dump(data, f)

    def tearDown(self):
        if os.path.exists(self.qfile):
            os.remove(self.qfile)

    def test_load_questions(self):
        questions = load_questions(self.qfile)
        self.assertEqual(len(questions), 2)
        self.assertEqual(questions[0].prompt, "Capital of France?")

    def test_administer_quiz(self):
        questions = load_questions(self.qfile)
        score = administer_quiz(questions, provided_answers=["Paris", "4"])
        self.assertEqual(score, 2)


if __name__ == '__main__':
    unittest.main()
