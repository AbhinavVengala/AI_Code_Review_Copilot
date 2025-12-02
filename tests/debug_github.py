import os
import glob
import sys
import shutil
import subprocess
from dotenv import load_dotenv

sys.path.append(os.getcwd())

from core.analyzer import analyze_file

def debug_analysis():
    load_dotenv()
    key = os.getenv("GEMINI_API_KEY")
    provider = os.getenv("AI_PROVIDER")
    print(f"DEBUG: AI_PROVIDER = {provider}")
    print(f"DEBUG: GEMINI_API_KEY loaded? {bool(key)}")
    if key:
        print(f"DEBUG: Key length: {len(key)}")

    repo_path = os.path.abspath("temp_clone_test")
    print(f"Debugging analysis for: {repo_path}")
    
    files = glob.glob(os.path.join(repo_path, "**/*.py"), recursive=True)
    print(f"Found {len(files)} files.")
    
    import shutil
    print(f"DEBUG: sys.executable = {sys.executable}")
    print(f"DEBUG: shutil.which('flake8') = {shutil.which('flake8')}")
    
    for file_path in files:
        print(f"\nAnalyzing {file_path}...")
        
        # Test flake8 manually
        cmd = [sys.executable, "-m", "flake8", "--isolated", file_path]
        print(f"Running: {cmd}")
        res = subprocess.run(cmd, capture_output=True, text=True)
        print(f"Manual Flake8 STDOUT: {repr(res.stdout)}")
        print(f"Manual Flake8 STDERR: {repr(res.stderr)}")
        print(f"Manual Flake8 Return: {res.returncode}")
        
        try:
            static, security, feedback, practices = analyze_file(file_path, use_rag=False)
            print("✅ Success!")
            print(f"Static issues: {len(static)}")
            print(f"Security issues: {len(security)}")
            print(f"AI Feedback length: {len(feedback)}")
            print(f"AI Feedback preview: {feedback[:100]}...")
        except Exception as e:
            print(f"❌ Failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_analysis()
