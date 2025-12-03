"""
Simple smoke test to verify pytest and imports work.
"""
import pytest


def test_pytest_works():
    """Verify pytest is working."""
    assert True


def test_imports():
    """Test that core modules can be imported."""
    try:
        from core import analyzer
        from core import report_generator
        from core import llm_factory
        from utils import email_sender
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


def test_environment_setup():
    """Test that environment variables are set by conftest."""
    import os
    assert os.getenv('GEMINI_API_KEY') is not None
    assert os.getenv('AI_PROVIDER') is not None
