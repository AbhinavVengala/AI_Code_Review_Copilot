import subprocess
from pathlib import Path

def get_changed_files(repo_path: str, commit: str = "HEAD"):
    """
    Returns a list of changed Python files in a commit or branch
    """
    cmd = ["git", "-C", repo_path, "diff", "--name-only", commit]
    result = subprocess.run(cmd, capture_output=True, text=True)
    files = [f.strip() for f in result.stdout.split("\n") if f.endswith(".py")]
    return [str(Path(repo_path) / f) for f in files]
