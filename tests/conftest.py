"""
Pytest configuration and shared fixtures for AI Code Review Copilot tests.
"""
import os
import sys
import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock
from typing import Generator

# Add project root to Python path so modules can be imported
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def temp_python_file() -> Generator[Path, None, None]:
    """Create a temporary Python file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write("""
import sys
import os

def example_function(x):
    '''Example function for testing.'''
    if x > 0:
        return x * 2
    return 0

# Intentional flake8 issue: unused import
import unused_module
""")
        temp_path = Path(f.name)
    
    yield temp_path
    
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def temp_directory() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_code():
    """Sample Python code for testing."""
    return """
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
"""


@pytest.fixture
def mock_llm():
    """Mock LLM for testing AI functionality."""
    mock = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "This code looks good. No major issues found."
    mock.invoke.return_value = mock_response
    return mock


@pytest.fixture
def mock_embeddings():
    """Mock embeddings model for testing RAG."""
    mock = MagicMock()
    return mock


@pytest.fixture
def mock_chromadb():
    """Mock ChromaDB collection for testing."""
    mock_collection = MagicMock()
    mock_collection.query.return_value = {
        'documents': [['Sample context from codebase']],
        'distances': [[0.5]]
    }
    return mock_collection


@pytest.fixture
def sample_analysis_results():
    """Sample analysis results for testing report generation."""
    return {
        'test_file.py': (
            # Static issues
            [
                {'line': 5, 'col': 1, 'text': 'E501 line too long', 'severity': 'LOW'},
                {'line': 10, 'col': 5, 'text': 'F401 imported but unused', 'severity': 'MEDIUM'}
            ],
            # Security issues
            [
                {
                    'issue_severity': 'HIGH',
                    'issue_text': 'Possible SQL injection',
                    'line_number': 15
                }
            ],
            # AI feedback
            "The code structure is good but could benefit from better error handling.",
            # Best practices
            ['Add type hints to function parameters', 'Use context managers for file operations']
        )
    }


@pytest.fixture
def mock_smtp_server(mocker):
    """Mock SMTP server for email testing."""
    mock_smtp = mocker.patch('smtplib.SMTP')
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server
    return mock_server


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv('AI_PROVIDER', 'gemini')
    monkeypatch.setenv('GEMINI_API_KEY', 'test_api_key_12345')
    monkeypatch.setenv('SMTP_SERVER', 'smtp.test.com')
    monkeypatch.setenv('SMTP_PORT', '587')
    monkeypatch.setenv('SMTP_USER', 'test@test.com')
    monkeypatch.setenv('SMTP_PASSWORD', 'test_password')


@pytest.fixture
def fastapi_client():
    """Create a test client for FastAPI app."""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)


@pytest.fixture
def sample_flake8_output():
    """Sample flake8 output for testing."""
    return """3:1: F401 'sys' imported but unused
5:80: E501 line too long (85 > 79 characters)
10:1: E302 expected 2 blank lines, found 1"""


@pytest.fixture
def sample_bandit_output():
    """Sample bandit JSON output for testing."""
    return {
        "results": [
            {
                "issue_severity": "HIGH",
                "issue_confidence": "HIGH",
                "issue_text": "Use of insecure MD5 hash function.",
                "line_number": 42,
                "line_range": [42],
                "test_name": "blacklist",
                "test_id": "B303"
            }
        ]
    }
