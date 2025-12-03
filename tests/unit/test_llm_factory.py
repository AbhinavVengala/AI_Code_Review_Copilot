"""
Unit tests for core/llm_factory.py module.
Tests mock the actual langchain modules since imports happen inside functions.
"""
import pytest
import os
from unittest.mock import patch, MagicMock
from core.llm_factory import get_llm, get_embeddings


@pytest.mark.unit
class TestGetLLM:
    """Tests for get_llm function."""
    
    @patch('langchain_google_genai.ChatGoogleGenerativeAI')
    def test_get_llm_gemini_success(self, mock_gemini, monkeypatch):
        """Test successful Gemini LLM initialization."""
        monkeypatch.setenv('AI_PROVIDER', 'gemini')
        monkeypatch.setenv('GEMINI_API_KEY', 'test_key_123')
        
        mock_instance = MagicMock()
        mock_gemini.return_value = mock_instance
        
        llm = get_llm()
        
        assert llm is not None
        mock_gemini.assert_called_once()
    
    @patch('langchain_openai.ChatOpenAI')
    def test_get_llm_openai_success(self, mock_openai, monkeypatch):
        """Test successful OpenAI LLM initialization."""
        monkeypatch.setenv('AI_PROVIDER', 'openai')
        monkeypatch.setenv('OPENAI_API_KEY', 'sk-test123')
        
        mock_instance = MagicMock()
        mock_openai.return_value = mock_instance
        
        llm = get_llm()
        
        assert llm is not None
        mock_openai.assert_called_once()
    
    def test_get_llm_no_api_key_gemini(self, monkeypatch):
        """Test Gemini without API key returns None."""
        monkeypatch.setenv('AI_PROVIDER', 'gemini')
        monkeypatch.delenv('GEMINI_API_KEY', raising=False)
        
        llm = get_llm()
        
        assert llm is None
    
    def test_get_llm_no_api_key_openai(self, monkeypatch):
        """Test OpenAI without API key returns None."""
        monkeypatch.setenv('AI_PROVIDER', 'openai')
        monkeypatch.delenv('OPENAI_API_KEY', raising=False)
        
        llm = get_llm()
        
        assert llm is None
    
    @patch('langchain_google_genai.ChatGoogleGenerativeAI')
    def test_get_llm_default_provider(self, mock_gemini, monkeypatch):
        """Test default provider is Gemini."""
        monkeypatch.delenv('AI_PROVIDER', raising=False)
        monkeypatch.setenv('GEMINI_API_KEY', 'test_key')
        
        mock_gemini.return_value = MagicMock()
        llm = get_llm()
        
        # Should use Gemini by default
        mock_gemini.assert_called_once()
    
    def test_get_llm_unknown_provider(self, monkeypatch):
        """Test unknown provider returns None."""
        monkeypatch.setenv('AI_PROVIDER', 'unknown_provider')
        
        llm = get_llm()
        
        assert llm is None


@pytest.mark.unit
class TestGetEmbeddings:
    """Tests for get_embeddings function."""
    
    @patch('langchain_google_genai.GoogleGenerativeAIEmbeddings')
    def test_get_embeddings_gemini(self, mock_embeddings, monkeypatch):
        """Test Gemini embeddings initialization."""
        monkeypatch.setenv('AI_PROVIDER', 'gemini')
        monkeypatch.setenv('GEMINI_API_KEY', 'test_key')
        
        mock_instance = MagicMock()
        mock_embeddings.return_value = mock_instance
        
        embeddings = get_embeddings()
        
        assert embeddings is not None
        mock_embeddings.assert_called_once()
    
    @patch('langchain_openai.OpenAIEmbeddings')
    def test_get_embeddings_openai(self, mock_embeddings, monkeypatch):
        """Test OpenAI embeddings initialization."""
        monkeypatch.setenv('AI_PROVIDER', 'openai')
        monkeypatch.setenv('OPENAI_API_KEY', 'sk-test')
        
        mock_instance = MagicMock()
        mock_embeddings.return_value = mock_instance
        
        embeddings = get_embeddings()
        
        assert embeddings is not None
        mock_embeddings.assert_called_once()
    
    def test_get_embeddings_no_api_key(self, monkeypatch):
        """Test embeddings without API key returns None."""
        monkeypatch.setenv('AI_PROVIDER', 'gemini')
        monkeypatch.delenv('GEMINI_API_KEY', raising=False)
        
        embeddings = get_embeddings()
        
        assert embeddings is None
    
    @patch('langchain_google_genai.GoogleGenerativeAIEmbeddings')
    def test_get_embeddings_default_provider(self, mock_embeddings, monkeypatch):
        """Test embeddings uses default provider."""
        monkeypatch.delenv('AI_PROVIDER', raising=False)
        monkeypatch.setenv('GEMINI_API_KEY', 'test_key')
        
        mock_embeddings.return_value = MagicMock()
        embeddings = get_embeddings()
        
        mock_embeddings.assert_called_once()
