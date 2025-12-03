"""
PDF Processing and Indexing Service
Extracts text from PDFs and indexes them into ChromaDB
"""

import os
from PyPDF2 import PdfReader
from typing import List, Dict, Any
import uuid


class PDFProcessor:
    """Process PDF documents and index them into the knowledge base"""
    
    def __init__(self):
        self.chunk_size = 1000  # Characters per chunk
        self.chunk_overlap = 200  # Overlap between chunks
    
    def extract_text_from_pdf(self, pdf_path: str) -> tuple[str, int]:
        """
        Extract text from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Tuple of (extracted_text, page_count)
        """
        try:
            reader = PdfReader(pdf_path)
            page_count = len(reader.pages)
            
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
            
            return text.strip(), page_count
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks for better semantic search
        
        Args:
            text: The full text to chunk
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            
            # Try to break at a sentence boundary
            if end < text_length:
                # Look for sentence endings
                for delimiter in ['. ', '.\n', '? ', '! ']:
                    last_delim = text[start:end].rfind(delimiter)
                    if last_delim != -1:
                        end = start + last_delim + len(delimiter)
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.chunk_overlap
        
        return chunks
    
    def process_and_index_pdf(self, pdf_document):
        """
        Process a PDF document and index it into ChromaDB
        
        Args:
            pdf_document: PDFDocument model instance
        """
        from agent import get_luna_agent
        
        # Extract text from PDF
        pdf_path = pdf_document.file.path
        extracted_text, page_count = self.extract_text_from_pdf(pdf_path)
        
        # Update document with extracted info
        pdf_document.extracted_text = extracted_text
        pdf_document.page_count = page_count
        pdf_document.file_size = os.path.getsize(pdf_path)
        
        # Chunk the text for better indexing
        chunks = self.chunk_text(extracted_text)
        
        # Get Luna agent instance and add to ChromaDB
        agent = get_luna_agent()
        
        for i, chunk in enumerate(chunks):
            metadata = {
                'source': 'pdf_document',
                'document_id': str(pdf_document.id),
                'title': pdf_document.title,
                'chunk_index': i,
                'total_chunks': len(chunks),
                'page_count': page_count
            }
            
            # Add to agent's vector store
            agent.add_knowledge(
                content=chunk,
                metadata=metadata
            )
        
        # Mark as indexed
        pdf_document.is_indexed = True
        pdf_document.metadata = {
            'chunks_created': len(chunks),
            'indexed_at': str(pdf_document.updated_at)
        }
        pdf_document.save()
        
        return {
            'success': True,
            'page_count': page_count,
            'chunks_created': len(chunks),
            'text_length': len(extracted_text)
        }
    
    def reindex_all_pdfs(self):
        """
        Reindex all active PDF documents
        """
        from agent.models import PDFDocument
        
        pdfs = PDFDocument.objects.filter(is_active=True)
        results = []
        
        for pdf in pdfs:
            try:
                result = self.process_and_index_pdf(pdf)
                results.append({
                    'id': str(pdf.id),
                    'title': pdf.title,
                    'status': 'success',
                    'result': result
                })
            except Exception as e:
                results.append({
                    'id': str(pdf.id),
                    'title': pdf.title,
                    'status': 'error',
                    'error': str(e)
                })
        
        return results

