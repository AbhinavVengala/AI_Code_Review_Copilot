from dotenv import load_dotenv
load_dotenv()

import os, sys, subprocess, json
from pathlib import Path
from datetime import datetime

from code_analysis.ast_parser import analyze_code
from code_analysis.pattern_recognition import detect_patterns
from ml_models.bug_predictor import predict_bug_risk
from feedback.severity_classification import SEVERITY_ICONS, provide_feedback
from feedback.best_practice_recommender import recommend_best_practices
from utils.git_integration import get_changed_files

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", google_api_key=os.getenv("GEMINI_API_KEY"))
except Exception:
    llm = None


FEEDBACK_FILE = "feedback/human_feedback.json"
if not os.path.exists(FEEDBACK_FILE):
    with open(FEEDBACK_FILE, "w") as f:
        json.dump({}, f)


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
    """Extract raw code snippet (no markdown fences)."""
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
        start = max(0, line_no - context - 1)
        end = min(len(lines), line_no + context)
        return "".join(lines[start:end]).strip()
    except Exception:
        return ""


def ai_review(code_snippet: str):
    if llm is None:
        return "AI review not available. Google Gemini client not configured."
    prompt = f"Analyze this code:\n{code_snippet}"
    try:
        response = llm.invoke(prompt)
        return response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        return f"⚠️ AI review failed: {e}"

def save_human_feedback(file_path, issue, feedback):
    """Store human reviewer feedback"""
    with open(FEEDBACK_FILE, "r+") as f:
        data = json.load(f)
        key = f"{file_path}:{issue}"
        data[key] = feedback
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()


def analyze_file(file_path):
    flake8_issues = run_flake8(file_path)
    bandit_issues = run_bandit(file_path)

    with open(file_path, "r") as f:
        code = f.read()

    ast_issues = analyze_code(code)
    pattern_issues = detect_patterns(code)

    combined_issues = flake8_issues + ast_issues + pattern_issues
    for issue in combined_issues:
        issue["severity"] = predict_bug_risk(issue.get("text", ""))

    best_practices = recommend_best_practices(code)

    ai_feedback = ai_review(code[:1500])
    return combined_issues, bandit_issues, ai_feedback, best_practices



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


def gather_files(path):
    p = Path(path)
    if p.is_file():
        return [str(p)]
    else:
        return [str(f) for f in p.rglob("*.py")]

def main(target_path, git_commit=None):
    if git_commit:
        files = get_changed_files(target_path, git_commit)
    else:
        files = gather_files(target_path)

    results = {}
    for file_path in files:
        static_issues, bandit_issues, ai_feedback, best_practices = analyze_file(file_path)
        results[file_path] = (static_issues, bandit_issues, ai_feedback, best_practices)

    report = generate_report(results)
    output_file = "review_report.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n✅ Review completed. Report saved to {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python review_copilot.py <file_or_folder> [git_commit]")
    elif len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        main(sys.argv[1], sys.argv[2])