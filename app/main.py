from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import subprocess
import glob
from pathlib import Path
import tempfile
from app.models import AnalyzeRequest, AnalyzeResponse, Issue, SecurityIssue, GithubAnalyzeRequest
from core.analyzer import analyze_file
from fastapi.responses import StreamingResponse
import json
import asyncio
from utils.email_sender import send_email_report

app = FastAPI(title="AI Code Review Copilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

def _format_response(static_issues, bandit_issues, ai_feedback, best_practices):
    formatted_static = [
        Issue(
            line=i.get("line", 0),
            col=i.get("col", 0),
            text=i.get("text", ""),
            severity=i.get("severity", "LOW")
        ) for i in static_issues
    ]
    
    formatted_security = [
        SecurityIssue(
            severity=i.get("issue_severity", "LOW"),
            issue_text=i.get("issue_text", ""),
            line_number=i.get("line_number", 0)
        ) for i in bandit_issues
    ]
    
    if not isinstance(best_practices, list):
        best_practices = [best_practices] if best_practices else []

    return AnalyzeResponse(
        static_issues=formatted_static,
        security_issues=formatted_security,
        ai_feedback=ai_feedback,
        best_practices=best_practices
    )

def _run_analysis(file_path, use_rag, filename=""):
    static_issues, bandit_issues, ai_feedback, best_practices = analyze_file(file_path, use_rag=use_rag)
    return _format_response(static_issues, bandit_issues, ai_feedback, best_practices)

@app.post("/analyze/upload", response_model=AnalyzeResponse)
async def analyze_upload_endpoint(file: UploadFile = File(...), use_rag: bool = False):
    try:
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(mode="wb", suffix=suffix, delete=False) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        try:
            return _run_analysis(tmp_path, use_rag, filename=file.filename)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/upload-folder", response_model=AnalyzeResponse)
async def analyze_upload_folder_endpoint(files: list[UploadFile] = File(...), use_rag: bool = False):
    try:
        all_static = []
        all_security = []
        all_feedback = []
        all_practices = set()

        # Filter for Python files
        py_files = [f for f in files if f.filename.endswith(".py")]
        
        if not py_files:
             raise HTTPException(status_code=400, detail="No Python files found in the uploaded folder.")

        for file in py_files:
            suffix = Path(file.filename).suffix
            with tempfile.NamedTemporaryFile(mode="wb", suffix=suffix, delete=False) as tmp:
                shutil.copyfileobj(file.file, tmp)
                tmp_path = tmp.name

            try:
                # Analyze
                static, security, feedback, practices = analyze_file(tmp_path, use_rag=use_rag)
                
                # Aggregate
                all_static.extend(static)
                all_security.extend(security)
                
                if feedback:
                    # Deduplicate global API errors
                    if "AI Review Unavailable" in feedback:
                        # Only add if not already present (to avoid spamming every file)
                        if not any("AI Review Unavailable" in f for f in all_feedback):
                            all_feedback.append(feedback)
                    else:
                        all_feedback.append(f"### File: {file.filename}\n{feedback}")

                if practices:
                    all_practices.update(practices)
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        
        return _format_response(all_static, all_security, "\n\n---\n\n".join(all_feedback), list(all_practices))

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_code_endpoint(request: AnalyzeRequest):
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as tmp:
            tmp.write(request.code)
            tmp_path = tmp.name

        try:
            return _run_analysis(tmp_path, request.use_rag)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_github_analysis_background(repo_url: str, email: str, use_rag: bool):
    """
    Background task to analyze GitHub repo and send email.
    """
    print(f"📧 Starting background analysis for {repo_url} -> {email}")
    tmp_dir = tempfile.mkdtemp()
    try:
        # Clone repo
        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"
        
        process = await asyncio.create_subprocess_exec(
            "git", "clone", "--depth", "1", "--single-branch", repo_url, tmp_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )
        await process.communicate()
        
        if process.returncode != 0:
            send_email_report(email, repo_url, "Failed to clone repository.")
            return

        files = glob.glob(os.path.join(tmp_dir, "**/*.py"), recursive=True)
        if not files:
            send_email_report(email, repo_url, "No Python files found in repository.")
            return

        report_lines = []
        for file_path in files:
            try:
                rel_name = os.path.relpath(file_path, tmp_dir)
                static, security, feedback, practices = analyze_file(file_path, use_rag=use_rag)
                
                report_lines.append(f"### File: {rel_name}")
                report_lines.append(f"**Static Issues**: {len(static)}")
                report_lines.append(f"**Security Issues**: {len(security)}")
                report_lines.append("\n**AI Feedback**:")
                report_lines.append(feedback)
                report_lines.append("\n---\n")
            except Exception as e:
                report_lines.append(f"Error analyzing {rel_name}: {str(e)}")

        full_report = "\n".join(report_lines)
        send_email_report(email, repo_url, full_report)
        print(f"✅ Background analysis complete for {repo_url}")

    except Exception as e:
        print(f"❌ Background analysis failed: {e}")
        send_email_report(email, repo_url, f"Analysis failed: {str(e)}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.post("/analyze/github")
async def analyze_github_endpoint(request: GithubAnalyzeRequest, background_tasks: BackgroundTasks):
    # If email is provided, run in background
    if request.email:
        background_tasks.add_task(process_github_analysis_background, request.repo_url, request.email, request.use_rag)
        return {"message": f"Analysis queued. Report will be sent to {request.email}"}

    # Otherwise, stream results
    async def generate():
        tmp_dir = tempfile.mkdtemp()
        try:
            # Clone repo (Shallow clone for speed)
            # GIT_TERMINAL_PROMPT=0 prevents hanging on credential prompts
            env = os.environ.copy()
            env["GIT_TERMINAL_PROMPT"] = "0"
            
            print(f"🔄 Cloning {request.repo_url} to {tmp_dir}...")
            process = await asyncio.create_subprocess_exec(
                "git", "clone", "--depth", "1", "--single-branch", request.repo_url, tmp_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            try:
                # 60 second timeout for cloning
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60.0)
            except asyncio.TimeoutError:
                process.kill()
                yield json.dumps({"error": "Git clone timed out (60s)"}) + "\n"
                return
            
            if process.returncode != 0:
                yield json.dumps({"error": "Failed to clone repository"}) + "\n"
                return

            # Find Python files
            files = glob.glob(os.path.join(tmp_dir, "**/*.py"), recursive=True)
            if not files:
                yield json.dumps({"error": "No Python files found in repository"}) + "\n"
                return

            # Analyze ALL files (streaming)
            for file_path in files:
                try:
                    rel_name = os.path.relpath(file_path, tmp_dir)
                    
                    # Run analysis (synchronous for now, but fast enough per file)
                    static, security, feedback, practices = analyze_file(file_path, use_rag=request.use_rag)
                    
                    # Format result for this single file
                    file_result = {
                        "filename": rel_name,
                        "static_issues": [
                            {
                                "line": i.get("line", 0),
                                "col": i.get("col", 0),
                                "text": i.get("text", ""),
                                "severity": i.get("severity", "LOW")
                            } for i in static
                        ],
                        "security_issues": [
                            {
                                "severity": i.get("issue_severity", "LOW"),
                                "issue_text": i.get("issue_text", ""),
                                "line_number": i.get("line_number", 0)
                            } for i in security
                        ],
                        "ai_feedback": feedback,
                        "best_practices": practices if isinstance(practices, list) else []
                    }
                    
                    yield json.dumps(file_result) + "\n"
                    
                    # Small delay to ensure UI updates smoothly
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    yield json.dumps({"error": f"Error analyzing {rel_name}: {str(e)}"}) + "\n"

        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n"
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    return StreamingResponse(generate(), media_type="application/x-ndjson")
