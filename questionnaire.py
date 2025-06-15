"""Simple questionnaire tool for knowledge tests."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Iterable, List, Optional


@dataclass
class Question:
    prompt: str
    answer: str
    options: Optional[List[str]] = None


def load_questions(path: str) -> List[Question]:
    """Load questions from a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Question(**q) for q in data]


def administer_quiz(
    questions: Iterable[Question], provided_answers: Optional[Iterable[str]] = None
) -> int:
    """Ask questions and return the number of correct answers.

    If ``provided_answers`` is given, answers are taken from this iterable
    instead of prompting the user. This makes the function testable.
    """
    score = 0
    answers_iter = iter(provided_answers) if provided_answers is not None else None
    for q in questions:
        if answers_iter is None:
            if q.options:
                opts = " / ".join(f"{i+1}. {o}" for i, o in enumerate(q.options))
                user_input = input(f"{q.prompt} ({opts}) ")
            else:
                user_input = input(f"{q.prompt} ")
        else:
            try:
                user_input = next(answers_iter)
            except StopIteration:
                user_input = ""
        if user_input.strip().lower() == q.answer.strip().lower():
            score += 1
    return score


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a question-based test")
    parser.add_argument("questions", help="Path to questions JSON file")
    args = parser.parse_args()

    questions = load_questions(args.questions)
    score = administer_quiz(questions)
    print(f"You scored {score} out of {len(questions)}")


if __name__ == "__main__":
    main()
