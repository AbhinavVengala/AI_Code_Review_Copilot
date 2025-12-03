"""
Unit tests for utils/email_sender.py module.
"""
import pytest
from unittest.mock import patch, MagicMock, call
from utils.email_sender import send_email_report


@pytest.mark.unit
class TestSendEmailReport:
    """Tests for send_email_report function."""
    
    def test_send_email_success(self, mock_smtp_server, monkeypatch):
        """Test successful email sending."""
        monkeypatch.setenv('SMTP_USER', 'sender@test.com')
        monkeypatch.setenv('SMTP_PASSWORD', 'password123')
        
        result = send_email_report(
            to_email='recipient@test.com',
            repo_url='https://github.com/test/repo',
            report_content='Test report content',
            html_content='<html>Test HTML</html>'
        )
        
        assert result is True
        
        # Verify SMTP calls
        mock_smtp_server.starttls.assert_called_once()
        mock_smtp_server.login.assert_called_once_with('sender@test.com', 'password123')
        mock_smtp_server.sendmail.assert_called_once()
        mock_smtp_server.quit.assert_called_once()
    
    def test_send_email_no_credentials(self, monkeypatch):
        """Test email sending without credentials."""
        monkeypatch.delenv('SMTP_USER', raising=False)
        monkeypatch.delenv('SMTP_PASSWORD', raising=False)
        
        result = send_email_report(
            to_email='test@test.com',
            repo_url='https://github.com/test/repo',
            report_content='Report'
        )
        
        assert result is False
    
    def test_send_email_missing_user(self, monkeypatch):
        """Test with missing SMTP user."""
        monkeypatch.delenv('SMTP_USER', raising=False)
        monkeypatch.setenv('SMTP_PASSWORD', 'password')
        
        result = send_email_report(
            to_email='test@test.com',
            repo_url='https://github.com/test/repo',
            report_content='Report'
        )
        
        assert result is False
    
    def test_send_email_missing_password(self, monkeypatch):
        """Test with missing SMTP password."""
        monkeypatch.setenv('SMTP_USER', 'user@test.com')
        monkeypatch.delenv('SMTP_PASSWORD', raising=False)
        
        result = send_email_report(
            to_email='test@test.com',
            repo_url='https://github.com/test/repo',
            report_content='Report'
        )
        
        assert result is False
    
    def test_send_email_smtp_failure(self, mocker, monkeypatch):
        """Test SMTP connection failure."""
        monkeypatch.setenv('SMTP_USER', 'sender@test.com')
        monkeypatch.setenv('SMTP_PASSWORD', 'password')
        
        mock_smtp = mocker.patch('smtplib.SMTP')
        mock_smtp.side_effect = Exception("Connection failed")
        
        result = send_email_report(
            to_email='test@test.com',
            repo_url='https://github.com/test/repo',
            report_content='Report'
        )
        
        assert result is False
    
    def test_send_email_with_html_content(self, mock_smtp_server, monkeypatch):
        """Test email with HTML content."""
        monkeypatch.setenv('SMTP_USER', 'sender@test.com')
        monkeypatch.setenv('SMTP_PASSWORD', 'password')
        
        html_content = '<html><body><h1>Test Report</h1></body></html>'
        
        result = send_email_report(
            to_email='recipient@test.com',
            repo_url='https://github.com/test/repo',
            report_content='Plain text',
            html_content=html_content
        )
        
        assert result is True
        
        # Verify email was sent
        mock_smtp_server.sendmail.assert_called_once()
    
    def test_send_email_without_html_content(self, mock_smtp_server, monkeypatch):
        """Test email without HTML content (plain text only)."""
        monkeypatch.setenv('SMTP_USER', 'sender@test.com')
        monkeypatch.setenv('SMTP_PASSWORD', 'password')
        
        result = send_email_report(
            to_email='recipient@test.com',
            repo_url='https://github.com/test/repo',
            report_content='Plain text only'
        )
        
        assert result is True
    
    def test_send_email_subject_format(self, mock_smtp_server, monkeypatch):
        """Test email subject includes repo URL."""
        monkeypatch.setenv('SMTP_USER', 'sender@test.com')
        monkeypatch.setenv('SMTP_PASSWORD', 'password')
        
        repo_url = 'https://github.com/user/awesome-project'
        
        send_email_report(
            to_email='test@test.com',
            repo_url=repo_url,
            report_content='Report'
        )
        
        # Verify sendmail was called with proper arguments
        call_args = mock_smtp_server.sendmail.call_args[0]
        message_string = call_args[2]
        
        # Subject should contain repo URL
        assert repo_url in message_string
        assert "AI Code Review Report" in message_string
    
    def test_send_email_custom_smtp_settings(self, mocker, monkeypatch):
        """Test with custom SMTP server and port."""
        monkeypatch.setenv('SMTP_SERVER', 'mail.custom.com')
        monkeypatch.setenv('SMTP_PORT', '465')
        monkeypatch.setenv('SMTP_USER', 'user@custom.com')
        monkeypatch.setenv('SMTP_PASSWORD', 'pass')
        
        mock_smtp = mocker.patch('smtplib.SMTP')
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        send_email_report(
            to_email='test@test.com',
            repo_url='https://github.com/test/repo',
            report_content='Report'
        )
        
        # Verify custom server was used
        mock_smtp.assert_called_once_with('mail.custom.com', 465)
