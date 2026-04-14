import os
from dataclasses import dataclass

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS


@dataclass
class SimpleRetriever:
    chunks: list[str]

    def query(self, text: str, k: int = 4) -> list[str]:
        scored = []
        q = set(text.lower().split())
        for c in self.chunks:
            words = set(c.lower().split())
            score = len(q.intersection(words))
            scored.append((score, c))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored[:k] if c]


def build_chunks(text: str) -> list[str]:
    if not text.strip():
        return []
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    return splitter.split_text(text)


def build_retriever(chunks: list[str], embeddings=None):
    if not chunks:
        return SimpleRetriever(chunks=[])
    if embeddings is None:
        return SimpleRetriever(chunks=chunks)
    db = FAISS.from_texts(chunks, embedding=embeddings)
    return db.as_retriever(search_kwargs={"k": 4})
