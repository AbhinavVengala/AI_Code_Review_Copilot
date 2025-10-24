# 🧑‍💻 AI Code Review Report
Generated at: 2025-10-11 19:15:20

---

## 📂 File: `data/sample_repo/insecure.py`

### ✅ Static Analysis + ML Severity
| Line | Col | Issue | Severity | Snippet |
|------|-----|-------|---------|---------|
| 4 | 1 | expected 2 blank lines, found 1 | 🔴 [HIGH] expected 2 blank lines, found 1 |

```python
eval(user_input)  # security risk

def delete_file(file_path):
    import os
    os.remove(file_path)  # potentially dangerous
```

| 1 | 12 | Pattern: Use of 'eval' detected — potential security risk | 🟠 [MEDIUM] Pattern: Use of 'eval' detected — potential security risk |

```python
def unsafe_eval(user_input):
    eval(user_input)  # security risk
```

| 2 | 5 | Pattern: Use of 'eval' detected — potential security risk | 🟡 [LOW] Pattern: Use of 'eval' detected — potential security risk |

```python
def unsafe_eval(user_input):
    eval(user_input)  # security risk

def delete_file(file_path):
```


### 🔒 Security Analysis
| Severity | Issue | Line | Snippet |
|----------|-------|------|---------|
| 🟠 MEDIUM | Use of possibly insecure function - consider using safer ast.literal_eval. | 2 | def unsafe_eval(user_input):
    eval(user_input)  # security risk

def delete_file(file_path): |

```python
def unsafe_eval(user_input):
    eval(user_input)  # security risk

def delete_file(file_path):
```


### 📘 Best Practice Recommendations
- Avoid using eval(); consider safer alternatives like ast.literal_eval.
- Add docstrings to functions for better maintainability.

### 🤖 AI Suggestions
AI review not available. Google Gemini client not configured.

---

## 📂 File: `data/sample_repo/example.py`

### ✅ Static Analysis + ML Severity
| Line | Col | Issue | Severity | Snippet |
|------|-----|-------|---------|---------|
| 1 | 1 | 'os' imported but unused | 🔴 [HIGH] 'os' imported but unused |

```python
import os

def empty_function():
```

| 3 | 1 | expected 2 blank lines, found 1 | 🟡 [LOW] expected 2 blank lines, found 1 |

```python
import os

def empty_function():
    pass
```

| 6 | 1 | expected 2 blank lines, found 1 | 🟠 [MEDIUM] expected 2 blank lines, found 1 |

```python
pass

def unsafe_eval(user_input):
    eval(user_input)  # Security risk
```

| 9 | 1 | expected 2 blank lines, found 1 | 🔴 [HIGH] expected 2 blank lines, found 1 |

```python
eval(user_input)  # Security risk

def add(a, b):
    return a+b
```

| 12 | 1 | expected 2 blank lines after class or function definition, found 1 | 🟡 [LOW] expected 2 blank lines after class or function definition, found 1 |

```python
return a+b

print(add(2, 3))
```

| 6 | 12 | Pattern: Use of 'eval' detected — potential security risk | 🟠 [MEDIUM] Pattern: Use of 'eval' detected — potential security risk |

```python
pass

def unsafe_eval(user_input):
    eval(user_input)  # Security risk
```

| 7 | 5 | Pattern: Use of 'eval' detected — potential security risk | 🔴 [HIGH] Pattern: Use of 'eval' detected — potential security risk |

```python
def unsafe_eval(user_input):
    eval(user_input)  # Security risk

def add(a, b):
```


### 🔒 Security Analysis
| Severity | Issue | Line | Snippet |
|----------|-------|------|---------|
| 🟠 MEDIUM | Use of possibly insecure function - consider using safer ast.literal_eval. | 7 | def unsafe_eval(user_input):
    eval(user_input)  # Security risk

def add(a, b): |

```python
def unsafe_eval(user_input):
    eval(user_input)  # Security risk

def add(a, b):
```


### 📘 Best Practice Recommendations
- Avoid using eval(); consider safer alternatives like ast.literal_eval.
- Add docstrings to functions for better maintainability.

### 🤖 AI Suggestions
AI review not available. Google Gemini client not configured.

---

## 📂 File: `data/sample_repo/utils.py`

### ✅ Static Analysis + ML Severity
| Line | Col | Issue | Severity | Snippet |
|------|-----|-------|---------|---------|
| 4 | 1 | expected 2 blank lines, found 1 | 🔴 [HIGH] expected 2 blank lines, found 1 |

```python
pass

def add_numbers(a,b):
    return a+b
```

| 4 | 18 | missing whitespace after ',' | 🟡 [LOW] missing whitespace after ',' |

```python
pass

def add_numbers(a,b):
    return a+b
```

| 7 | 1 | expected 2 blank lines, found 1 | 🟠 [MEDIUM] expected 2 blank lines, found 1 |

```python
return a+b

def multiply_numbers(a,b):
    return a * b
```

| 7 | 23 | missing whitespace after ',' | 🔴 [HIGH] missing whitespace after ',' |

```python
return a+b

def multiply_numbers(a,b):
    return a * b
```


### 🔒 Security Analysis
- No security issues found.

### 📘 Best Practice Recommendations
- Add docstrings to functions for better maintainability.

### 🤖 AI Suggestions
AI review not available. Google Gemini client not configured.

---

## 📂 File: `data/sample_repo/main.py`

### ✅ Static Analysis + ML Severity
| Line | Col | Issue | Severity | Snippet |
|------|-----|-------|---------|---------|
| 3 | 20 | missing whitespace after ',' | 🟡 [LOW] missing whitespace after ',' |

```python
from utils import add_numbers, multiply_numbers

print(add_numbers(2,3))
print(multiply_numbers(4,5))
```

| 4 | 25 | missing whitespace after ',' | 🟡 [LOW] missing whitespace after ',' |

```python
print(add_numbers(2,3))
print(multiply_numbers(4,5))
```


### 🔒 Security Analysis
- No security issues found.

### 📘 Best Practice Recommendations
- Follow coding standards and best practices.

### 🤖 AI Suggestions
AI review not available. Google Gemini client not configured.

---

## 📌 Summary
- **Static issues found:** 16
- **Security warnings:** 2
- **Files analyzed:** 4