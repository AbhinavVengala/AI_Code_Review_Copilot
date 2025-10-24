from dotenv import load_dotenv
load_dotenv()

import os, sys, subprocess, json, tempfile, shutil, requests
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


LANGUAGE_TOOLS = {
    "python": {
        "extensions": [".py"],
        "static_analyzer": "flake8",
        "security_scanner": "bandit",
    },
}

def run_flake8(file_path):
    """Run flake8 static analysis"""
    result = subprocess.run(
        [sys.executable, "-m", "flake8", file_path, "--format=%(row)d:%(col)d: %(text)s"],
        capture_output=True, text=True
    )
    if result.returncode != 0 and result.stdout.strip() == "":
        return []
    issues = []
    for line in result.stdout.strip().split("\n"):
        if line:
            try:
                parts = line.split(":", 2)
                if len(parts) == 3:
                    issues.append({"line": int(parts[0]), "col": int(parts[1]), "text": parts[2].strip()})
            except (ValueError, IndexError):
                continue
    return issues

def run_bandit(file_path):
    """Run bandit security analysis"""
    result = subprocess.run(
        [sys.executable, "-m", "bandit", "-q", file_path, "-f", "json"],
        capture_output=True, text=True
    )
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []
    return data.get("results", [])

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

def post_results_to_dashboard(results_data):
    """Posts the JSON analysis results to a central dashboard API."""
    api_endpoint = os.getenv("DASHBOARD_API_ENDPOINT")
    api_key = os.getenv("DASHBOARD_API_KEY")

    if not api_endpoint or not api_key:
        return

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = list(results_data.values())

    try:
        print("📈 Posting results to dashboard...")
        response = requests.post(api_endpoint, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        print("✅ Results successfully posted to dashboard.")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Warning: Could not post results to dashboard: {e}")


def analyze_file(file_path):
    file_extension = os.path.splitext(file_path)[1]
    language = None
    for lang, config in LANGUAGE_TOOLS.items():
        if file_extension in config["extensions"]:
            language = lang
            break

    if not language:
        return None


    static_issues = []
    security_issues = []
    ast_issues = []
    pattern_issues = []

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    if language == "python":
        static_issues = run_flake8(file_path)
        security_issues = run_bandit(file_path)
        ast_issues = analyze_code(code)
        pattern_issues = detect_patterns(code)

    combined_issues = static_issues + ast_issues + pattern_issues
    for issue in combined_issues:
        issue["severity"] = predict_bug_risk(issue.get("text", ""))

    best_practices = recommend_best_practices(code)
    ai_feedback = ai_review(code[:1500])
    return {
        "static_issues": combined_issues,
        "security": security_issues,
        "ai_feedback": ai_feedback,
        "best_practices": best_practices
    }


def generate_report(results):
    report = []
    report.append("# 🧑‍💻 AI Code Review Report")
    report.append(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("\n---\n")

    total_static = 0
    total_security = 0

    for file_path, analysis_data in results.items():
        report.append(f"## 📂 File: `{analysis_data['relative_path']}`")

        report.append("\n### ✅ Static Analysis + ML Severity")
        if analysis_data["static_issues"]:
            report.append("| Line | Col | Issue | Severity | Snippet |")
            report.append("|------|-----|-------|---------|---------|")
            for issue in analysis_data["static_issues"][:10]:
                severity = issue.get("severity", "LOW")
                icon_text = provide_feedback(issue.get("text", ""), severity) # This function returns a string with icon and severity
                report.append(f"| {issue.get('line','-')} | {issue.get('col','-')} | {issue.get('text','')} | {icon_text} |")
                snippet = extract_snippet(file_path, int(issue.get("line", 1)))
                if snippet:
                    report.append(f"\n```python\n{snippet}\n```\n")
            total_static += len(analysis_data["static_issues"])
        else:
            report.append("- No static issues found.")

        report.append("\n### 🔒 Security Analysis")
        if analysis_data["security"]:
            report.append("| Severity | Issue | Line | Snippet |")
            report.append("|----------|-------|------|---------|")
            for issue in analysis_data["security"][:5]:
                icon = SEVERITY_ICONS.get(issue["issue_severity"], "⚠️")
                snippet = extract_snippet(file_path, issue["line_number"])
                report.append(f"| {icon} {issue['issue_severity']} | {issue['issue_text']} | {issue['line_number']} | {snippet} |")
                if snippet:
                    report.append(f"\n```python\n{snippet}\n```\n")
            total_security += len(analysis_data["security"])
        else:
            report.append("- No security issues found.")

        report.append("\n### 📘 Best Practice Recommendations")
        if analysis_data["best_practices"]:
            if not isinstance(analysis_data["best_practices"], list):
                analysis_data["best_practices"] = [analysis_data["best_practices"]]
            
            for rec in analysis_data["best_practices"]:
                report.append(f"- {rec}")
        else:
            report.append("- No best practice suggestions.")

        report.append("\n### 🤖 AI Suggestions")
        report.append(analysis_data["ai_feedback"] or "No AI suggestions generated.")
        report.append("\n---\n")

    report.append("## 📌 Summary")
    report.append(f"- **Static issues found:** {total_static}")
    report.append(f"- **Security warnings:** {total_security}")
    report.append(f"- **Files analyzed:** {len(results)}")
    return "\n".join(report)


def gather_files(path):
    p = Path(path)
    if p.is_file():
        for lang_config in LANGUAGE_TOOLS.values():
            if p.suffix in lang_config["extensions"]:
                return [str(p)]
        return []
    else:
        all_files = [str(f) for f in p.rglob("*") if not f.is_dir()]
        return [f for f in all_files if os.path.splitext(f)[1] in [ext for conf in LANGUAGE_TOOLS.values() for ext in conf['extensions']]]

def main(target_path, git_commit=None):
    analysis_path = target_path
    temp_dir = None

    try:
        if target_path.startswith(("http://", "https://")) and "github.com" in target_path:
            temp_dir = tempfile.mkdtemp(prefix="ai_code_review_")
            print(f"Cloning repository from {target_path} into {temp_dir}...")
            try:
                subprocess.run(
                    ["git", "clone", "--depth", "1", target_path, "."],
                    check=True, capture_output=True, text=True, cwd=temp_dir
                )
                analysis_path = temp_dir
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to clone repository: {e.stderr}")
                return

        if git_commit:
            files = get_changed_files(analysis_path, git_commit)
        else:
            files = gather_files(analysis_path)

        if not files:
            print(f"❌ No supported files found in the target path: {analysis_path}")
            print("Please check the repository URL or local path.")
            return

        results = {}
        for file_path in files:
            print(f"🔎 Analyzing {os.path.basename(file_path)}...")
            relative_path = os.path.relpath(file_path, analysis_path) if temp_dir else file_path
            if (analysis_results := analyze_file(file_path)):
                analysis_results["relative_path"] = relative_path
                results[file_path] = analysis_results

        report = generate_report(results)
        output_file = "review_report.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n✅ Review completed. Report saved to {output_file}")

        post_results_to_dashboard(results)

    finally:
        if temp_dir:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python review_copilot.py <file_or_folder> [git_commit]")
    elif len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        main(sys.argv[1], sys.argv[2])