"""Knowledge-base ingestion: load -> chunk -> embed -> index."""
from config import KB_DIR
from rag.chunking import chunk_markdown
from rag.embeddings import get_embedder
from rag.vector_store import VectorStore


def build_index(force_local=False, reset=True):
    embedder = get_embedder(force_local)
    store = VectorStore(embedder)
    if reset:
        store.reset()
    chunks = []
    for f in sorted(KB_DIR.glob("*.md")):
        chunks += chunk_markdown(f.read_text(encoding="utf-8"), f.name)
    store.add_chunks(chunks)
    return {"provider": embedder.name, "files": len(list(KB_DIR.glob('*.md'))),
            "chunks": len(chunks), "indexed": store.count()}


def get_store(force_local=False):
    return VectorStore(get_embedder(force_local))
