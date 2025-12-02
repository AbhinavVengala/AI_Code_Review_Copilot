import os
import json
from github import Github

def post_pr_comment(report_content):
    """
    Posts the review report as a comment on the GitHub PR.
    """
    token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    event_path = os.getenv("GITHUB_EVENT_PATH")

    if not token or not repo_name or not event_path:
        print("⚠️ GitHub environment variables missing. Skipping PR comment.")
        return

    try:
        with open(event_path, "r") as f:
            event_data = json.load(f)
        
        # Check if it's a pull request event
        pr_number = event_data.get("pull_request", {}).get("number")
        if not pr_number:
            print("⚠️ Not a Pull Request event. Skipping comment.")
            return

        g = Github(token)
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        
        # Post the comment
        pr.create_issue_comment(report_content)
        print(f"✅ Posted review report to PR #{pr_number}")

    except Exception as e:
        print(f"❌ Failed to post PR comment: {e}")
