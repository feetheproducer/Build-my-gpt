import re
import heapq
from typing import Iterable
from typing import Optional

try:
    from onedrive_client import OneDriveClient
except ImportError:  # pragma: no cover - optional dependency
    OneDriveClient = None  # type: ignore

# Basic set of stopwords for summarization
STOPWORDS = {
    'the', 'and', 'is', 'in', 'it', 'of', 'to', 'a', 'an', 'that', 'this',
    'for', 'on', 'with', 'as', 'at', 'by', 'from', 'be', 'has', 'have',
}

def chunk_file(path: str, chunk_size: int) -> Iterable[str]:
    """Yield chunks of text from a file."""
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk

def _tokenize_sentences(text: str) -> list[str]:
    return re.split(r'(?<=[.!?])\s+', text.strip())


def _tokenize_words(sentence: str) -> list[str]:
    return re.findall(r'\w+', sentence.lower())


def simple_summarize(text: str, max_sentences: int = 5) -> str:
    """Summarize text by ranking sentence word frequencies."""
    sentences = [s for s in _tokenize_sentences(text) if s]
    word_freq: dict[str, int] = {}
    for sentence in sentences:
        for word in _tokenize_words(sentence):
            if word not in STOPWORDS:
                word_freq[word] = word_freq.get(word, 0) + 1
    sentence_scores = []
    for sentence in sentences:
        score = sum(word_freq.get(word, 0) for word in _tokenize_words(sentence))
        sentence_scores.append((score, sentence))
    top_sentences = [s for _, s in heapq.nlargest(max_sentences, sentence_scores)]
    return ' '.join(top_sentences)

def summarize_file(path: str, chunk_size: int = 5 * 1024 * 1024, max_sentences: int = 5) -> str:
    """Summarize a large text file by chunking and summarizing each chunk."""
    partial_summaries = []
    for chunk in chunk_file(path, chunk_size):
        partial_summaries.append(simple_summarize(chunk, max_sentences))
    return simple_summarize(' '.join(partial_summaries), max_sentences)

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Summarize a text file up to 150 MB.")
    parser.add_argument('input', help='Input text file path')
    parser.add_argument('-o', '--output', help='Output file for summary')
    parser.add_argument('-c', '--chunk-size', type=int, default=5 * 1024 * 1024,
                        help='Chunk size in bytes (default 5MB)')
    parser.add_argument('-n', '--sentences', type=int, default=5,
                        help='Number of sentences in summary')
    parser.add_argument('--onedrive-path', help='Upload summary to this OneDrive path')
    parser.add_argument('--access-token', help='OneDrive OAuth access token')
    args = parser.parse_args()
    summary = summarize_file(args.input, args.chunk_size, args.sentences)
    output_path: Optional[str] = args.output
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as out:
            out.write(summary)
    else:
        if args.onedrive_path:
            import tempfile
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
            output_path = tmp.name
            with open(output_path, 'w', encoding='utf-8') as out:
                out.write(summary)
            print(summary)
        else:
            print(summary)

    if args.onedrive_path:
        if OneDriveClient is None:
            raise RuntimeError('onedrive_client module is required for upload')
        if not args.access_token:
            raise RuntimeError('--access-token is required when using --onedrive-path')
        client = OneDriveClient(args.access_token)
        client.upload_file(output_path, args.onedrive_path)

if __name__ == '__main__':
    main()
