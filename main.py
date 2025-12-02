import os
import sys
import argparse
import json
import subprocess
import tempfile
import shutil
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from core.analyzer import analyze_file
from core.report_generator import generate_report
from utils.git_integration import get_changed_files
from utils.knowledge_base import build_index
from utils.github_client import post_pr_comment

LANGUAGE_TOOLS = {
    "python": {
        "extensions": [".py"],
        "static_analyzer": "flake8",
        "security_scanner": "bandit",
    },
}

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

def post_results_to_dashboard(results):
    """Posts the analysis results to a central dashboard API."""
    api_endpoint = os.getenv("DASHBOARD_API_ENDPOINT")
    api_key = os.getenv("DASHBOARD_API_KEY")

    if not api_endpoint or not api_key:
        return

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # Convert results (path -> tuple) to list of dicts for dashboard
    payload = []
    for file_path, (static_issues, bandit_issues, ai_feedback, best_practices) in results.items():
        payload.append({
            "file_path": file_path,
            "static_issues": static_issues,
            "security": bandit_issues,
            "ai_feedback": ai_feedback,
            "best_practices": best_practices
        })

    try:
        print("📈 Posting results to dashboard...")
        response = requests.post(api_endpoint, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        print("✅ Results successfully posted to dashboard.")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Warning: Could not post results to dashboard: {e}")

def main():
    parser = argparse.ArgumentParser(description="AI Code Review Copilot")
    parser.add_argument("path", help="Path to file or directory to analyze, or a Git repository URL")
    parser.add_argument("--commit", help="Git commit hash to analyze changed files", default=None)
    parser.add_argument("--deep", action="store_true", help="Enable deep analysis using RAG (requires API tokens)")
    
    args = parser.parse_args()
    target_path = args.path
    temp_dir = None
    
    try:
        # Handle Git URL
        if target_path.startswith(("http://", "https://")) and "github.com" in target_path:
            temp_dir = tempfile.mkdtemp(prefix="ai_code_review_")
            print(f"Cloning repository from {target_path} into {temp_dir}...")
            try:
                subprocess.run(
                    ["git", "clone", "--depth", "1", target_path, "."],
                    check=True, capture_output=True, text=True, cwd=temp_dir
                )
                target_path = temp_dir
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to clone repository: {e.stderr}")
                return

        # Build RAG index if deep mode is enabled
        if args.deep:
            if os.path.isdir(target_path):
                build_index(target_path)
            else:
                # If analyzing a single file, index its parent directory
                build_index(os.path.dirname(os.path.abspath(target_path)))

        if args.commit:
            files = get_changed_files(target_path, args.commit)
        else:
            files = gather_files(target_path)

        if not files:
            print(f"❌ No supported files found in the target path: {target_path}")
            return

        results = {}
        for file_path in files:
            print(f"🔍 Analyzing {file_path}...")
            # analyze_file returns: combined_issues, bandit_issues, ai_feedback, best_practices
            analysis_result = analyze_file(file_path, use_rag=args.deep)
            results[file_path] = analysis_result

        # Generate and save report
        report = generate_report(results)
        output_file = "review_report.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n✅ Review completed. Report saved to {output_file}")

        # Post to dashboard
        post_results_to_dashboard(results)

        # Post to GitHub PR if running in Action
        if os.getenv("GITHUB_ACTIONS"):
            post_pr_comment(report)

    finally:
        if temp_dir:
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()