"""Utility for handling text, audio and video files.

This module provides a basic command line interface that delegates text
summarization to `summarizer.py` and stubs out handling for audio and video
files. It is intentionally lightweight so it can run without installing extra
packages.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import shutil

from summarizer import summarize_file

try:  # optional dependency for speech to text
    import speech_recognition as sr
except Exception:  # pragma: no cover - optional
    sr = None


def process_text_file(path: str) -> str:
    """Summarize a text file using the existing summarizer."""
    return summarize_file(path)


def process_audio_file(path: str, response: str = "notation") -> str:
    """Transcribe an audio file when speech recognition is available."""
    if response not in {"notation", "tab"}:
        raise ValueError("response must be 'notation' or 'tab'")

    if sr is not None:
        recognizer = sr.Recognizer()
        with sr.AudioFile(path) as source:
            audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_sphinx(audio_data)
        except (sr.UnknownValueError, sr.RequestError):
            text = ""
        return text

    filename = os.path.basename(path)
    return f"[stub] Would generate {response} for {filename}"


def process_video_file(path: str) -> str:
    """Return video duration when ffprobe is available."""
    if shutil.which("ffprobe"):
        try:
            output = subprocess.check_output(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    path,
                ],
                text=True,
                stderr=subprocess.STDOUT,
            )
            duration = float(output.strip())
            return f"Video duration: {duration:.2f} seconds"
        except Exception:
            pass

    filename = os.path.basename(path)
    return f"[stub] Would perform predictive analysis on {filename}"


def infer_type(path: str) -> str:
    """Infer file type based on extension."""
    ext = os.path.splitext(path)[1].lower()
    if ext in {".txt"}:
        return "text"
    if ext in {".wav", ".mp3"}:
        return "audio"
    if ext in {".mp4", ".mov", ".avi"}:
        return "video"
    raise ValueError(f"Unsupported file extension: {ext}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Process text, audio, or video files")
    parser.add_argument("path", help="Path to the input file")
    parser.add_argument("--audio-response", choices=["notation", "tab"], default="notation",
                        help="Response format when processing audio files")
    args = parser.parse_args()

    file_type = infer_type(args.path)
    if file_type == "text":
        result = process_text_file(args.path)
    elif file_type == "audio":
        result = process_audio_file(args.path, args.audio_response)
    else:
        result = process_video_file(args.path)

    print(result)


if __name__ == "__main__":
    main()
