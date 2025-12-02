import requests
import os

BASE_URL = "http://localhost:8000"

def test_upload():
    print("Testing /analyze/upload...")
    # Create a dummy file
    with open("temp_test.py", "w") as f:
        f.write("def foo():\n    print('hello')\n")
    
    try:
        with open("temp_test.py", "rb") as f:
            files = {"file": ("temp_test.py", f, "text/x-python")}
            response = requests.post(f"{BASE_URL}/analyze/upload", files=files)
        
        if response.status_code == 200:
            print("✅ Upload test passed!")
            print(response.json().keys())
        else:
            print(f"❌ Upload test failed: {response.text}")
    finally:
        if os.path.exists("temp_test.py"):
            os.remove("temp_test.py")

def test_github():
    print("\nTesting /analyze/github...")
    # Use a small repo or a dummy one that might fail cloning but prove endpoint exists
    # Using a non-existent repo to check error handling (should be 400 or 500)
    # Or use a real one if possible. Let's try a known small one.
    # https://github.com/kennethreitz/samplemod is small.
    repo_url = "https://github.com/kennethreitz/samplemod"
    
    response = requests.post(f"{BASE_URL}/analyze/github", json={"repo_url": repo_url})
    
    if response.status_code == 200:
        print("✅ GitHub test passed!")
        data = response.json()
        print(f"Issues found: {len(data['static_issues'])}")
    else:
        print(f"❌ GitHub test failed (might be expected if git not found or network issue): {response.status_code} {response.text}")

if __name__ == "__main__":
    try:
        test_upload()
        test_github()
    except Exception as e:
        print(f"❌ Test script failed: {e}")
