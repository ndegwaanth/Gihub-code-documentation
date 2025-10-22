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
    SUPPORTED_EXTENSIONS = [
    ".py",    # Python
    ".js",    # JavaScript
    ".ts",    # TypeScript
    ".java",  # Java
    ".cpp",   # C++
    ".c",     # C
    ".cs",    # C#
    ".rb",    # Ruby
    ".go",    # Go
    ".php",   # PHP
    ".rs",    # Rust
    ".kt",    # Kotlin
    ".swift", # Swift
    ".m",     # Objective-C
    ".scala", # Scala
    ".r",     # R
    ".jl",    # Julia
    ".dart",  # Dart
    ".hs",    # Haskell
    ".sh",    # Shell
    ".jac",   # Jaseci
    ".html",  # HTML
    ".css",   # CSS
    ".xml",   # XML
    ".yml",   # YAML
    ".yaml",  # YAML
    ".json"   # JSON
    ]
    for root, _, files in os.walk(repo_dir):
        for file in files:
            if any(file.endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                path = os.path.join(root, file)
                file_docs = extract_docs_from_file(path)
                all_docs.extend(file_docs)
    return all_docs


def extract_js_docstrings(file_path):
    docs = []
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Extract /** ... */ comments
    import re
    matches = re.findall(r'/\*\*(.*?)\*/', content, re.DOTALL)
    for i, doc in enumerate(matches):
        docs.append({
            "type": "function_or_class",
            "name": f"item_{i}",
            "docstring": doc.strip()
        })
    return docs
