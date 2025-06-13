# Build-my-gpt

This repository provides a simple summarization tool capable of processing text
files up to approximately **150 MB**. The summarization logic is implemented in
`summarizer.py` and works completely offline using a basic extractive
algorithm.

A lightweight helper `media_processor.py` is also included for working with
text, audio and video files. Audio input is now transcribed into musical
notation or guitar tab using `librosa`. Install `librosa` and `soundfile` to
enable this functionality. Video support remains a stub.

## Quick Start

1. Place the text you want to summarize in a file.
2. Run the summarizer script:

```bash
python3 summarizer.py path/to/input.txt -o summary.txt
```

Command‑line options allow customizing the chunk size and number of sentences in
the final summary.

### Handling audio and video

Use `media_processor.py` to run the summarizer on text files or to convert
audio into notation or tab. Video files still return stub predictions:

```bash
python3 media_processor.py path/to/file.wav --audio-response notation --clef treble
```

The `--audio-response` option chooses between `notation` and `tab` modes when
processing audio files. Use `--clef treble` or `--clef bass` when requesting
notation to select the clef.

## Running Tests

Automated tests ensure the tools operate correctly. Execute them with:

```bash
python3 -m unittest discover -s tests
```
