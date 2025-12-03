"""
Unit tests for core/analyzer.py module.
"""
import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from core.analyzer import run_flake8, run_bandit, ai_review, analyze_file


@pytest.mark.unit
class TestRunFlake8:
    """Tests for run_flake8 function."""
    
    def test_run_flake8_with_issues(self, temp_python_file):
        """Test flake8 parsing when issues are found."""
        issues = run_flake8(str(temp_python_file))
        
        # Should find at least the unused import
        assert isinstance(issues, list)
        assert len(issues) > 0
        
        # Check structure of issues
        for issue in issues:
            assert 'line' in issue
            assert 'col' in issue
            assert 'text' in issue
            assert isinstance(issue['line'], int)
            assert isinstance(issue['col'], int)
    
    def test_run_flake8_clean_file(self, temp_directory):
        """Test flake8 with a clean file."""
        clean_file = temp_directory / "clean.py"
        clean_file.write_text("'''Clean module.'''\n")
        
        issues = run_flake8(str(clean_file))
        
        # Should have no issues or minimal issues
        assert isinstance(issues, list)
    
    def test_run_flake8_regex_parsing(self, temp_directory):
        """Test that flake8 output is correctly parsed."""
        test_file = temp_directory / "test.py"
        test_file.write_text("import   sys\nx=1")  # Multiple issues
        
        issues = run_flake8(str(test_file))
        
        # Verify all issues have valid line numbers
        for issue in issues:
            assert issue['line'] > 0
            assert issue['col'] >= 0


@pytest.mark.unit
class TestRunBandit:
    """Tests for run_bandit function."""
    
    def test_run_bandit_with_security_issue(self, temp_directory):
        """Test bandit with code containing security issues."""
        vuln_file = temp_directory / "vulnerable.py"
        vuln_file.write_text("""
import pickle
import os

def load_data(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)  # B301: Pickle usage

os.system('ls')  # B605: Shell command
""")
        
        issues = run_bandit(str(vuln_file))
        
        assert isinstance(issues, list)
        # Bandit should find issues in this vulnerable code
        if len(issues) > 0:
            assert 'issue_severity' in issues[0]
            assert 'issue_text' in issues[0]
    
    def test_run_bandit_clean_file(self, temp_directory):
        """Test bandit with secure code."""
        clean_file = temp_directory / "secure.py"
        clean_file.write_text("""
def add(a, b):
    return a + b
""")
        
        issues = run_bandit(str(clean_file))
        
        assert isinstance(issues, list)
        # Clean file should have no security issues
        assert len(issues) == 0
    
    @patch('subprocess.run')
    def test_run_bandit_invalid_json(self, mock_run, temp_python_file):
        """Test bandit when JSON parsing fails."""
        mock_run.return_value = MagicMock(stdout="invalid json")
        
        issues = run_bandit(str(temp_python_file))
        
        # Should return empty list on parse failure
        assert issues == []


@pytest.mark.unit
class TestAIReview:
    """Tests for ai_review function."""
    
    @patch('core.analyzer.get_llm')
    def test_ai_review_success(self, mock_get_llm, sample_code):
        """Test successful AI review."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "The code looks good. Consider adding error handling."
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        result = ai_review(sample_code, context="Test context")
        
        assert "good" in result.lower()
        mock_llm.invoke.assert_called_once()
        
        # Verify prompt includes code and context
        call_args = mock_llm.invoke.call_args[0][0]
        assert "Test context" in call_args
        assert sample_code in call_args
    
    @patch('core.analyzer.get_llm')
    def test_ai_review_no_llm(self, mock_get_llm, sample_code):
        """Test AI review when LLM is unavailable."""
        mock_get_llm.return_value = None
        
        result = ai_review(sample_code)
        
        assert "not available" in result
    
    @patch('core.analyzer.get_llm')
    def test_ai_review_api_error(self, mock_get_llm, sample_code):
        """Test AI review with API error."""
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception("API Key not found")
        mock_get_llm.return_value = mock_llm
        
        result = ai_review(sample_code)
        
        assert "Unavailable" in result or "Invalid" in result
    
    @patch('core.analyzer.get_llm')
    def test_ai_review_with_response_object(self, mock_get_llm, sample_code):
        """Test AI review handling different response types."""
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = "Direct string response"
        mock_get_llm.return_value = mock_llm
        
        result = ai_review(sample_code)
        
        assert isinstance(result, str)


@pytest.mark.unit
class TestAnalyzeFile:
    """Tests for analyze_file function."""
    
    @patch('core.analyzer.ai_review')
    @patch('core.analyzer.retrieve_context')
    @patch('core.analyzer.recommend_best_practices')
    @patch('core.analyzer.predict_risk_for_line')
    @patch('core.analyzer.analyze_complexity')
    @patch('core.analyzer.detect_patterns')
    @patch('core.analyzer.analyze_code')
    def test_analyze_file_basic(
        self, mock_analyze_code, mock_detect_patterns, 
        mock_analyze_complexity, mock_predict_risk,
        mock_recommend_bp, mock_retrieve_context, mock_ai_review,
        temp_python_file
    ):
        """Test basic file analysis."""
        # Setup mocks
        mock_analyze_code.return_value = []
        mock_detect_patterns.return_value = []
        mock_analyze_complexity.return_value = []
        mock_predict_risk.return_value = "LOW"
        mock_recommend_bp.return_value = ["Use type hints"]
        mock_retrieve_context.return_value = ""
        mock_ai_review.return_value = "Good code"
        
        static, security, ai, practices = analyze_file(str(temp_python_file), use_rag=False)
        
        assert isinstance(static, list)
        assert isinstance(security, list)
        assert isinstance(ai, str)
        assert isinstance(practices, list)
        
        # AI review should be called
        mock_ai_review.assert_called_once()
    
    @patch('core.analyzer.ai_review')
    @patch('core.analyzer.retrieve_context')
    @patch('core.analyzer.recommend_best_practices')
    @patch('core.analyzer.predict_risk_for_line')
    @patch('core.analyzer.analyze_complexity')
    @patch('core.analyzer.detect_patterns')
    @patch('core.analyzer.analyze_code')
    def test_analyze_file_with_rag(
        self, mock_analyze_code, mock_detect_patterns,
        mock_analyze_complexity, mock_predict_risk,
        mock_recommend_bp, mock_retrieve_context, mock_ai_review,
        temp_python_file
    ):
        """Test file analysis with RAG enabled."""
        mock_analyze_code.return_value = []
        mock_detect_patterns.return_value = []
        mock_analyze_complexity.return_value = []
        mock_predict_risk.return_value = "LOW"
        mock_recommend_bp.return_value = []
        mock_retrieve_context.return_value = "Related context from codebase"
        mock_ai_review.return_value = "Analysis with context"
        
        static, security, ai, practices = analyze_file(str(temp_python_file), use_rag=True)
        
        # Verify RAG context was retrieved
        mock_retrieve_context.assert_called_once()
        
        # Verify context was passed to AI review
        call_args = mock_ai_review.call_args
        assert len(call_args[0]) == 2  # code and context
    
    def test_analyze_file_encoding_error(self, temp_directory):
        """Test handling of encoding errors."""
        # Create a file with invalid encoding
        bad_file = temp_directory / "bad_encoding.py"
        bad_file.write_bytes(b'\x80\x81\x82')  # Invalid UTF-8
        
        static, security, ai, practices = analyze_file(str(bad_file))
        
        # Should return error message in ai field
        assert "Error reading file" in ai or "encoding" in ai.lower()
        assert isinstance(static, list)
        assert isinstance(security, list)
    
    @patch('core.analyzer.run_flake8')
    def test_analyze_file_severity_assignment(self, mock_flake8, temp_python_file):
        """Test that severity is assigned to issues."""
        # Mock flake8 to return issues without severity
        mock_flake8.return_value = [
            {'line': 1, 'col': 0, 'text': 'E501 line too long'},
            {'line': 5, 'col': 0, 'text': 'F401 unused import'}
        ]
        
        with patch('core.analyzer.run_bandit', return_value=[]):
            with patch('core.analyzer.analyze_code', return_value=[]):
                with patch('core.analyzer.detect_patterns', return_value=[]):
                    with patch('core.analyzer.analyze_complexity', return_value=[]):
                        with patch('core.analyzer.predict_risk_for_line', return_value='MEDIUM'):
                            with patch('core.analyzer.recommend_best_practices', return_value=[]):
                                with patch('core.analyzer.ai_review', return_value="ok"):
                                    static, _, _, _ = analyze_file(str(temp_python_file))
        
        # All issues should have severity assigned
        for issue in static:
            assert 'severity' in issue
            assert issue['severity'] in ['LOW', 'MEDIUM', 'HIGH']
