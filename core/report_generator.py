from datetime import datetime
from feedback.severity_classification import SEVERITY_ICONS, provide_feedback
from core.utils import extract_snippet

def generate_report(results):
    report = []
    report.append("# 🧑‍💻 AI Code Review Report")
    report.append(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("\n---\n")

    total_static = 0
    total_security = 0

    for file_path, (static_issues, bandit_issues, ai_feedback, best_practices) in results.items():
        report.append(f"## 📂 File: `{file_path}`")

        report.append("### ✅ Static Analysis + ML Severity")
        if static_issues:
            report.append("| Line | Col | Issue | Severity | Snippet |")
            report.append("|------|-----|-------|---------|---------|")
            for issue in static_issues[:10]:
                severity = issue.get("severity", "LOW")
                icon_text = provide_feedback(issue.get("text", ""), severity)
                report.append(f"| {issue.get('line','-')} | {issue.get('col','-')} | {issue.get('text','')} | {icon_text} |")
                snippet = extract_snippet(file_path, issue.get("line", 1))
                if snippet:
                    report.append(f"\n```python\n{snippet}\n```\n")
            total_static += len(static_issues)
        else:
            report.append("- No static issues found.")

        report.append("\n### 🔒 Security Analysis")
        if bandit_issues:
            report.append("| Severity | Issue | Line | Snippet |")
            report.append("|----------|-------|------|---------|")
            for issue in bandit_issues[:5]:
                icon = SEVERITY_ICONS.get(issue["issue_severity"], "⚠️")
                snippet = extract_snippet(file_path, issue["line_number"])
                report.append(f"| {icon} {issue['issue_severity']} | {issue['issue_text']} | {issue['line_number']} | {snippet} |")
                snippet = extract_snippet(file_path, issue.get("line", 1))
                if snippet:
                    report.append(f"\n```python\n{snippet}\n```\n")
            total_security += len(bandit_issues)
        else:
            report.append("- No security issues found.")

        report.append("\n### 📘 Best Practice Recommendations")
        if best_practices:
            if not isinstance(best_practices, list):
                best_practices = [best_practices]
            
            for rec in best_practices:
                report.append(f"- {rec}")
        else:
            report.append("- No best practice suggestions.")

        report.append("\n### 🤖 AI Suggestions")
        report.append(ai_feedback or "No AI suggestions generated.")
        report.append("\n---\n")

    report.append("## 📌 Summary")
    report.append(f"- **Static issues found:** {total_static}")
    report.append(f"- **Security warnings:** {total_security}")
    report.append(f"- **Files analyzed:** {len(results)}")
    return "\n".join(report)


def generate_html_report(results):
    """
    Generates a dark-themed HTML report for email.
    """
    total_static = 0
    total_security = 0
    file_reports = []

    for file_path, (static_issues, bandit_issues, ai_feedback, best_practices) in results.items():
        total_static += len(static_issues)
        total_security += len(bandit_issues)
        
        # Format Static Issues
        static_html = ""
        if static_issues:
            for issue in static_issues[:10]: # Limit to top 10
                severity = issue.get("severity", "LOW")
                color = "#ef4444" if severity == "HIGH" else "#eab308" if severity == "MEDIUM" else "#3b82f6"
                static_html += f"""
                <div style="background: rgba(30, 41, 59, 0.5); border-left: 4px solid {color}; padding: 12px; margin-bottom: 8px; border-radius: 4px;">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                        <span style="background: {color}20; color: {color}; font-size: 10px; font-weight: bold; padding: 2px 6px; border-radius: 4px;">{severity}</span>
                        <span style="color: #94a3b8; font-family: monospace; font-size: 12px;">Line {issue.get('line', '-')}</span>
                    </div>
                    <div style="color: #e2e8f0; font-size: 13px;">{issue.get('text', '')}</div>
                </div>
                """
        else:
            static_html = '<p style="color: #94a3b8; font-style: italic;">No static issues found.</p>'

        # Format Security Issues
        security_html = ""
        if bandit_issues:
            for issue in bandit_issues[:5]:
                severity = issue.get("issue_severity", "LOW")
                security_html += f"""
                <div style="background: rgba(69, 10, 10, 0.3); border: 1px solid rgba(239, 68, 68, 0.3); padding: 12px; margin-bottom: 8px; border-radius: 4px;">
                    <div style="color: #fca5a5; font-weight: bold; font-size: 13px; margin-bottom: 4px;">{issue.get('issue_text', '')}</div>
                    <div style="color: #f87171; font-size: 11px;">Severity: {severity} • Line {issue.get('line_number', '-')}</div>
                </div>
                """
        else:
            security_html = '<p style="color: #94a3b8; font-style: italic;">No security issues found.</p>'

        # Format AI Feedback
        ai_html = ""
        if ai_feedback:
            # Simple markdown-like parsing for bold/headers
            formatted_feedback = ai_feedback.replace("\n", "<br>").replace("**", "<b>").replace("##", "<br><strong>").replace("```", "")
            ai_html = f"""
            <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid #334155; padding: 16px; border-radius: 8px; color: #cbd5e1; font-size: 13px; line-height: 1.6;">
                {formatted_feedback}
            </div>
            """
        else:
            ai_html = '<p style="color: #94a3b8;">No AI feedback available.</p>'

        file_reports.append(f"""
        <div style="background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 24px; margin-bottom: 32px;">
            <h2 style="color: #f8fafc; margin-top: 0; margin-bottom: 20px; font-size: 18px; border-bottom: 1px solid #334155; padding-bottom: 12px;">
                📂 {file_path}
            </h2>

            <h3 style="color: #94a3b8; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px;">Static Analysis</h3>
            {static_html}

            <h3 style="color: #94a3b8; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 24px; margin-bottom: 12px;">Security Risks</h3>
            {security_html}

            <h3 style="color: #818cf8; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 24px; margin-bottom: 12px;">✨ AI Insights</h3>
            {ai_html}
        </div>
        """)

    # Main Template
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; background-color: #0f172a; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #f8fafc;">
        <div style="max-width: 800px; margin: 0 auto; padding: 40px 20px;">
            
            <!-- Header -->
            <div style="text-align: center; margin-bottom: 40px;">
                <h1 style="background: linear-gradient(to right, #818cf8, #22d3ee); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 32px; margin: 0; font-weight: 800;">
                    AI Code Review Report
                </h1>
                <p style="color: #94a3b8; margin-top: 8px;">Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M')}</p>
            </div>

            <!-- Summary Cards -->
            <div style="display: flex; gap: 16px; margin-bottom: 40px;">
                <div style="flex: 1; background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 20px; text-align: center;">
                    <div style="font-size: 32px; font-weight: bold; color: #3b82f6; margin-bottom: 4px;">{total_static}</div>
                    <div style="color: #94a3b8; font-size: 12px; text-transform: uppercase; font-weight: 600;">Static Issues</div>
                </div>
                <div style="flex: 1; background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 20px; text-align: center;">
                    <div style="font-size: 32px; font-weight: bold; color: #ef4444; margin-bottom: 4px;">{total_security}</div>
                    <div style="color: #94a3b8; font-size: 12px; text-transform: uppercase; font-weight: 600;">Security Risks</div>
                </div>
                <div style="flex: 1; background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 20px; text-align: center;">
                    <div style="font-size: 32px; font-weight: bold; color: #10b981; margin-bottom: 4px;">{len(results)}</div>
                    <div style="color: #94a3b8; font-size: 12px; text-transform: uppercase; font-weight: 600;">Files Analyzed</div>
                </div>
            </div>

            <!-- File Reports -->
            {"".join(file_reports)}

            <!-- Footer -->
            <div style="text-align: center; margin-top: 60px; padding-top: 20px; border-top: 1px solid #334155; color: #64748b; font-size: 12px;">
                Generated by AI Code Review Copilot
            </div>
        </div>
    </body>
    </html>
    """
    return html
