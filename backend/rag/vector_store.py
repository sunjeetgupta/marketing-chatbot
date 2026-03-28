"""ChromaDB vector store — persists to disk locally, uses in-memory on cloud."""
from __future__ import annotations

import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from config import CHROMA_PERSIST_DIR, CHROMA_MODE
from rag.knowledge_base import MARKETING_DOCUMENTS

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "marketing_knowledge"

_embedding_model: SentenceTransformer | None = None
_chroma_client = None
_collection = None


def get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        print(f"Loading embedding model: {EMBEDDING_MODEL}...")
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    return _embedding_model


def get_chroma_client():
    global _chroma_client
    if _chroma_client is None:
        if CHROMA_MODE == "memory":
            _chroma_client = chromadb.EphemeralClient(
                settings=Settings(anonymized_telemetry=False)
            )
        else:
            os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
            _chroma_client = chromadb.PersistentClient(
                path=CHROMA_PERSIST_DIR,
                settings=Settings(anonymized_telemetry=False),
            )
    return _chroma_client


def get_collection():
    global _collection
    if _collection is None:
        client = get_chroma_client()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        if _collection.count() == 0:
            _seed_knowledge_base(_collection)
    return _collection


def _seed_knowledge_base(collection) -> None:
    print(f"Seeding {len(MARKETING_DOCUMENTS)} marketing documents...")
    model = get_embedding_model()
    texts = [doc["content"] for doc in MARKETING_DOCUMENTS]
    embeddings = model.encode(texts, show_progress_bar=False).tolist()
    collection.add(
        ids=[doc["id"] for doc in MARKETING_DOCUMENTS],
        documents=texts,
        embeddings=embeddings,
        metadatas=[{"category": doc["category"]} for doc in MARKETING_DOCUMENTS],
    )
    print("RAG seeded.")


def query_knowledge_base(query: str, n_results: int = 3, category_filter: str | None = None) -> list[str]:
    collection = get_collection()
    model = get_embedding_model()
    query_embedding = model.encode([query]).tolist()
    where = {"category": category_filter} if category_filter else None
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results,
        where=where,
        include=["documents"],
    )
    return results.get("documents", [[]])[0]
