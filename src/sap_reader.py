import fitz  # PyMuPDF
from docx import Document
import os


class SAPReader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_extension = os.path.splitext(file_path)[1].lower()

    def read(self) -> str:
        if self.file_extension == ".pdf":
            return self._read_pdf()
        elif self.file_extension == ".docx":
            return self._read_docx()
        else:
            raise ValueError(f"Unsupported format: {self.file_extension}")

    def _read_pdf(self) -> str:
        text_parts = []
        try:
            with fitz.open(self.file_path) as doc:
                for page in doc:
                    text_parts.append(page.get_text())
            return "\n".join(text_parts)
        except Exception:
            return ""

    def _read_docx(self) -> str:
        try:
            doc = Document(self.file_path)
            return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        except Exception:
            return ""