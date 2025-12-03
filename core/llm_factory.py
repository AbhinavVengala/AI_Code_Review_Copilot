import os
from dotenv import load_dotenv
from core.logging_config import get_logger

load_dotenv()

logger = get_logger(__name__)

def get_llm():
    """
    Returns the configured Chat Model based on AI_PROVIDER.
    Defaults to Gemini.
    """
    provider = os.getenv("AI_PROVIDER", "gemini").lower()
    
    if provider == "openai":
        try:
            from langchain_openai import ChatOpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("llm_init_failed", provider="openai", reason="missing_api_key")
                return None
            logger.info("llm_initialized", provider="openai", model="gpt-4o")
            return ChatOpenAI(model="gpt-4o", openai_api_key=api_key)
        except ImportError:
            logger.error("llm_init_failed", provider="openai", reason="import_error", package="langchain-openai")
            return None
            
    elif provider == "gemini":
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.warning("llm_init_failed", provider="gemini", reason="missing_api_key")
                return None
            api_key = api_key.strip()
            # Ensure GOOGLE_API_KEY is set for the library
            os.environ["GOOGLE_API_KEY"] = api_key
            logger.info("llm_initialized", provider="gemini", model="gemini-1.5-flash-latest")
            return ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", google_api_key=api_key)
        except ImportError:
            logger.error("llm_init_failed", provider="gemini", reason="import_error", package="langchain-google-genai")
            return None
    
    return None

def get_embeddings():
    """
    Returns the configured Embeddings Model based on AI_PROVIDER.
    """
    provider = os.getenv("AI_PROVIDER", "gemini").lower()
    
    if provider == "openai":
        try:
            from langchain_openai import OpenAIEmbeddings
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return None
            return OpenAIEmbeddings(openai_api_key=api_key)
        except ImportError:
            return None

    elif provider == "gemini":
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                return None
            return GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
        except ImportError:
            return None
            
    return None
