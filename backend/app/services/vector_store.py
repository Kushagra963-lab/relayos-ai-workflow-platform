import os
from math import sqrt
from typing import Any


class VectorStore:
    def __init__(self) -> None:
        self.collection = None
        self.enabled = False
        self.error: str | None = None
        self._connect()

    def add_document(self, document_id: str, text: str, metadata: dict[str, Any]) -> str:
        if not self.enabled or self.collection is None or not text.strip():
            return "chroma:skipped"

        safe_metadata = {
            key: value
            for key, value in metadata.items()
            if isinstance(value, str | int | float | bool) or value is None
        }
        self.collection.upsert(
            ids=[document_id],
            documents=[text[:12000]],
            embeddings=[_simple_embedding(text)],
            metadatas=[safe_metadata],
        )
        return "chroma:indexed"

    def _connect(self) -> None:
        try:
            import chromadb

            path = os.getenv("CHROMA_PATH", "./data/chroma")
            client = chromadb.PersistentClient(path=path)
            self.collection = client.get_or_create_collection("business_documents")
            self.enabled = True
        except Exception as exc:
            self.enabled = False
            self.error = str(exc)


def _simple_embedding(text: str, dimensions: int = 64) -> list[float]:
    values = [0.0] * dimensions
    for index, char in enumerate(text.lower()[:8000]):
        values[index % dimensions] += (ord(char) % 31) / 31

    norm = sqrt(sum(value * value for value in values)) or 1.0
    return [value / norm for value in values]
