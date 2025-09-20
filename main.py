import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

from code_analysis.ast_parser import analyze_code as ast_analyze
from code_analysis.pattern_recognition import detect_patterns
from feedback.severity_classification import SEVERITY_ICONS, provide_feedback
from feedback.best_practice_recommender import recommend_best_practices


try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=os.getenv("GEMINI_API_KEY"))
except Exception:
    llm = None


def run_flake8(file_path):
    """Run flake8 static analysis"""
    result = subprocess.run(
        [sys.executable, "-m", "flake8", file_path, "--format=%(row)d:%(col)d: %(text)s"],
        capture_output=True, text=True
    )
    issues = []
    for line in result.stdout.strip().split("\n"):
        if line:
            parts = line.split(" ", 1)
            location = parts[0]
            text = parts[1] if len(parts) > 1 else ""
            row, col = location.split(":")[0:2]
            issues.append({"line": int(row), "col": int(col), "text": text})
    return issues

def run_bandit(file_path):
    """Run bandit security analysis"""
    result = subprocess.run(
        [sys.executable, "-m", "bandit", "-q", "-r", file_path, "-f", "json"],
        capture_output=True, text=True
    )
    try:
        data = json.loads(result.stdout)
        return data.get("results", [])
    except:
        return []

def extract_snippet(file_path, line_no, context=2):
    """Extract code snippet around a line"""
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
        start = max(0, line_no - context - 1)
        end = min(len(lines), line_no + context)
        snippet = "".join(lines[start:end])
        return f"```python\n{snippet.strip()}\n```"
    except:
        return ""

def ai_review(code_snippet: str) -> str:
    """Generate AI review from Google Gemini"""
    if llm is None:
        return "AI review not available. Google Gemini client not configured."
    prompt = f"""
You are an AI code reviewer. Analyze the following Python code:
- Identify bugs
- Suggest readability and performance improvements
- Highlight best practice violations
- Mention security concerns if any

Code:
{code_snippet}
"""
    try:
        response = llm.invoke(prompt)
        return response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        return f"⚠️ AI review failed: {e}"


def analyze_file(file_path):
    """Run full analysis for a single file"""
    print(f"🔍 Analyzing {file_path}...")
    flake8_issues = run_flake8(file_path)
    bandit_issues = run_bandit(file_path)

    try:
        with open(file_path, "r") as f:
            code = f.read()
        ast_issues = ast_analyze(code)
        pattern_issues = detect_patterns(code)
        combined_issues = flake8_issues + ast_issues + pattern_issues
    except Exception:
        combined_issues = flake8_issues

    ai_feedback = ai_review(code[:1500])
    return combined_issues, bandit_issues, ai_feedback

def generate_report(results):
    """Generate Markdown report"""
    report = []
    report.append("# 🧑‍💻 Intelligent Code Review Report")
    report.append(f"**Generated at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("\n---\n")

    total_static = 0
    total_security = 0

    for file_path, (static_issues, bandit_issues, ai_feedback) in results.items():
        report.append(f"## 📂 File: `{file_path}`")

        report.append("### ✅ Static Analysis (flake8 + AST + Patterns)")
        if static_issues:
            report.append("| Line | Column | Issue | Snippet |")
            report.append("|------|--------|-------|---------|")
            for issue in static_issues[:10]:
                line = issue.get("line", "-")
                col = issue.get("col", "-")
                text = issue.get("text", str(issue))
                snippet = extract_snippet(file_path, line if isinstance(line, int) else 1)
                report.append(f"| {line} | {col} | {text} | {snippet} |")
            total_static += len(static_issues)
        else:
            report.append("- No static issues found.")

        report.append("\n### 🔒 Security Analysis (bandit)")
        if bandit_issues:
            report.append("| Severity | Issue | Line | Snippet |")
            report.append("|----------|-------|------|---------|")
            for issue in sorted(bandit_issues, key=lambda x: x["issue_severity"], reverse=True)[:5]:
                icon = SEVERITY_ICONS.get(issue["issue_severity"], "⚠️")
                snippet = extract_snippet(file_path, issue["line_number"])
                report.append(f"| {icon} {issue['issue_severity']} | {issue['issue_text']} | {issue['line_number']} | {snippet} |")
            total_security += len(bandit_issues)
        else:
            report.append("- No security issues found.")

        report.append("\n### 🤖 AI Suggestions")
        report.append(ai_feedback or "No AI suggestions generated.")
        report.append("\n---\n")

    report.append("## 📌 Summary (All Files)")
    report.append(f"- **Static issues found:** {total_static}")
    report.append(f"- **Security warnings:** {total_security}")
    report.append(f"- **Files analyzed:** {len(results)}")

    return "\n".join(report)

def gather_files(path):
    """Gather Python files from a path"""
    p = Path(path)
    if p.is_file():
        return [str(p)]
    else:
        return [str(f) for f in p.rglob("*.py")]

def main(target_path):
    files = gather_files(target_path)
    results = {}
    for file_path in files:
        static_issues, bandit_issues, ai_feedback = analyze_file(file_path)
        results[file_path] = (static_issues, bandit_issues, ai_feedback)

    report = generate_report(results)
    output_file = "review_report.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n✅ Review completed. Report saved to **{output_file}**")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python review_copilot.py <file_or_folder>")
    else:
        main(sys.argv[1])
