import re
from typing import List, Dict, Any
from app.rag.document_loader import DocumentChunk

class SectionAwareTextSplitter:
    """Splits markdown and text documents while preserving section headers and semantic coherence."""
    
    def __init__(self, chunk_size: int = 650, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_documents(self, documents: List[DocumentChunk], doc_hash: str) -> List[DocumentChunk]:
        all_chunks: List[DocumentChunk] = []
        chunk_counter = 0

        for doc in documents:
            text = doc.page_content
            source = doc.metadata.get("source", "airline_policy.md")
            page = doc.metadata.get("page")

            # Split by markdown top/sub-level headings: #, ##, ###
            sections = self._split_by_headings(text)

            for sec_title, sec_text in sections:
                # If section text is within chunk size, keep it as a clean cohesive chunk
                if len(sec_text) <= self.chunk_size:
                    chunk_counter += 1
                    metadata = {
                        "source": source,
                        "section": sec_title,
                        "page": page,
                        "chunk_id": f"chunk_{chunk_counter}",
                        "chunk_index": chunk_counter - 1,
                        "doc_hash": doc_hash,
                    }
                    all_chunks.append(DocumentChunk(content=sec_text.strip(), metadata=metadata))
                else:
                    # Further split large section into sub-chunks with overlap
                    sub_chunks = self._recursive_split(sec_text, self.chunk_size, self.chunk_overlap)
                    for sub in sub_chunks:
                        if not sub.strip():
                            continue
                        chunk_counter += 1
                        metadata = {
                            "source": source,
                            "section": sec_title,
                            "page": page,
                            "chunk_id": f"chunk_{chunk_counter}",
                            "chunk_index": chunk_counter - 1,
                            "doc_hash": doc_hash,
                        }
                        # Prepend section context if not already present
                        formatted_content = sub.strip()
                        if not formatted_content.startswith(f"[{sec_title}]"):
                            formatted_content = f"[{sec_title}]\n{formatted_content}"
                        all_chunks.append(DocumentChunk(content=formatted_content, metadata=metadata))

        return all_chunks

    def _split_by_headings(self, text: str) -> List[tuple[str, str]]:
        """Splits markdown text into (heading_title, section_body) pairs."""
        pattern = r"(^#{1,3}\s+[^\n]+)"
        tokens = re.split(pattern, text, flags=re.MULTILINE)
        
        sections: List[tuple[str, str]] = []
        current_title = "General Policy Overview"
        current_body = ""

        for token in tokens:
            stripped = token.strip()
            if not stripped:
                continue
            if re.match(r"^#{1,3}\s+", stripped):
                # We reached a new heading
                if current_body.strip():
                    sections.append((current_title, current_body.strip()))
                current_title = re.sub(r"^#{1,3}\s+", "", stripped)
                current_body = ""
            else:
                current_body += "\n" + token

        if current_body.strip():
            sections.append((current_title, current_body.strip()))

        return sections if sections else [("General", text)]

    def _recursive_split(self, text: str, max_size: int, overlap: int) -> List[str]:
        """Splits text recursively by double newline, single newline, or sentence."""
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = []
        current_len = 0

        for p in paragraphs:
            p_len = len(p)
            if current_len + p_len + 2 > max_size and current_chunk:
                joined = "\n\n".join(current_chunk)
                chunks.append(joined)
                
                # Keep tail for overlap if possible
                overlap_text = current_chunk[-1] if len(current_chunk[-1]) < overlap else ""
                current_chunk = [overlap_text, p] if overlap_text else [p]
                current_len = sum(len(x) for x in current_chunk) + 2
            else:
                current_chunk.append(p)
                current_len += p_len + 2

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        # Check if any chunk still exceeds max_size (e.g. giant paragraph)
        refined_chunks = []
        for c in chunks:
            if len(c) > max_size:
                lines = c.split("\n")
                temp = ""
                for line in lines:
                    if len(temp) + len(line) + 1 > max_size:
                        if temp:
                            refined_chunks.append(temp)
                        temp = line
                    else:
                        temp = (temp + "\n" + line).strip()
                if temp:
                    refined_chunks.append(temp)
            else:
                refined_chunks.append(c)

        return refined_chunks
