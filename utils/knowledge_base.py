import os
import glob
from langchain_community.vectorstores import Chroma
from core.llm_factory import get_embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Global vector store instance
vector_store = None

def build_index(directory: str):
    """
    Scans the directory for Python files, chunks them, and builds a vector index.
    """
    global vector_store
    print("🔄 Building RAG Knowledge Base... (this may take a moment)")
    
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
            print(f"⚠️ Could not read {file_path}: {e}")

    if not documents:
        print("⚠️ No documents found to index.")
        return

    # Split text into chunks (functions/classes usually fit in 1000 chars)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)

    try:
        embeddings = get_embeddings()
        if not embeddings:
            print("❌ Embeddings model not configured. Check AI_PROVIDER.")
            return

        # Create a transient in-memory vector store for this session
        vector_store = Chroma.from_documents(chunks, embeddings)
        print(f"✅ Indexed {len(chunks)} code chunks.")
    except Exception as e:
        print(f"❌ Failed to create vector store: {e}")
        vector_store = None

def retrieve_context(query: str, k=3):
    """
    Retrieves the most relevant code chunks for a given query.
    """
    global vector_store
    if not vector_store:
        return ""
    
    try:
        docs = vector_store.similarity_search(query, k=k)
        context = "\n\n".join([f"File: {d.metadata['source']}\nCode:\n{d.page_content}" for d in docs])
        return context
    except Exception as e:
        print(f"⚠️ Retrieval failed: {e}")
        return ""
