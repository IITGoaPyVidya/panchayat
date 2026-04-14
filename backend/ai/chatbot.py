import os
from typing import Any

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from sqlalchemy.orm import Session

from .document_loader import load_faq_text, load_pdf_text
from .vector_store import SimpleRetriever, build_chunks, build_retriever
from ..models import Contact, Rulebook


class SocietyChatbot:
    def __init__(self, db: Session):
        self.db = db
        self.name = "SocietyBot 🏠"
        self.model = None
        self.embeddings = None

        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            self.embeddings = OpenAIEmbeddings()

        text = self._collect_knowledge()
        chunks = build_chunks(text)
        self.retriever = build_retriever(chunks, self.embeddings)

    def _collect_knowledge(self) -> str:
        sections: list[str] = []
        contacts = self.db.query(Contact).all()
        if contacts:
            sections.append("Contacts:\n" + "\n".join(f"{c.category}: {c.name} - {c.phone}" for c in contacts))

        rb = self.db.query(Rulebook).order_by(Rulebook.updated_at.desc()).first()
        if rb:
            sections.append(f"Key Rules:\n{rb.key_rules_text}")
            full_path = rb.file_path.replace("/uploads/", "")
            upload_dir = os.getenv("UPLOAD_DIR", "./data/uploads")
            sections.append(load_pdf_text(os.path.join(upload_dir, full_path)))

        sections.append(load_faq_text("./data/faq.txt"))
        return "\n\n".join([s for s in sections if s])

    def ask(self, question: str, history: list[dict[str, str]] | None = None) -> str:
        history = history or []
        context = []
        if hasattr(self.retriever, "invoke"):
            docs = self.retriever.invoke(question)
            context = [d.page_content for d in docs]
        elif isinstance(self.retriever, SimpleRetriever):
            context = self.retriever.query(question)

        prompt = (
            "You are SocietyBot 🏠, a friendly and concise assistant for a residential society app.\n"
            "Answer using the provided context. If missing, clearly say information is unavailable.\n"
            f"Context:\n{'\n---\n'.join(context)}\n\n"
            f"Recent chat: {history[-6:]}\n"
            f"Question: {question}"
        )

        if not self.model:
            if context:
                return f"SocietyBot 🏠: Based on available records, here's what I found:\n\n{context[0][:900]}"
            return "SocietyBot 🏠: I couldn't find this in current rulebook/contacts/FAQ data. Please ask admin to update records."

        response = self.model.invoke(prompt)
        return response.content
