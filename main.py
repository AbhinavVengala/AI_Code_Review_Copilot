import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

from core.analyzer import analyze_file
from core.report_generator import generate_report
from utils.git_integration import get_changed_files
from utils.knowledge_base import build_index
from utils.github_client import post_pr_comment

load_dotenv()

def gather_files(path):
    p = Path(path)
    if p.is_file():
        return [str(p)]
    else:
        return [str(f) for f in p.rglob("*.py")]

def main():
    parser = argparse.ArgumentParser(description="AI Code Review Copilot")
    parser.add_argument("path", help="Path to file or directory to analyze")
    parser.add_argument("--commit", help="Git commit hash to analyze changed files", default=None)
    parser.add_argument("--deep", action="store_true", help="Enable deep analysis using RAG (requires API tokens)")
    
    args = parser.parse_args()
    target_path = args.path
    
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

    results = {}
    for file_path in files:
        print(f"🔍 Analyzing {file_path}...")
        static_issues, bandit_issues, ai_feedback, best_practices = analyze_file(file_path, use_rag=args.deep)
        results[file_path] = (static_issues, bandit_issues, ai_feedback, best_practices)

    report = generate_report(results)
    output_file = "review_report.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n✅ Review completed. Report saved to {output_file}")

    # Post to GitHub PR if running in Action
    if os.getenv("GITHUB_ACTIONS"):
        post_pr_comment(report)


if __name__ == "__main__":
    main()