# Build-my-gpt

This repository provides a simple summarization tool capable of processing text
files up to approximately **150 MB**. The summarization logic is implemented in
`summarizer.py` and works completely offline using a basic extractive
algorithm.

## Quick Start

1. Place the text you want to summarize in a file.
2. Run the summarizer script:

```bash
python3 summarizer.py path/to/input.txt -o summary.txt
```

Command‑line options allow customizing the chunk size and number of sentences in
the final summary.

## Running Tests

Automated tests ensure the summarizer operates correctly. Execute them with:

```bash
python3 -m unittest discover -s tests
```
