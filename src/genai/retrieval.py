"""Persistent Chroma index with point-in-time filtering before ranking."""
from __future__ import annotations

from datetime import datetime
import hashlib
from pathlib import Path
from zoneinfo import ZoneInfo

from src.common.dates import shift_months


class LocalEmbedder:
    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()


class FilingIndex:
    def __init__(self, path: Path, embedder, *, model_id: str = "test"):
        import chromadb
        namespace = hashlib.sha256(model_id.encode()).hexdigest()[:12]
        self.collection = chromadb.PersistentClient(path=str(path)).get_or_create_collection(f"filing_chunks_{namespace}")
        self.embedder = embedder

    def upsert(self, chunks: list[dict]) -> None:
        if not chunks:
            return
        existing = set(self.collection.get(ids=[c["id"] for c in chunks], include=[])["ids"])
        chunks = [c for c in chunks if c["id"] not in existing]
        if not chunks:
            return
        self.collection.upsert(
            ids=[c["id"] for c in chunks],
            documents=[c["text"] for c in chunks],
            embeddings=self.embedder.encode([c["text"] for c in chunks]),
            metadatas=[{k: v for k, v in c.items() if k not in ("id", "text")} for c in chunks],
        )

    def search(self, query: str, *, ticker: str, cutoff: datetime,
               section: str | None = None, top_k: int = 5,
               lookback_months: int | None = None) -> list[dict]:
        if cutoff.tzinfo is None or top_k < 1:
            raise ValueError("Cutoff must be timezone aware and top_k positive")
        if lookback_months is not None and lookback_months < 1:
            raise ValueError("Lookback months must be positive")
        clauses = [{"ticker": {"$eq": ticker.upper()}},
                   {"first_eligible_epoch": {"$lte": int(cutoff.timestamp())}}]
        if lookback_months is not None:
            local = cutoff.astimezone(ZoneInfo("America/New_York"))
            start = shift_months(local.date(), -lookback_months)
            start_at = datetime.combine(start, datetime.min.time(), ZoneInfo("America/New_York"))
            clauses.append({"first_eligible_epoch": {"$gte": int(start_at.timestamp())}})
        if section:
            clauses.append({"section": {"$eq": section}})
        result = self.collection.query(
            query_embeddings=self.embedder.encode([query]),
            n_results=top_k,
            where={"$and": clauses},
            include=["documents", "metadatas", "distances"],
        )
        return [{"text": text, "metadata": meta, "distance": distance}
                for text, meta, distance in zip(result["documents"][0],
                                                 result["metadatas"][0],
                                                 result["distances"][0])]
