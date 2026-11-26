"""Embedding provider: Gemini if an API key exists, else a local offline fallback."""
import hashlib
import re

import numpy as np

from config import GEMINI_API_KEY, EMBED_MODEL

LOCAL_DIM = 512


class LocalEmbedder:
    """Hashed bag-of-words embedder. No API or internet needed (for dev/demo fallback)."""
    name = "local"

    def _vec(self, text):
        v = np.zeros(LOCAL_DIM, dtype="float32")
        for tok in re.findall(r"[a-z0-9_]+", text.lower()):
            v[int(hashlib.md5(tok.encode()).hexdigest(), 16) % LOCAL_DIM] += 1.0
        n = np.linalg.norm(v)
        return (v / n if n else v).tolist()

    def embed_documents(self, texts):
        return [self._vec(t) for t in texts]

    def embed_query(self, text):
        return self._vec(text)


class GeminiEmbedder:
    name = "gemini"

    def __init__(self, api_key):
        from google import genai
        self.client = genai.Client(api_key=api_key)

    def _embed(self, texts, task):
        from google.genai import types
        out = []
        for i in range(0, len(texts), 50):  # batch to respect API limits
            res = self.client.models.embed_content(
                model=EMBED_MODEL, contents=texts[i:i + 50],
                config=types.EmbedContentConfig(task_type=task))
            out += [e.values for e in res.embeddings]
        return out

    def embed_documents(self, texts):
        return self._embed(texts, "RETRIEVAL_DOCUMENT")

    def embed_query(self, text):
        return self._embed([text], "RETRIEVAL_QUERY")[0]


def get_embedder(force_local=False):
    if GEMINI_API_KEY and not force_local:
        return GeminiEmbedder(GEMINI_API_KEY)
    return LocalEmbedder()
