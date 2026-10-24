from pathlib import Path
from typing import List, Dict, Any, Optional
import os
import re

class DocumentChunk:
    def __init__(self, content: str, metadata: Dict[str, Any]):
        self.page_content = content
        self.metadata = metadata

class PolicyDocumentLoader:
    """Loads policy documents in Markdown, TXT, PDF, or DOCX formats."""
    
    @staticmethod
    def load_document(file_path: Path) -> List[DocumentChunk]:
        if not file_path.exists():
            raise FileNotFoundError(f"Policy document not found at: {file_path}")
            
        file_size = file_path.stat().st_size
        if file_size == 0:
            raise ValueError(f"Policy document at {file_path} is empty (0 bytes).")
            
        ext = file_path.suffix.lower()
        
        if ext in [".md", ".markdown", ".txt"]:
            return PolicyDocumentLoader._load_text_or_markdown(file_path)
        elif ext == ".pdf":
            return PolicyDocumentLoader._load_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            return PolicyDocumentLoader._load_docx(file_path)
        else:
            raise ValueError(f"Unsupported document format: {ext}. Supported formats: .md, .txt, .pdf, .docx")

    @staticmethod
    def _load_text_or_markdown(file_path: Path) -> List[DocumentChunk]:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read().strip()
            
        if not content:
            raise ValueError(f"Document {file_path.name} contains no readable text.")
            
        filename = file_path.name
        return [DocumentChunk(content=content, metadata={"source": filename, "page": None})]

    @staticmethod
    def _load_pdf(file_path: Path) -> List[DocumentChunk]:
        chunks = []
        filename = file_path.name
        try:
            import pypdf
            reader = pypdf.PdfReader(str(file_path))
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    chunks.append(DocumentChunk(content=text.strip(), metadata={"source": filename, "page": i + 1}))
        except Exception as e:
            # Fallback to fitz (PyMuPDF) if pypdf has issues
            try:
                import fitz
                doc = fitz.open(str(file_path))
                for i, page in enumerate(doc):
                    text = page.get_text() or ""
                    if text.strip():
                        chunks.append(DocumentChunk(content=text.strip(), metadata={"source": filename, "page": i + 1}))
            except Exception:
                raise RuntimeError(f"Failed to read PDF document {file_path}: {e}")
                
        if not chunks:
            raise ValueError(f"No text could be extracted from PDF {file_path.name}")
        return chunks

    @staticmethod
    def _load_docx(file_path: Path) -> List[DocumentChunk]:
        filename = file_path.name
        try:
            import docx
            doc = docx.Document(str(file_path))
            full_text = "\n\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            if not full_text.strip():
                raise ValueError("Docx contains no text.")
            return [DocumentChunk(content=full_text, metadata={"source": filename, "page": None})]
        except Exception as e:
            raise RuntimeError(f"Failed to read DOCX document {file_path}: {e}")
