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
