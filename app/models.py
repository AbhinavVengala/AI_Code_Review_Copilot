from pydantic import BaseModel
from typing import List, Optional

class Issue(BaseModel):
    line: int
    col: int
    text: str
    severity: str

class SecurityIssue(BaseModel):
    severity: str
    issue_text: str
    line_number: int

class AnalyzeRequest(BaseModel):
    code: str
    use_rag: bool = False

class GithubAnalyzeRequest(BaseModel):
    repo_url: str
    use_rag: bool = False
    email: Optional[str] = None

class AnalyzeResponse(BaseModel):
    static_issues: List[Issue]
    security_issues: List[SecurityIssue]
    ai_feedback: str
    best_practices: List[str]
