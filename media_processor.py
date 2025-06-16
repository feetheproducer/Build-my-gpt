"""Utility for handling text, audio and video files.

This module provides a basic command line interface that delegates text
summarization to `summarizer.py` and stubs out handling for audio and video
files. It is intentionally lightweight so it can run without installing extra
packages.
"""

from __future__ import annotations

import argparse
import os

from summarizer import summarize_file

try:
    import librosa
    import numpy as np
except Exception:  # pragma: no cover - handled in tests
    librosa = None  # type: ignore
    np = None  # type: ignore


def process_text_file(path: str) -> str:
    """Summarize a text file using the existing summarizer."""
    return summarize_file(path)


NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def _hz_to_note_name(hz: float) -> str | None:
    """Convert frequency in Hz to a note name like C4."""
    if hz <= 0 or np is None:
        return None
    note_num = 12 * np.log2(hz / 440.0) + 69
    index = int(round(note_num))
    name = NOTE_NAMES[index % 12]
    octave = index // 12 - 1
    return f"{name}{octave}"


def _extract_notes(path: str) -> list[str]:
    """Extract a sequence of note names from an audio file."""
    if librosa is None or np is None:
        return []
    y, sr = librosa.load(path)
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    notes: list[str] = []
    for i in range(pitches.shape[1]):
        index = magnitudes[:, i].argmax()
        pitch = pitches[index, i]
        name = _hz_to_note_name(float(pitch))
        if name:
            notes.append(name)
    return notes


OPEN_MIDI = {"E2": 40, "A2": 45, "D3": 50, "G3": 55, "B3": 59, "E4": 64}


def _note_name_to_midi(note: str) -> int:
    if np is None:
        return 0
    match = __import__("re").match(r"([A-G]#?)(-?\d+)", note)
    if not match:
        return 0
    name, octave = match.groups()
    semitone = NOTE_NAMES.index(name)
    octave = int(octave)
    return semitone + (octave + 1) * 12


def _notes_to_tab(notes: list[str]) -> str:
    """Convert note names to a simple guitar tab representation."""
    lines = [[] for _ in range(6)]
    open_notes = list(OPEN_MIDI.values())
    for note in notes:
        midi = _note_name_to_midi(note)
        best_string = 0
        best_fret = 1000
        for idx, open_midi in enumerate(open_notes):
            fret = midi - open_midi
            if 0 <= fret < best_fret:
                best_fret = fret
                best_string = idx
        for idx in range(6):
            if idx == best_string:
                lines[5 - idx].append(str(best_fret))
            else:
                lines[5 - idx].append("-")
    return "\n".join("".join(l) for l in lines)


def _notes_to_notation(notes: list[str], clef: str = "treble") -> str:
    """Return a very naive text notation of notes."""
    return f"Clef: {clef}\n" + " ".join(notes)


def process_audio_file(path: str, response: str = "notation", clef: str = "treble") -> str:
    """Transcribe audio to notes and format as notation or tab."""
    if response not in {"notation", "tab"}:
        raise ValueError("response must be 'notation' or 'tab'")
    notes = _extract_notes(path)
    if response == "tab":
        return _notes_to_tab(notes)
    return _notes_to_notation(notes, clef)


def process_video_file(path: str) -> str:
    """Return a stub response for video files."""
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
    parser.add_argument("--clef", choices=["treble", "bass"], default="treble",
                        help="Clef to use when returning notation")
    args = parser.parse_args()

    file_type = infer_type(args.path)
    if file_type == "text":
        result = process_text_file(args.path)
    elif file_type == "audio":
        result = process_audio_file(args.path, args.audio_response, args.clef)
    else:
        result = process_video_file(args.path)

    print(result)


if __name__ == "__main__":
    main()
