import os
import sys
import subprocess
import json
from dotenv import load_dotenv

from code_analysis.ast_parser import analyze_code
from code_analysis.pattern_recognition import detect_patterns
from ml_models.bug_predictor import analyze_complexity, predict_risk_for_line
from feedback.best_practice_recommender import recommend_best_practices
from utils.knowledge_base import retrieve_context

load_dotenv()

from core.llm_factory import get_llm

load_dotenv()

# LLM is initialized lazily in ai_review to allow env var changes to take effect if needed
# or just to keep module load fast.

def run_flake8(file_path):
    import shutil
    flake8_cmd = shutil.which("flake8")
    if flake8_cmd:
        cmd = [flake8_cmd, "--isolated", file_path, "--format=%(row)d:%(col)d: %(text)s"]
    else:
        cmd = [sys.executable, "-m", "flake8", "--isolated", file_path, "--format=%(row)d:%(col)d: %(text)s"]
    
    result = subprocess.run(
        cmd,
        capture_output=True, text=True
    )
    
    issues = []
    import re
    # Regex to match "line:col: message"
    pattern = re.compile(r"^(\d+):(\d+):\s*(.*)$")
    
    for line in result.stdout.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
            
        match = pattern.match(line)
        if match:
            row, col, text = match.groups()
            issues.append({
                "line": int(row),
                "col": int(col),
                "text": text
            })
    
    print(f"DEBUG ISSUES FOUND: {len(issues)}")
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

def ai_review(code_snippet: str, context: str = ""):
    llm = get_llm()
    if llm is None:
        return "AI review not available. Check AI_PROVIDER and API keys."
    
    prompt = f"""
    You are an expert Senior Software Engineer. Review the following Python code.
    
    CONTEXT (from other files):
    {context}
    
    CODE TO REVIEW:
    {code_snippet}
    
    INSTRUCTIONS:
    1. Identify potential bugs, security risks, or performance issues.
    2. If you find an issue, provide the FIXED CODE snippet.
    3. Be concise.
    """
    try:
        response = llm.invoke(prompt)
        return response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        error_msg = str(e)
        if "API Key not found" in error_msg or "400" in error_msg:
            return "⚠️ **AI Review Unavailable**: Invalid or missing API Key. Please check your `.env` file and ensure `GEMINI_API_KEY` is set correctly."
        return f"⚠️ AI review failed: {error_msg}"

def analyze_file(file_path, use_rag=False):
    flake8_issues = run_flake8(file_path)
    bandit_issues = run_bandit(file_path)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
    except UnicodeDecodeError:
        return [], [], "Error reading file (encoding)", []

    ast_issues = analyze_code(code)
    pattern_issues = detect_patterns(code)
    
    # Calculate complexity for the whole file
    complexity_blocks = analyze_complexity(code)

    combined_issues = flake8_issues + ast_issues + pattern_issues
    for issue in combined_issues:
        issue["severity"] = predict_risk_for_line(complexity_blocks, issue.get("line", 0))

    best_practices = recommend_best_practices(code)

    # RAG Context Retrieval
    context = ""
    if use_rag:
        # Retrieve context relevant to the first few lines or the whole file summary
        context = retrieve_context(code[:500])

    ai_feedback = ai_review(code[:1500], context)
    return combined_issues, bandit_issues, ai_feedback, best_practices
