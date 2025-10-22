import os
import ast
from git import Repo
import tempfile

def clone_repo(repo_url):
    temp_dir = tempfile.mkdtemp()
    Repo.clone_from(repo_url, temp_dir)
    return temp_dir

def extract_docs_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except Exception:
            return []
    docs = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            docstring = ast.get_docstring(node)
            if docstring:
                docs.append({
                    "type": "class" if isinstance(node, ast.ClassDef) else "function",
                    "name": node.name,
                    "docstring": docstring
                })
    return docs

def analyze_repo(repo_dir):
    all_docs = []
    for root, _, files in os.walk(repo_dir):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                file_docs = extract_docs_from_file(path)
                all_docs.extend(file_docs)
    return all_docs
