# 🧑‍💻 Intelligent Code Review Report

**Generated at:** 2025-09-20 14:41:11

---

## 📂 File: `data\sample_repo\example.py`

### ✅ Static Analysis (flake8 + AST + Patterns)

| Line | Column | Issue                                                     | Snippet   |
| ---- | ------ | --------------------------------------------------------- | --------- |
| 6    | 12     | Pattern: Use of 'eval' detected — potential security risk | ```python |

pass

def unsafe_eval(user_input):
eval(user_input) # Security risk

````|
| 7 | 5 | Pattern: Use of 'eval' detected — potential security risk | ```python
def unsafe_eval(user_input):
    eval(user_input)  # Security risk

def add(a, b):
``` |

### 🔒 Security Analysis (bandit)
- No security issues found.

### 🤖 AI Suggestions
AI review not available. Google Gemini client not configured.

---

## 📂 File: `data\sample_repo\insecure.py`
### ✅ Static Analysis (flake8 + AST + Patterns)
| Line | Column | Issue | Snippet |
|------|--------|-------|---------|
| 1 | 12 | Pattern: Use of 'eval' detected — potential security risk | ```python
def unsafe_eval(user_input):
    eval(user_input)  # security risk
``` |
| 2 | 5 | Pattern: Use of 'eval' detected — potential security risk | ```python
def unsafe_eval(user_input):
    eval(user_input)  # security risk

def delete_file(file_path):
``` |

### 🔒 Security Analysis (bandit)
- No security issues found.

### 🤖 AI Suggestions
AI review not available. Google Gemini client not configured.

---

## 📂 File: `data\sample_repo\main.py`
### ✅ Static Analysis (flake8 + AST + Patterns)
- No static issues found.

### 🔒 Security Analysis (bandit)
- No security issues found.

### 🤖 AI Suggestions
AI review not available. Google Gemini client not configured.

---

## 📂 File: `data\sample_repo\utils.py`
### ✅ Static Analysis (flake8 + AST + Patterns)
- No static issues found.

### 🔒 Security Analysis (bandit)
- No security issues found.

### 🤖 AI Suggestions
AI review not available. Google Gemini client not configured.

---

## 📌 Summary (All Files)
- **Static issues found:** 4
- **Security warnings:** 0
- **Files analyzed:** 4
````
