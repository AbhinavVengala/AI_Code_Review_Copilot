import os
import glob
from langchain_community.vectorstores import Chroma
from core.llm_factory import get_embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from core.logging_config import get_logger

logger = get_logger(__name__)

# Global vector store instance
vector_store = None

def build_index(directory: str):
    """
    Scans the directory for Python files, chunks them, and builds a vector index.
    """
    global vector_store
    logger.info("rag_index_building_started", directory=directory)
    
    documents = []
    files = glob.glob(os.path.join(directory, "**/*.py"), recursive=True)
    
    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Create a document with metadata
                doc = Document(page_content=content, metadata={"source": file_path})
                documents.append(doc)
        except Exception as e:
            logger.warning("file_read_failed", file=file_path, error=str(e))

    if not documents:
        logger.warning("rag_index_no_documents")
        return

    # Split text into chunks (functions/classes usually fit in 1000 chars)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)

    try:
        embeddings = get_embeddings()
        if not embeddings:
            logger.error("rag_embeddings_unavailable")
            return

        # Create a transient in-memory vector store for this session
        vector_store = Chroma.from_documents(chunks, embeddings)
        logger.info("rag_index_complete", chunk_count=len(chunks), document_count=len(documents))
    except Exception as e:
        logger.error("rag_index_failed", error=str(e), exc_info=True)
        vector_store = None

def retrieve_context(query: str, k=3):
    """
    Retrieves the most relevant code chunks for a given query.
    """
    if not vector_store:
        return ""
    
    try:
        docs = vector_store.similarity_search(query, k=k)
        context = "\n\n".join([f"File: {d.metadata['source']}\nCode:\n{d.page_content}" for d in docs])
        return context
    except Exception as e:
        logger.error("rag_retrieval_failed", error=str(e))
        return ""
