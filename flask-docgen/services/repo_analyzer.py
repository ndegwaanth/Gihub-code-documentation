import os
import ast
import re
import json
import tempfile
from git import Repo


# ---------------------------
# 1. Clone Repository
# ---------------------------
def clone_repo(repo_url):
    temp_dir = tempfile.mkdtemp()
    Repo.clone_from(repo_url, temp_dir)
    return temp_dir


# ---------------------------
# 2. Extractors per Language
# ---------------------------

def extract_python_docs(file_path):
    """Extract Python functions, classes, and docstrings."""
    docs = []
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except Exception:
            return []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            docs.append({
                "language": "Python",
                "type": "class" if isinstance(node, ast.ClassDef) else "function",
                "name": node.name,
                "docstring": ast.get_docstring(node) or "No docstring provided"
            })
    return docs


def extract_js_ts_docs(file_path):
    """Extract JS/TS functions and classes using syntax patterns."""
    docs = []
    content = open(file_path, "r", encoding="utf-8").read()

    function_patterns = [
        r'function\s+(\w+)\s*\(',                # function name() {}
        r'(\w+)\s*=\s*\(.*?\)\s*=>',            # const name = (...) => {}
        r'class\s+(\w+)\s*{',                   # class Name {}
    ]
    for pattern in function_patterns:
        for match in re.findall(pattern, content):
            docs.append({
                "language": "JavaScript/TypeScript",
                "type": "declaration",
                "name": match,
                "docstring": "Detected via syntax"
            })
    return docs


def extract_java_like_docs(file_path, language_name):
    """Extract methods and classes for C-like syntaxes (Java, C, C++, C#, Kotlin, Swift, Go)."""
    docs = []
    content = open(file_path, "r", encoding="utf-8", errors="ignore").read()

    patterns = [
        r'class\s+(\w+)',                        # class ClassName
        r'(?:public|private|protected)?\s*\w+\s+(\w+)\s*\([^)]*\)\s*\{',  # returnType name(args)
    ]

    for pattern in patterns:
        for match in re.findall(pattern, content):
            docs.append({
                "language": language_name,
                "type": "method_or_class",
                "name": match,
                "docstring": "Parsed from syntax"
            })
    return docs


def extract_php_docs(file_path):
    """Extract PHP functions and classes."""
    docs = []
    content = open(file_path, "r", encoding="utf-8", errors="ignore").read()

    patterns = [
        r'class\s+(\w+)',
        r'function\s+(\w+)\s*\('
    ]
    for pattern in patterns:
        for match in re.findall(pattern, content):
            docs.append({
                "language": "PHP",
                "type": "class_or_function",
                "name": match,
                "docstring": "Parsed from syntax"
            })
    return docs


def extract_ruby_docs(file_path):
    """Extract Ruby methods and classes."""
    docs = []
    content = open(file_path, "r", encoding="utf-8", errors="ignore").read()
    for match in re.findall(r'(?:def|class)\s+(\w+)', content):
        docs.append({
            "language": "Ruby",
            "type": "definition",
            "name": match,
            "docstring": "Parsed from syntax"
        })
    return docs


def extract_go_docs(file_path):
    """Extract Go functions and methods."""
    docs = []
    content = open(file_path, "r", encoding="utf-8", errors="ignore").read()
    for match in re.findall(r'func\s+(\w+)', content):
        docs.append({
            "language": "Go",
            "type": "function",
            "name": match,
            "docstring": "Parsed from syntax"
        })
    return docs


def extract_rust_docs(file_path):
    """Extract Rust functions, structs, and impls."""
    docs = []
    content = open(file_path, "r", encoding="utf-8", errors="ignore").read()
    patterns = [r'fn\s+(\w+)', r'struct\s+(\w+)', r'impl\s+(\w+)']
    for pattern in patterns:
        for match in re.findall(pattern, content):
            docs.append({
                "language": "Rust",
                "type": "definition",
                "name": match,
                "docstring": "Parsed from syntax"
            })
    return docs


def extract_html_docs(file_path):
    """Extract HTML tags and comments."""
    docs = []
    content = open(file_path, "r", encoding="utf-8", errors="ignore").read()
    tags = re.findall(r'<(\w+)', content)
    comments = re.findall(r'<!--(.*?)-->', content, re.DOTALL)
    docs.append({
        "language": "HTML",
        "type": "tags",
        "name": f"{len(tags)} tags found",
        "docstring": ", ".join(set(tags))
    })
    for i, c in enumerate(comments):
        docs.append({
            "language": "HTML",
            "type": "comment",
            "name": f"comment_{i}",
            "docstring": c.strip()
        })
    return docs


def extract_css_docs(file_path):
    """Extract CSS selectors and rules."""
    docs = []
    content = open(file_path, "r", encoding="utf-8", errors="ignore").read()
    selectors = re.findall(r'([.#]?\w[\w-]*)\s*{', content)
    if selectors:
        docs.append({
            "language": "CSS",
            "type": "selector",
            "name": f"{len(selectors)} selectors found",
            "docstring": ", ".join(set(selectors))
        })
    return docs


def extract_json_yaml_docs(file_path):
    """Load JSON/YAML and extract top-level keys."""
    try:
        content = open(file_path, "r", encoding="utf-8").read()
        data = json.loads(content)
        keys = list(data.keys())
        return [{
            "language": "JSON/YAML",
            "type": "data_keys",
            "name": os.path.basename(file_path),
            "docstring": f"Top-level keys: {keys}"
        }]
    except Exception:
        return [{
            "language": "YAML/Plain",
            "type": "text",
            "name": os.path.basename(file_path),
            "docstring": "Non-JSON text content"
        }]


def extract_shell_docs(file_path):
    """Extract shell functions and variables."""
    docs = []
    content = open(file_path, "r", encoding="utf-8", errors="ignore").read()
    functions = re.findall(r'(\w+)\s*\(\)\s*{', content)
    for func in functions:
        docs.append({
            "language": "Shell",
            "type": "function",
            "name": func,
            "docstring": "Parsed from shell syntax"
        })
    return docs


def extract_jac_docs(file_path):
    """Extract Jaseci walkers, actions, and nodes."""
    docs = []
    content = open(file_path, "r", encoding="utf-8").read()
    patterns = [r'walker\s+(\w+)', r'action\s+(\w+)', r'node\s+(\w+)']
    for pattern in patterns:
        for match in re.findall(pattern, content):
            docs.append({
                "language": "Jaseci",
                "type": "construct",
                "name": match,
                "docstring": "Parsed from syntax"
            })
    return docs


# ---------------------------
# 3. Unified Dispatcher
# ---------------------------
def extract_docs_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    dispatch_map = {
        ".py": extract_python_docs,
        ".js": extract_js_ts_docs,
        ".ts": extract_js_ts_docs,
        ".java": lambda f: extract_java_like_docs(f, "Java"),
        ".cpp": lambda f: extract_java_like_docs(f, "C++"),
        ".c": lambda f: extract_java_like_docs(f, "C"),
        ".cs": lambda f: extract_java_like_docs(f, "C#"),
        ".go": extract_go_docs,
        ".php": extract_php_docs,
        ".rb": extract_ruby_docs,
        ".rs": extract_rust_docs,
        ".kt": lambda f: extract_java_like_docs(f, "Kotlin"),
        ".swift": lambda f: extract_java_like_docs(f, "Swift"),
        ".m": lambda f: extract_java_like_docs(f, "Objective-C"),
        ".scala": lambda f: extract_java_like_docs(f, "Scala"),
        ".dart": lambda f: extract_java_like_docs(f, "Dart"),
        ".hs": lambda f: extract_java_like_docs(f, "Haskell"),
        ".html": extract_html_docs,
        ".css": extract_css_docs,
        ".xml": extract_html_docs,
        ".json": extract_json_yaml_docs,
        ".yaml": extract_json_yaml_docs,
        ".yml": extract_json_yaml_docs,
        ".sh": extract_shell_docs,
        ".jac": extract_jac_docs,
    }

    if ext in dispatch_map:
        return dispatch_map[ext](file_path)
    return []


# ---------------------------
# 4. Analyze Repository
# ---------------------------
def analyze_repo(repo_dir):
    all_docs = []
    SUPPORTED_EXTENSIONS = [
        ".py", ".js", ".ts", ".java", ".cpp", ".c", ".cs", ".rb", ".go", ".php", ".rs",
        ".kt", ".swift", ".m", ".scala", ".r", ".jl", ".dart", ".hs", ".sh", ".jac",
        ".html", ".css", ".xml", ".yml", ".yaml", ".json"
    ]
    for root, _, files in os.walk(repo_dir):
        for file in files:
            if any(file.endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                path = os.path.join(root, file)
                all_docs.extend(extract_docs_from_file(path))
    return all_docs
