# 🤖 AI Code Review Copilot

**AI-powered assistant for automated code reviews with ML, security analysis, Git integration, and continuous feedback.**

---

An intelligent code review assistant that automates the process of code analysis by combining static analysis, security scanning, machine learning, and Large Language Models (LLMs) to provide comprehensive feedback. This tool is designed to be a copilot for developers, helping to identify potential issues, improve code quality, and enforce best practices before human review.

## ✨ Features

-   **Multi-faceted Analysis**: Integrates multiple analysis techniques for a holistic review:
    -   **Static Analysis**: Uses `flake8` for style and error checking.
    -   **Security Scanning**: Uses `bandit` to find common security vulnerabilities.
    -   **Advanced Code Analysis**: Employs Abstract Syntax Tree (AST) parsing and pattern recognition for deeper insights.
-   **AI-Powered Suggestions**: Leverages the Google Gemini Pro model to provide contextual, AI-generated feedback and improvement suggestions.
-   **ML-Powered Severity Prediction**: A built-in machine learning model predicts the severity and risk of identified issues.
-   **Comprehensive Reporting**: Generates a clean, detailed Markdown report (`review_report.md`) that summarizes all findings with code snippets, severity levels, and AI suggestions.
-   **Git Integration**: Can be pointed at a specific commit to analyze only the files that have changed.
-   **Human-in-the-Loop**: Includes a mechanism to save human feedback, creating a foundation for a continuous learning system.

## ⚙️ How It Works

The AI Code Review Copilot follows a multi-stage pipeline for each Python file it analyzes:

1.  **File Gathering**: Collects all `.py` files from the target directory or from a specific Git commit.
2.  **Static & Security Analysis**: Runs `flake8` and `bandit` on each file to catch common issues and vulnerabilities.
3.  **Code Intelligence**: Parses the code into an AST and uses custom detectors to find complex patterns and potential bugs.
4.  **ML Severity Prediction**: Each issue found is passed through a machine learning model to classify its severity (e.g., `LOW`, `MEDIUM`, `HIGH`).
5.  **AI Review**: A code snippet is sent to the Google Gemini API, which provides an overall review and suggestions for improvement.
6.  **Report Generation**: All findings are compiled into a single, easy-to-read Markdown report.

## 🚀 Getting Started

### Prerequisites

-   Python 3.9+
-   Git (for commit-based analysis)

### 1. Installation

Clone the repository and install the required Python packages from `requirements.txt`:

```bash
git clone https://github.com/codewithabhi8/AI_Code_Review_Copilot.git
cd AI_Code_Review_Copilot

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configuration

This project uses the Google Gemini API for AI-powered reviews. You will need to obtain an API key and configure it as an environment variable.

1.  Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  Set the environment variable `GEMINI_API_KEY`.

    -   On Windows:
        ```powershell
        $env:GEMINI_API_KEY="your_api_key_here"
        ```
    -   On macOS/Linux:
        ```bash
        export GEMINI_API_KEY="your_api_key_here"
        ```

    To make the key permanent, add it to your system's environment variables or your shell's profile file (e.g., `.bashrc`, `.zshrc`).

### 3. (Optional) Dashboard Configuration

To enable posting results to a central dashboard, set the following environment variables:

-   `DASHBOARD_API_ENDPOINT`: The URL of your dashboard's API endpoint.
-   `DASHBOARD_API_KEY`: The API key for authenticating with your dashboard.

## ▶️ Usage

Run the copilot from the command line, pointing it to a Python file or a directory.

### Analyze a Directory

```bash
python main.py ./path/to/your/code
```

### Analyze a Single File

```bash
python main.py ./path/to/your/file.py
```

### Analyze Changed Files in a Git Commit

To analyze only the Python files changed in a specific Git commit:

```bash
python main.py . <commit-hash>
```

After the analysis is complete, a detailed report named `review_report.md` will be generated in the project's root directory.

## 🧪 Testing the Dashboard Integration

To test the dashboard integration feature locally, you can use the provided mock dashboard server.

### 1. Install Dependencies

Ensure you have installed all dependencies, including `Flask` for the mock server, which is included in `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 2. Start the Mock Dashboard

In your first terminal window, start the mock dashboard server. It will create a `dashboard.db` file to store results and begin listening for requests.

```bash
python mock_dashboard.py
```

You should see a confirmation that the server is running on `http://127.0.0.1:5000`.

### 3. Run the Copilot to Send Data

In a **second terminal window**, configure the environment variables to point to your local mock server and run an analysis:

```bash
export DASHBOARD_API_ENDPOINT="http://127.0.0.1:5000/api/v1/reviews"
export DASHBOARD_API_KEY="supersecretkey"

python main.py ./data/sample_repo
```

### 4. View the Dashboard

Open your web browser and navigate to **http://127.0.0.1:5000/dashboard**. You will see a list of the analysis reports that have been sent to the server. You can click on each report to see a detailed breakdown.

## 📦 Usage as a GitHub Action

You can automate code reviews directly in your repository by using this tool as a GitHub Action. The action will run on every push or pull request to your main branch, and it will upload the `review_report.md` as a build artifact.

### 1. Add the Gemini API Key

In your GitHub repository, go to `Settings` > `Secrets and variables` > `Actions`. Create a new repository secret named `GEMINI_API_KEY` and paste your Google Gemini API key into the value field.

### 2. Create the Workflow File

In your repository, create a new file at `.github/workflows/code-review.yml` and add the following content:

```yaml
name: AI Code Review

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Run AI Code Review
        uses: codewithabhi8/AI_Code_Review_Copilot@main
        with:
          gemini_api_key: ${{ secrets.GEMINI_API_KEY }}
```

## 📄 Sample Report

Here is a condensed example of what a report looks like:

---

# 🧑‍💻 AI Code Review Report

**Generated at:** 2025-09-20 18:30:00

---

## 📂 File: `data/sample_repo/insecure.py`

### ✅ Static Analysis + ML Severity

| Line | Col | Issue         | Severity |
| ---- | --- | ------------- | -------- |
| 2    | 5   | `eval()` used | 🚨 HIGH  |

'''python
def unsafe_eval(user_input):
eval(user_input) # security risk
'''

### 🔒 Security Analysis

| Severity | Issue                     | Line |
| -------- | ------------------------- | ---- |
| ❗ HIGH  | Use of `eval` is insecure | 2    |

### 🤖 AI Suggestions

The use of `eval()` on user-provided input is a significant security vulnerability. A malicious user could execute arbitrary code. Consider using a safer alternative like `ast.literal_eval` for parsing simple data structures, or refactor the logic to avoid evaluating dynamic expressions entirely.

---

## ⚖️ License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---
