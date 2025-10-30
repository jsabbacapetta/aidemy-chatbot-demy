#!/usr/bin/env python3
"""
Document Processor for Aidemy Chatbot RAG System
Processes documents from Google Drive, chunks them, and prepares for embedding.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

import PyPDF2
from docx import Document
import markdown
from bs4 import BeautifulSoup
import tiktoken
from tqdm import tqdm


class DocumentProcessor:
    """Process documents into chunks for RAG system."""

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        model: str = "gpt-4"
    ):
        """
        Initialize document processor.

        Args:
            chunk_size: Target tokens per chunk
            chunk_overlap: Overlap tokens between chunks
            model: Model name for tiktoken encoding
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.encoding_for_model(model)
        self.documents_dir = Path("/app/documents")
        self.processed_dir = Path("/app/processed")
        self.processed_dir.mkdir(exist_ok=True)

    def extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file."""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error extracting PDF {file_path}: {e}")
        return text

    def extract_text_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file."""
        text = ""
        try:
            doc = Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            print(f"Error extracting DOCX {file_path}: {e}")
        return text

    def extract_text_from_markdown(self, file_path: Path) -> str:
        """Extract text from Markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                md_text = file.read()
                html = markdown.markdown(md_text)
                soup = BeautifulSoup(html, 'html.parser')
                return soup.get_text()
        except Exception as e:
            print(f"Error extracting Markdown {file_path}: {e}")
            return ""

    def extract_text_from_file(self, file_path: Path) -> str:
        """Extract text from file based on extension."""
        extension = file_path.suffix.lower()

        if extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif extension in ['.docx', '.doc']:
            return self.extract_text_from_docx(file_path)
        elif extension in ['.md', '.markdown']:
            return self.extract_text_from_markdown(file_path)
        elif extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            print(f"Unsupported file type: {extension}")
            return ""

    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Chunk text into smaller pieces with overlap.

        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk

        Returns:
            List of chunks with metadata
        """
        # Tokenize the text
        tokens = self.encoding.encode(text)

        chunks = []
        start = 0

        while start < len(tokens):
            # Get chunk
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]

            # Decode back to text
            chunk_text = self.encoding.decode(chunk_tokens)

            # Clean up the chunk
            chunk_text = chunk_text.strip()

            if chunk_text:
                chunk_data = {
                    "text": chunk_text,
                    "metadata": {
                        **metadata,
                        "chunk_index": len(chunks),
                        "token_count": len(chunk_tokens),
                        "start_char": start,
                        "end_char": end
                    }
                }
                chunks.append(chunk_data)

            # Move to next chunk with overlap
            start = end - self.chunk_overlap

        return chunks

    def compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of file for change detection."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def process_document(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a single document.

        Args:
            file_path: Path to document

        Returns:
            Dictionary with processed document data
        """
        print(f"Processing: {file_path.name}")

        # Extract text
        text = self.extract_text_from_file(file_path)

        if not text.strip():
            print(f"Warning: No text extracted from {file_path.name}")
            return None

        # Compute hash
        file_hash = self.compute_file_hash(file_path)

        # Metadata
        metadata = {
            "source_file": file_path.name,
            "source_type": file_path.suffix[1:],
            "file_hash": file_hash,
            "processed_at": datetime.utcnow().isoformat(),
        }

        # Chunk the text
        chunks = self.chunk_text(text, metadata)

        return {
            "source_file": file_path.name,
            "file_hash": file_hash,
            "chunk_count": len(chunks),
            "total_chars": len(text),
            "chunks": chunks,
            "processed_at": datetime.utcnow().isoformat()
        }

    def process_all_documents(self) -> List[Dict[str, Any]]:
        """Process all documents in the documents directory."""
        all_documents = []
        supported_extensions = ['.pdf', '.docx', '.doc', '.md', '.markdown', '.txt']

        files = [
            f for f in self.documents_dir.iterdir()
            if f.is_file() and f.suffix.lower() in supported_extensions
        ]

        print(f"Found {len(files)} documents to process")

        for file_path in tqdm(files, desc="Processing documents"):
            doc_data = self.process_document(file_path)
            if doc_data:
                all_documents.append(doc_data)

        return all_documents

    def save_processed_documents(self, documents: List[Dict[str, Any]]):
        """Save processed documents to JSON file."""
        output_file = self.processed_dir / "processed_documents.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(documents, f, indent=2, ensure_ascii=False)

        print(f"\nProcessed documents saved to: {output_file}")
        print(f"Total documents: {len(documents)}")
        print(f"Total chunks: {sum(doc['chunk_count'] for doc in documents)}")


def main():
    """Main execution function."""
    print("=" * 60)
    print("Aidemy Chatbot - Document Processor")
    print("=" * 60)

    # Initialize processor
    processor = DocumentProcessor(
        chunk_size=500,
        chunk_overlap=50
    )

    # Process all documents
    documents = processor.process_all_documents()

    # Save results
    if documents:
        processor.save_processed_documents(documents)
    else:
        print("No documents were processed successfully.")


if __name__ == "__main__":
    main()
