"""Heading-aware chunking with overlap."""
import re
from config import CHUNK_SIZE, CHUNK_OVERLAP


def _split_long(text, size, overlap):
    if len(text) <= size:
        return [text]
    parts, start = [], 0
    while start < len(text):
        parts.append(text[start:start + size])
        start += size - overlap
    return parts


def chunk_markdown(text: str, source: str):
    """Split on markdown headings first (keeps topics intact), then by size."""
    sections = re.split(r"\n(?=#{1,3} )", text)
    chunks = []
    for sec in sections:
        sec = sec.strip()
        if not sec:
            continue
        title = sec.splitlines()[0].lstrip("# ").strip()
        for i, piece in enumerate(_split_long(sec, CHUNK_SIZE, CHUNK_OVERLAP)):
            chunks.append({"text": piece, "source": source, "section": title, "part": i})
    return chunks
