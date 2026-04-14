import os

import pdfplumber


def load_pdf_text(pdf_path: str) -> str:
    if not os.path.exists(pdf_path):
        return ""
    pages: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text() or "")
    return "\n".join(pages)


def load_faq_text(faq_path: str) -> str:
    if not os.path.exists(faq_path):
        return ""
    with open(faq_path, "r", encoding="utf-8") as f:
        return f.read()
