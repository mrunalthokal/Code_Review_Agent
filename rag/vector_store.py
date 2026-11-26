"""ChromaDB persistent vector store. One collection per embedding provider
(different providers produce different vector sizes, so they must not mix)."""
import chromadb

from config import VECTOR_DIR


class VectorStore:
    def __init__(self, embedder):
        self.embedder = embedder
        self.client = chromadb.PersistentClient(path=str(VECTOR_DIR))
        self.name = f"secure_coding_{embedder.name}"
        self.col = self.client.get_or_create_collection(self.name, metadata={"hnsw:space": "cosine"})

    def reset(self):
        self.client.delete_collection(self.name)
        self.col = self.client.get_or_create_collection(self.name, metadata={"hnsw:space": "cosine"})

    def add_chunks(self, chunks):
        texts = [c["text"] for c in chunks]
        self.col.add(
            ids=[f"{c['source']}::{c['section']}::{c['part']}" for c in chunks],
            documents=texts,
            embeddings=self.embedder.embed_documents(texts),
            metadatas=[{"source": c["source"], "section": c["section"]} for c in chunks],
        )

    def count(self):
        return self.col.count()

    def search(self, query, k=4):
        res = self.col.query(query_embeddings=[self.embedder.embed_query(query)], n_results=k)
        return [{"text": d, "source": m["source"], "section": m["section"], "score": round(1 - dist, 3)}
                for d, m, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0])]

