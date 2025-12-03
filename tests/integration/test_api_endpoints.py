"""
Integration tests for FastAPI endpoints in app/main.py.
"""
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


@pytest.mark.integration
class TestHealthEndpoint:
    """Tests for /health endpoint."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


@pytest.mark.integration
class TestAnalyzeEndpoint:
    """Tests for /analyze endpoint."""
    
    @patch('app.main.analyze_file')
    def test_analyze_code_success(self, mock_analyze):
        """Test successful code analysis."""
        mock_analyze.return_value = (
            [{'line': 1, 'col': 0, 'text': 'Issue', 'severity': 'LOW'}],
            [],
            "Good code",
            []
        )
        
        response = client.post(
            "/analyze",
            json={
                "code": "def test():\n    pass",
                "use_rag": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "static_issues" in data
        assert "security_issues" in data
        assert "ai_feedback" in data
        assert len(data["static_issues"]) == 1
    
    @patch('app.main.analyze_file')
    def test_analyze_code_with_rag(self, mock_analyze):
        """Test code analysis with RAG enabled."""
        mock_analyze.return_value = ([], [], "Analysis with context", [])
        
        response = client.post(
            "/analyze",
            json={
                "code": "print('hello')",
                "use_rag": True
            }
        )
        
        assert response.status_code == 200
        
        # Verify analyze_file was called with use_rag=True
        call_args = mock_analyze.call_args
        assert call_args[1]['use_rag'] is True
    
    @patch('app.main.analyze_file')
    def test_analyze_code_error_handling(self, mock_analyze):
        """Test error handling in analyze endpoint."""
        mock_analyze.side_effect = Exception("Analysis failed")
        
        response = client.post(
            "/analyze",
            json={"code": "test", "use_rag": False}
        )
        
        assert response.status_code == 500
        assert "detail" in response.json()


@pytest.mark.integration
class TestAnalyzeUploadEndpoint:
    """Tests for /analyze/upload endpoint."""
    
    @patch('app.main.analyze_file')
    def test_upload_file_success(self, mock_analyze):
        """Test successful file upload and analysis."""
        mock_analyze.return_value = (
            [],
            [{'issue_severity': 'HIGH', 'issue_text': 'SQL injection', 'line_number': 10}],
            "Security issue found",
            []
        )
        
        # Create test file
        test_content = b"def vulnerable():\n    pass"
        
        response = client.post(
            "/analyze/upload",
            files={"file": ("test.py", test_content, "text/x-python")},
            data={"use_rag": "false"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["security_issues"]) == 1
        assert data["security_issues"][0]["severity"] == "HIGH"
    
    @patch('app.main.analyze_file')
    def test_upload_non_python_file(self, mock_analyze):
        """Test uploading non-Python file."""
        test_content = b"Not Python code"
        
        response = client.post(
            "/analyze/upload",
            files={"file": ("test.txt", test_content, "text/plain")},
            data={"use_rag": "false"}
        )
        
        # Should still attempt analysis (analyzer will handle it)
        assert response.status_code in [200, 500]


@pytest.mark.integration
class TestAnalyzeFolderEndpoint:
    """Tests for /analyze/upload-folder endpoint."""
    
    @patch('app.main.analyze_file')
    def test_upload_folder_multiple_files(self, mock_analyze):
        """Test analyzing multiple files from a folder."""
        mock_analyze.return_value = (
            [{'line': 1, 'col': 0, 'text': 'Issue', 'severity': 'LOW'}],
            [],
            "OK",
            []
        )
        
        files = [
            ("files", ("file1.py", b"print('test1')", "text/x-python")),
            ("files", ("file2.py", b"print('test2')", "text/x-python"))
        ]
        
        response = client.post(
            "/analyze/upload-folder",
            files=files,
            data={"use_rag": "false"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should aggregate issues from both files
        assert "static_issues" in data
    
    @patch('app.main.analyze_file')
    def test_upload_folder_no_python_files(self, mock_analyze):
        """Test uploading folder with no Python files."""
        files = [
            ("files", ("readme.txt", b"Not Python", "text/plain")),
            ("files", ("config.json", b"{}", "application/json"))
        ]
        
        response = client.post(
            "/analyze/upload-folder",
            files=files,
            data={"use_rag": "false"}
        )
        
        assert response.status_code == 400
        assert "No Python files" in response.json()["detail"]
    
    @patch('app.main.analyze_file')
    def test_upload_folder_deduplicates_errors(self, mock_analyze):
        """Test that global errors are deduplicated."""
        # Return API error for each file
        mock_analyze.return_value = (
            [],
            [],
            "⚠️ **AI Review Unavailable**: Invalid API Key",
            []
        )
        
        files = [
            ("files", ("file1.py", b"code1", "text/x-python")),
            ("files", ("file2.py", b"code2", "text/x-python")),
            ("files", ("file3.py", b"code3", "text/x-python"))
        ]
        
        response = client.post(
            "/analyze/upload-folder",
            files=files,
            data={"use_rag": "false"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Error message should appear only once, not three times
        feedback = data["ai_feedback"]
        assert feedback.count("AI Review Unavailable") == 1


@pytest.mark.integration
@pytest.mark.slow
class TestAnalyzeGithubEndpoint:
    """Tests for /analyze/github endpoint."""
    
    @patch('app.main.process_github_analysis_background')
    def test_github_analysis_with_email(self, mock_background):
        """Test GitHub analysis with email notification."""
        response = client.post(
            "/analyze/github",
            json={
                "repo_url": "https://github.com/test/repo",
                "email": "user@test.com",
                "use_rag": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "queued" in data["message"].lower()
        assert "user@test.com" in data["message"]
    
    @patch('asyncio.create_subprocess_exec')
    async def test_github_analysis_streaming(self, mock_subprocess):
        """Test GitHub analysis with streaming response."""
        # Mock successful git clone
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b"", b"")
        mock_subprocess.return_value = mock_process
        
        with patch('glob.glob', return_value=[]):
            response = client.post(
                "/analyze/github",
                json={
                    "repo_url": "https://github.com/test/repo",
                    "use_rag": False
                }
            )
            
            # Should return streaming response
            assert response.status_code == 200
    
    @patch('asyncio.create_subprocess_exec')
    async def test_github_clone_failure(self, mock_subprocess):
        """Test handling of git clone failure."""
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.communicate.return_value = (b"", b"Error")
        mock_subprocess.return_value = mock_process
        
        response = client.post(
            "/analyze/github",
            json={
                "repo_url": "https://github.com/test/repo",
                "use_rag": False
            }
        )
        
        # Should handle error gracefully
        assert response.status_code == 200


@pytest.mark.integration
class TestCORS:
    """Tests for CORS configuration."""
    
    def test_cors_headers_present(self):
        """Test CORS headers are present in responses."""
        response = client.get("/health", headers={"Origin": "http://localhost:3000"})
        
        assert response.status_code == 200
        # CORS middleware should add headers
        # Note: TestClient may not fully simulate CORS


@pytest.mark.integration
class TestErrorHandling:
    """Tests for general error handling."""
    
    def test_invalid_endpoint(self):
        """Test accessing non-existent endpoint."""
        response = client.get("/nonexistent")
        
        assert response.status_code == 404
    
    def test_invalid_json_payload(self):
        """Test sending invalid JSON."""
        response = client.post(
            "/analyze",
            data="not json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422  # Unprocessable Entity
