"""Run tests and save output to file for debugging."""
import subprocess
import sys

# Run pytest and capture output
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_smoke.py", "-v"],
    capture_output=True,
    text=True,
    cwd=r"d:\Abhi\Projects\AI_Code_Review_Copilot"
)

# Write to file
with open("pytest_output_full.txt", "w", encoding="utf-8") as f:
    f.write("STDOUT:\n")
    f.write(result.stdout)
    f.write("\n\nSTDERR:\n")
    f.write(result.stderr)
    f.write(f"\n\nEXIT CODE: {result.returncode}")

print(f"Output saved to pytest_output_full.txt")
print(f"Exit code: {result.returncode}")

# Print last 50 lines
lines = result.stdout.split('\n') + result.stderr.split('\n')
for line in lines[-50:]:
    print(line)
