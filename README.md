# 🤖 AI Code Review Copilot

**An intelligent, full-stack code review assistant that combines Static Analysis, Security Scanning, and LLM-based insights.**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Next.js](https://img.shields.io/badge/Next.js-Dashboard-black)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

---

## 🚀 What is this?

The **AI Code Review Copilot** is a next-generation developer tool designed to automate code quality checks. Unlike standard linters, it uses **Retrieval-Augmented Generation (RAG)** to understand the *context* of your project, providing deeper insights than simple syntax checking.

It operates in three modes:
1.  **CLI Tool**: For quick local scans.
2.  **Web Dashboard**: A modern SaaS-like interface for visualizing code health.
3.  **GitHub Action**: Automated PR reviews in your CI/CD pipeline.

## ✨ Key Features

-   **🧠 Context-Aware AI**: Uses Google Gemini Pro + RAG to understand your entire codebase, not just single files.
-   **🛡️ Security First**: Integrated `bandit` scanning to catch vulnerabilities (SQLi, hardcoded secrets, etc.).
-   **📉 Smart Risk Prediction**: Calculates **Cyclomatic Complexity** to mathematically predict bug-prone areas.
-   **🔧 Auto-Fixer**: Doesn't just find bugs—suggests the exact code to fix them.
-   **📊 Visual Dashboard**: A dark-themed Next.js dashboard to track issues and AI feedback.

---

## 🛠️ Installation

### Prerequisites
-   Python 3.9+
-   Node.js 18+ (for Dashboard)
-   Google Gemini API Key ([Get one here](https://aistudio.google.com/app/apikey))

### 1. Clone & Setup
```bash
git clone https://github.com/codewithabhi8/AI_Code_Review_Copilot.git
cd AI_Code_Review_Copilot

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the root directory:

**For Google Gemini (Default)**
```bash
AI_PROVIDER="gemini"
GEMINI_API_KEY="your_google_api_key_here"
```

**For OpenAI (GPT-4)**
```bash
AI_PROVIDER="openai"
OPENAI_API_KEY="sk-..."
```

---

## 🏃‍♂️ Usage

### Option A: Web Dashboard (Recommended)
Run the full-stack application to visualize your code reviews.

**1. Start the Backend (FastAPI)**
```bash
uvicorn app.main:app --reload
```

**2. Start the Frontend (Next.js)**
Open a new terminal:
```bash
cd dashboard
npm install  # First time only
npm run dev
```
Visit **[http://localhost:3000](http://localhost:3000)** to use the tool.

### Option B: Command Line Interface (CLI)
Run quick scans directly from your terminal.

**Standard Scan (Fast & Free)**
Uses static analysis and complexity metrics.
```bash
python main.py ./path/to/your/file_or_folder
```

**Deep Scan (AI + RAG)**
Indexes your codebase for context-aware AI feedback.
```bash
python main.py ./path/to/your/file_or_folder --deep
```

### Option C: GitHub Action
Add this to your repository to automatically review Pull Requests.

Create `.github/workflows/review.yml`:
```yaml
name: AI Code Review
on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run AI Copilot
        uses: codewithabhi8/AI_Code_Review_Copilot@main
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          gemini_api_key: ${{ secrets.GEMINI_API_KEY }}
```

---

## 🏗️ Architecture

-   **Core Engine**: Python (`flake8`, `bandit`, `radon`, `langchain`)
-   **Backend**: FastAPI
-   **Frontend**: Next.js + Tailwind CSS
-   **Database (Vector)**: ChromaDB (for RAG)
-   **LLM**: Google Gemini 1.5 Flash

---

## 📄 License
MIT License. Free to use for personal and commercial projects.
