from typing import List
import streamlit as st
from pyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from config import Config

class RAGPipeline:
    """RAG pipeline for PDF processing and retrieval"""
    
    def __init__(self):
        """Initialize the RAG pipeline with embeddings and text splitter"""
        try:
            if Config.USE_FREE_EMBEDDINGS:
                # Use free sentence transformers
                from langchain_community.embeddings import HuggingFaceEmbeddings
                st.info("Using free HuggingFace embeddings (first load may take a moment)")
                self.embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2",
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True}
                )
            else:
                # Use OpenAI embeddings
                from langchain_openai import OpenAIEmbeddings
                self.embeddings = OpenAIEmbeddings(
                    openai_api_key=Config.OPENAI_API_KEY,
                    model=Config.EMBEDDING_MODEL
                )
        except Exception as e:
            st.error(f"Error initializing embeddings: {str(e)}")
            raise
        
        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from uploaded PDF file"""
        try:
            # Reset file pointer to beginning
            pdf_file.seek(0)
            
            # Read PDF
            pdf_reader = PdfReader(pdf_file)
            
            # Check if PDF has pages
            if len(pdf_reader.pages) == 0:
                raise Exception("PDF file has no pages")
            
            text = ""
            pages_with_text = 0
            
            # Extract text from each page
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text += page_text + "\n\n"
                        pages_with_text += 1
                except Exception as e:
                    st.warning(f"Could not extract text from page {page_num + 1}: {str(e)}")
                    continue
            
            # Check if we extracted any text
            if not text.strip():
                raise Exception(
                    f"No text could be extracted from the PDF. "
                    f"This might be a scanned/image-based PDF. "
                    f"Total pages: {len(pdf_reader.pages)}, Pages with text: {pages_with_text}"
                )
            
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Error extracting text from PDF '{pdf_file.name}': {str(e)}")
    
    def process_pdfs(self, pdf_files) -> bool:
        """Process multiple PDF files and create vector store"""
        try:
            if not pdf_files:
                st.error("No PDF files provided")
                return False
            
            all_texts = []
            successful_files = []
            failed_files = []
            
            # Extract text from each PDF
            st.info(f"Processing {len(pdf_files)} PDF file(s)...")
            
            for pdf_file in pdf_files:
                try:
                    st.info(f"Extracting text from: {pdf_file.name}")
                    text = self.extract_text_from_pdf(pdf_file)
                    
                    if text and len(text.strip()) > 0:
                        all_texts.append(text)
                        successful_files.append(pdf_file.name)
                        st.success(f"✓ Successfully extracted text from {pdf_file.name} ({len(text)} characters)")
                    else:
                        failed_files.append(pdf_file.name)
                        st.warning(f"✗ No text extracted from {pdf_file.name}")
                        
                except Exception as e:
                    failed_files.append(pdf_file.name)
                    st.warning(f"✗ Error processing {pdf_file.name}: {str(e)}")
                    continue
            
            # Check if we have any text
            if not all_texts:
                error_msg = "No text could be extracted from any PDF files. "
                if failed_files:
                    error_msg += f"Failed files: {', '.join(failed_files)}"
                raise Exception(error_msg)
            
            # Show summary
            if failed_files:
                st.warning(f"Successfully processed {len(successful_files)}/{len(pdf_files)} files. Failed: {', '.join(failed_files)}")
            
            # Combine all texts
            combined_text = "\n\n".join(all_texts)
            
            # Validate combined text
            if not combined_text.strip():
                raise Exception("Combined text is empty after processing")
            
            st.info(f"Combined text length: {len(combined_text)} characters")
            
            # Split into chunks
            st.info("Splitting text into chunks...")
            chunks = self.text_splitter.split_text(combined_text)
            
            # Validate chunks
            if not chunks:
                raise Exception("No chunks created from text. The text might be too short.")
            
            # Filter out empty chunks
            original_chunk_count = len(chunks)
            chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
            
            if not chunks:
                raise Exception("All chunks are empty after filtering")
            
            if len(chunks) < original_chunk_count:
                st.info(f"Filtered out {original_chunk_count - len(chunks)} empty chunks")
            
            st.info(f"Created {len(chunks)} text chunks")
            
            # Create documents
            documents = [
                Document(
                    page_content=chunk,
                    metadata={"chunk_id": i}
                ) 
                for i, chunk in enumerate(chunks)
            ]
            
            # Validate documents
            if not documents:
                raise Exception("No documents created from chunks")
            
            # Create vector store
            if Config.USE_FREE_EMBEDDINGS:
                st.info(f"Creating vector embeddings for {len(documents)} documents (this may take 30-60 seconds on first run)...")
            else:
                st.info(f"Creating vector embeddings for {len(documents)} documents...")
            
            try:
                self.vector_store = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    persist_directory=None
                )
                st.success(f"✓ Vector store created successfully with {len(documents)} documents")
            except Exception as e:
                raise Exception(f"Failed to create vector store: {str(e)}")
            
            return True
            
        except Exception as e:
            st.error(f"Error processing PDFs: {str(e)}")
            return False
    
    def retrieve(self, query: str, k: int = None) -> List[str]:
        """Retrieve relevant chunks for a query"""
        if k is None:
            k = Config.TOP_K_RESULTS
            
        if self.vector_store is None:
            return []
        
        try:
            results = self.vector_store.similarity_search(query, k=k)
            return [doc.page_content for doc in results]
        except Exception as e:
            st.error(f"Error retrieving documents: {str(e)}")
            return []
    
    def is_initialized(self) -> bool:
        """Check if RAG pipeline is initialized"""
        return self.vector_store is not None
    
    def get_stats(self) -> dict:
        """Get statistics about the vector store"""
        if not self.is_initialized():
            return {
                "initialized": False,
                "document_count": 0
            }
        
        try:
            # Get collection info
            collection = self.vector_store._collection
            return {
                "initialized": True,
                "document_count": collection.count()
            }
        except:
            return {
                "initialized": True,
                "document_count": "Unknown"

            }
