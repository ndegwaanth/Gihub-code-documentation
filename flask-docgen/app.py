from flask import Flask, request, render_template, jsonify
from openai import OpenAI
from config import Config
from services.repo_analyzer import clone_repo, analyze_repo
from services.doc_generator import generate_rmarkdown

app = Flask(__name__)
app.config.from_object(Config)

# Initialize OpenRouter API client
client = OpenAI(
    base_url=Config.BASE_URL,
    api_key=Config.OPENROUTER_API_KEY,
)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        repo_url = request.form.get("repo_url")
        repo_dir = clone_repo(repo_url)
        docs = analyze_repo(repo_dir)
        rmd_content = generate_rmarkdown(docs)

        # Summarize using DeepSeek / OpenRouter model
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://yourwebsite.com",
                "X-Title": "Flask Doc Generator"
            },
            model="deepseek/deepseek-chat",
            messages = [
                {
                    "role": "system",
                    "content": """You are an advanced documentation generator that produces professional, detailed RMarkdown documentation
            for GitHub repositories. Format your output in rich RMarkdown style, including:

            - YAML header for metadata
            - Collapsible sections using HTML <details> and <summary> tags
            - Tables for summarizing components
            - Syntax-highlighted code blocks
            - Markdown badges or highlights for emphasis
            - 'Callout' sections for notes, warnings, or important info
            - Include a comprehensive 'Technologies Used' section listing all programming languages, frameworks, and libraries found in the repository

            Example structure:
            ---
            title: "Comprehensive Documentation for <Project Name>"
            author: "AI Documentation Generator"
            date: "`r Sys.Date()`"
            output:
            html_document:
                toc: true
                toc_depth: 3
                toc_float: true
            ---

            # Overview
            <High-level explanation>

            # Architecture
            <Flowchart or component table>

            # Key Modules
            <detailed sections with code snippets>

            # How It Works
            <step-by-step explanation>

            # Technologies Used
            <List all programming languages, frameworks, libraries, and tools utilized in the repository>

            # Importance and Use Cases
            <business and technical significance>

            # Conclusion
            <final thoughts or references>

            Use elegant formatting, clear structure, and ensure all technologies are mentioned."""
                },
                {
                    "role": "user",
                    "content": f"Generate comprehensive RMarkdown documentation for this repository: {repo_url}"
                }
            ]

        )

        doc_output = completion.choices[0].message.content

        return render_template("index.html", result=doc_output)

    return render_template("index.html")
    

@app.route("/api/generate", methods=["POST"])
def api_generate():
    data = request.get_json()
    repo_url = data.get("repo_url")
    repo_dir = clone_repo(repo_url)
    docs = analyze_repo(repo_dir)
    rmd_content = generate_rmarkdown(docs)

    completion = client.chat.completions.create(
        model="deepseek/deepseek-chat",
        messages=[{"role": "user", "content": f"Format this RMarkdown professionally:\n{rmd_content}"}]
    )

    doc_output = completion.choices[0].message.content
    return jsonify({"documentation": doc_output})


if __name__ == "__main__":
    app.run(debug=True)
