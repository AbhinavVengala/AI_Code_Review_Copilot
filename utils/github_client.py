import os
import json
from github import Github
from core.logging_config import get_logger

logger = get_logger(__name__)

def post_pr_comment(report_content):
    """
    Posts the review report as a comment on the GitHub PR.
    """
    token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    event_path = os.getenv("GITHUB_EVENT_PATH")

    if not token or not repo_name or not event_path:
        logger.warning("github_pr_comment_skipped", reason="missing_environment_variables")
        return

    try:
        with open(event_path, "r") as f:
            event_data = json.load(f)
        
        # Check if it's a pull request event
        pr_number = event_data.get("pull_request", {}).get("number")
        if not pr_number:
            logger.info("github_pr_comment_skipped", reason="not_pr_event")
            return

        g = Github(token)
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        
        # Post the comment
        pr.create_issue_comment(report_content)
        logger.info("github_pr_comment_posted", pr_number=pr_number, repo=repo_name)

    except Exception as e:
        logger.error("github_pr_comment_failed", error=str(e), exc_info=True)
