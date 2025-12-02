import json
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

TEST_API_KEY = "supersecretkey"
DATABASE = "dashboard.db"

def init_db():
    """Initialize the SQLite database."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                report_data TEXT NOT NULL
            );
        """)
        conn.commit()

@app.route('/')
def index():
    """A simple welcome page to confirm the server is running."""
    return """
    <h1>🚀 Mock Dashboard API is running!</h1>
    <p>This server is listening for POST requests at <code>/api/v1/reviews</code>.</p>
    <p>Run the main script in another terminal to send analysis data here.</p>
    <p><strong><a href="/dashboard">Click here to view the Dashboard</a></strong></p>
    """

@app.route('/dashboard')
def dashboard():
    """A simple page to display stored review data."""
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, received_at, report_data FROM reviews ORDER BY received_at DESC")
        reviews = cursor.fetchall()

    html = """
    <head>
        <title>Code Review Dashboard</title>
        <style>
            body { font-family: sans-serif; margin: 2em; background-color: #f9f9f9; color: #333; }
            h1, h2, h3 { color: #111; }
            a { color: #0056b3; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .report-summary { border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 8px; background-color: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        </style>
    </head>
    <body>
    <h1>Code Review Dashboard</h1>
    """
    if not reviews:
        html += "<p>No reports received yet.</p>"
        html += "</body>"
        return html

    for review in reviews:
        report_data = json.loads(review["report_data"])
        num_files = len(report_data)
        total_static = sum(len(file_data.get('static_issues', [])) for file_data in report_data)
        total_security = sum(len(file_data.get('security', [])) for file_data in report_data)

        html += f"""
        <div class="report-summary">
            <h3><a href="/report/{review['id']}">Report #{review['id']} - Received at {review['received_at']}</a></h3>
            <p>Analyzed {num_files} files.</p>
            <p><strong>Total Static Issues: {total_static}</strong> | <strong>Total Security Issues: {total_security}</strong></p>
        </div>"""
    html += "</body>"
    return html

@app.route('/report/<int:report_id>')
def report_detail(report_id):
    """Displays the full details of a single analysis report."""
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT report_data FROM reviews WHERE id = ?", (report_id,))
        review = cursor.fetchone()

    if not review:
        return "Report not found.", 404

    report_data = json.loads(review["report_data"])
    html = f"""
    <head>
        <title>Report #{report_id}</title>
        <style>
            body {{ font-family: sans-serif; margin: 2em; }}
            .file-report {{ border: 1px solid #ddd; padding: 15px; margin-bottom: 20px; border-radius: 8px; }}
            h1, h2, h3 {{ color: #111; }}
            code {{ background-color: #eee; padding: 2px 4px; border-radius: 3px; }}
            ul {{ padding-left: 20px; }}
        </style>
    </head>
    <body>
    <h1><a href="/dashboard">Dashboard</a> &gt; Report #{report_id}</h1>
    """

    for file_data in report_data:
        html += f"<div class='file-report'><h2>File: <code>{file_data['relative_path']}</code></h2>"
        html += "<h3>Static Analysis Issues</h3><ul>"
        if file_data['static_issues']:
            for issue in file_data['static_issues']:
                html += f"<li>Line {issue['line']}: {issue['text']} (Severity: {issue['severity']})</li>"
        else:
            html += "<li>No static issues found.</li>"
        html += "</ul>"

        html += "<h3>Security Issues</h3><ul>"
        if file_data['security']:
            for issue in file_data['security']:
                html += f"<li>Line {issue['line_number']}: {issue['issue_text']} (Severity: {issue['issue_severity']})</li>"
        else:
            html += "<li>No security issues found.</li>"
        html += "</ul></div>"

    html += "</body>"
    return html

@app.route('/api/v1/reviews', methods=['POST'])
def receive_review():
    """Endpoint to receive code review data."""
    auth_header = request.headers.get('Authorization')
    expected_header = f"Bearer {TEST_API_KEY}"

    if not auth_header or auth_header.strip() != expected_header:
        print(f"❌ Unauthorized attempt with token: {auth_header}")
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO reviews (report_data) VALUES (?)", (json.dumps(data),))
        conn.commit()

    print("\n✅ Successfully received analysis data from copilot:")
    print(json.dumps(data, indent=2))
    return jsonify({"message": "Data received successfully"}), 201

if __name__ == '__main__':
    init_db()
    print("🚀 Mock Dashboard API started at http://127.0.0.1:5000")
    print("Listening for POST requests at /api/v1/reviews...")
    app.run(port=5000)