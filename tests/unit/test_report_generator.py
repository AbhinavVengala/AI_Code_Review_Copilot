"""
Unit tests for core/report_generator.py module.
"""
import pytest
from datetime import datetime
from core.report_generator import generate_report, generate_html_report


@pytest.mark.unit
class TestGenerateReport:
    """Tests for generate_report function."""
    
    def test_generate_report_with_issues(self, sample_analysis_results):
        """Test markdown report generation with issues."""
        report = generate_report(sample_analysis_results)
        
        assert isinstance(report, str)
        assert "AI Code Review Report" in report
        assert "test_file.py" in report
        assert "Static Analysis" in report
        assert "Security Analysis" in report
        assert "Summary" in report
        
        # Check for issue counts
        assert "2" in report  # 2 static issues
        assert "1" in report  # 1 security issue
    
    def test_generate_report_empty_results(self):
        """Test report generation with no issues."""
        empty_results = {
            'clean_file.py': ([], [], "No issues found", [])
        }
        
        report = generate_report(empty_results)
        
        assert "clean_file.py" in report
        assert "No static issues found" in report
        assert "No security issues found" in report
        assert "No issues found" in report
    
    def test_generate_report_multiple_files(self):
        """Test report with multiple files."""
        results = {
            'file1.py': (
                [{'line': 1, 'col': 0, 'text': 'Issue 1', 'severity': 'LOW'}],
                [],
                "AI feedback 1",
                []
            ),
            'file2.py': (
                [],
                [{'issue_severity': 'HIGH', 'issue_text': 'Security issue', 'line_number': 10}],
                "AI feedback 2",
                []
            )
        }
        
        report = generate_report(results)
        
        assert "file1.py" in report
        assert "file2.py" in report
        assert "Files analyzed:** 2" in report
    
    def test_generate_report_best_practices(self):
        """Test report includes best practices."""
        results = {
            'test.py': (
                [],
                [],
                "Good",
                ['Use type hints', 'Add docstrings']
            )
        }
        
        report = generate_report(results)
        
        assert "Use type hints" in report
        assert "Add docstrings" in report
    
    def test_generate_report_severity_icons(self, sample_analysis_results):
        """Test that severity levels are included in report."""
        report = generate_report(sample_analysis_results)
        
        # Should contain severity information
        assert "Severity" in report or "severity" in report


@pytest.mark.unit
class TestGenerateHTMLReport:
    """Tests for generate_html_report function."""
    
    def test_generate_html_report_structure(self, sample_analysis_results):
        """Test HTML report has proper structure."""
        html = generate_html_report(sample_analysis_results)
        
        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html
        assert "<html>" in html
        assert "</html>" in html
        assert "AI Code Review Report" in html
    
    def test_generate_html_report_dark_theme(self, sample_analysis_results):
        """Test HTML report uses dark theme styling."""
        html = generate_html_report(sample_analysis_results)
        
        # Check for dark background colors
        assert "#0f172a" in html or "#1e293b" in html
        # Check for proper styling attributes
        assert "background" in html
        assert "color" in html
    
    def test_generate_html_report_summary_cards(self, sample_analysis_results):
        """Test HTML report includes summary cards."""
        html = generate_html_report(sample_analysis_results)
        
        # Should show counts
        assert "2" in html  # Static issues
        assert "1" in html  # Security issues
        # Should have summary section
        assert "Static Issues" in html or "static" in html.lower()
        assert "Security" in html or "security" in html.lower()
    
    def test_generate_html_report_file_sections(self, sample_analysis_results):
        """Test HTML report has file sections."""
        html = generate_html_report(sample_analysis_results)
        
        assert "test_file.py" in html
        assert "Static Analysis" in html
        assert "Security Risks" in html
        assert "AI Insights" in html
    
    def test_generate_html_report_empty_results(self):
        """Test HTML report with no issues."""
        empty_results = {
            'clean.py': ([], [], None, [])
        }
        
        html = generate_html_report(empty_results)
        
        assert "No static issues found" in html
        assert "No security issues found" in html
    
    def test_generate_html_report_severity_colors(self):
        """Test HTML report uses color coding for severity."""
        results = {
            'test.py': (
                [
                    {'line': 1, 'col': 0, 'text': 'High issue', 'severity': 'HIGH'},
                    {'line': 2, 'col': 0, 'text': 'Medium issue', 'severity': 'MEDIUM'},
                    {'line': 3, 'col': 0, 'text': 'Low issue', 'severity': 'LOW'}
                ],
                [],
                "OK",
                []
            )
        }
        
        html = generate_html_report(results)
        
        # Check for color codes (red for high, yellow for medium, blue for low)
        assert "#ef4444" in html  # Red
        assert "#eab308" in html  # Yellow
        assert "#3b82f6" in html  # Blue
    
    def test_generate_html_report_ai_feedback_formatting(self):
        """Test AI feedback is properly formatted in HTML."""
        results = {
            'test.py': (
                [],
                [],
                "**Important**: Use better naming\n\n## Suggestions\nCode is good",
                []
            )
        }
        
        html = generate_html_report(results)
        
        # Should contain the AI feedback
        assert "Important" in html
        assert "Suggestions" in html
    
    def test_generate_html_report_timestamp(self):
        """Test HTML report includes timestamp."""
        results = {'test.py': ([], [], "OK", [])}
        
        html = generate_html_report(results)
        
        # Should contain current date
        current_year = datetime.now().year
        assert str(current_year) in html
    
    def test_generate_html_report_email_compatibility(self, sample_analysis_results):
        """Test HTML uses inline styles for email compatibility."""
        html = generate_html_report(sample_analysis_results)
        
        # Should use inline styles, not external CSS
        assert 'style="' in html
        # Should not reference external stylesheets
        assert '<link' not in html
        assert '.css' not in html
