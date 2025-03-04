import os
import zipfile
import requests
import shutil
from flask import Flask, request, jsonify, send_file
import base64

# Hardcoded API Key & Username (⚠️ Security Risk)
GITHUB_TOKEN = "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"
GITHUB_USERNAME = "zuhaibbutt786"

app = Flask(__name__)

# GitHub API Headers
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        project_name = request.form["projectName"]
        zip_file = request.files["file"]

        if not project_name or not zip_file:
            return jsonify({"message": "Missing project name or file"}), 400

        # Save ZIP temporarily
        zip_path = f"{project_name}.zip"
        zip_file.save(zip_path)

        # Extract ZIP
        extract_path = f"./{project_name}"
        os.makedirs(extract_path, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            for member in zip_ref.namelist():
                filename = os.path.basename(member)
                if not filename:
                    continue
                source = zip_ref.open(member)
                target = open(os.path.join(extract_path, filename), "wb")
                with source, target:
                    shutil.copyfileobj(source, target)

        # Delete ZIP file
        os.remove(zip_path)

        # Create GitHub repository
        repo_url = create_github_repo(project_name)
        if not repo_url:
            return jsonify({"message": "Failed to create GitHub repository"}), 500

        # Upload files to GitHub
        upload_files_to_github(project_name, extract_path)

        # Enable GitHub Pages
        enable_github_pages(project_name)

        # Clean up
        shutil.rmtree(extract_path)

        return jsonify({"message": f"Website hosted successfully! View at {repo_url}"})

    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

def create_github_repo(project_name):
    url = "https://api.github.com/user/repos"
    data = {"name": project_name, "private": False, "auto_init": True}

    response = requests.post(url, json=data, headers=HEADERS)
    if response.status_code == 201:
        return f"https://{GITHUB_USERNAME}.github.io/{project_name}"
    else:
        print(f"Failed to create GitHub repository: {response.status_code} - {response.json()}")
    return None

def upload_files_to_github(project_name, folder_path):
    repo = f"{GITHUB_USERNAME}/{project_name}"
    url = f"https://api.github.com/repos/{repo}/contents/"

    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, "rb") as f:
                content = base64.b64encode(f.read()).decode()

            rel_path = os.path.relpath(file_path, folder_path).replace("\\", "/")
            upload_url = f"{url}{rel_path}"

            data = {"message": f"Add {file}", "content": content}
            requests.put(upload_url, json=data, headers=HEADERS)

def enable_github_pages(project_name):
    repo = f"{GITHUB_USERNAME}/{project_name}"
    url = f"https://api.github.com/repos/{repo}/pages"
    data = {"source": {"branch": "main"}}

    requests.post(url, json=data, headers=HEADERS)

if __name__ == "__main__":
    app.run(debug=True)
