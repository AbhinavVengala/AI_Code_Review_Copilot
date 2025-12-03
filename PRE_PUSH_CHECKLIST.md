# ✅ SAFE TO PUSH - Pre-Deployment Checklist

Run this before pushing to GitHub:

## 🔒 Security Check

```bash
# 1. Verify .env is NOT staged
git status | grep ".env"
# Should NOT appear! If it does, run: git reset .env

# 2. Check for API keys in code
grep -r "GEMINI_API_KEY\|OPENAI_API_KEY" --include="*.py" .
# Should only see os.getenv() calls, NOT actual keys

# 3. Verify sensitive files are ignored
cat .gitignore | grep -E "\.env|dashboard\.db|htmlcov|\.pytest_cache"
```

## ❌ DO NOT PUSH These Files:

- ❌ `.env` - Contains API keys (DANGEROUS!)
- ❌ `dashboard.db` - Database file (if exists)
- ❌ `htmlcov/` - Coverage reports
- ❌ `.pytest_cache/` - Test cache
- ❌ `temp_clone*/` - Temporary clone directories
- ❌ `*.pyc`, `__pycache__/` - Python cache
- ❌ `node_modules/` - Dashboard dependencies
- ❌ `pytest_output_full.txt` - Test debug files
- ❌ `review_report.md` - Generated reports
- ❌ `.DS_Store`, `Thumbs.db` - OS files

## ✅ SAFE TO PUSH:

- ✅ `.env.example` - Template (NO real keys)
- ✅ Source code (`.py` files)
- ✅ `requirements.txt`
- ✅ `README.md`, `DEPLOYMENT.md`
- ✅ `pytest.ini`
- ✅ `tests/` directory
- ✅ `.github/workflows/`
- ✅ `Dockerfile`
- ✅ Configuration files

## 🛡️ Before You Push - Run This:

```bash
# Clean up sensitive/temporary files
git rm --cached .env 2>/dev/null || true
git rm --cached dashboard.db 2>/dev/null || true
git rm --cached pytest_output_full.txt 2>/dev/null || true

# Add all safe files
git add .

# Double check what's being committed
git status

# Look for .env or keys
git diff --staged | grep -i "api_key\|gemini\|openai"
# Should show ONLY os.getenv() calls, not actual keys!

# If all looks good, commit
git commit -m "Add production-ready code with tests and logging"
```

## 🚨 Emergency: If You Accidentally Pushed .env

```bash
# Remove from latest commit
git rm --cached .env
git commit --amend -m "Remove .env file"
git push --force

# THEN IMMEDIATELY:
# 1. Rotate all API keys in .env
# 2. Update keys on deployment platform
# 3. Never use those old keys again
```

## ✅ Current Status Check

Run this to see what will be pushed:
```bash
git status
git diff --staged --name-only
```

Your current changes look good! Safe to push after cleanup.
