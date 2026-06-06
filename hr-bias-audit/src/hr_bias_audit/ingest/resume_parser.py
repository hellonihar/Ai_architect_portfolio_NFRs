import re
from pathlib import Path
from uuid import uuid4

from hr_bias_audit.models.resume import ResumeProfile


class ResumeParser:

    @staticmethod
    def extract_text(filepath: str) -> str:
        path = Path(filepath)
        suffix = path.suffix.lower()

        if suffix == ".txt":
            return path.read_text(encoding="utf-8", errors="ignore")

        if suffix == ".pdf":
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(str(path))
                return "\n".join(
                    page.extract_text() or "" for page in reader.pages
                )
            except ImportError:
                return f"[PDF parser unavailable: {path.name}]"

        if suffix == ".docx":
            try:
                from docx import Document
                doc = Document(str(path))
                return "\n".join(p.text for p in doc.paragraphs)
            except ImportError:
                return f"[DOCX parser unavailable: {path.name}]"

        return ""

    @staticmethod
    def parse(filepath: str) -> ResumeProfile:
        raw = ResumeParser.extract_text(filepath)
        name = Path(filepath).stem
        lines = [l.strip() for l in raw.split("\n") if l.strip()]
        email = ""
        for line in lines:
            m = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", line)
            if m:
                email = m.group()
                break

        return ResumeProfile(
            id=str(uuid4()),
            name=name,
            email=email,
            raw_text=raw,
            skills=[],
            source=filepath,
        )
