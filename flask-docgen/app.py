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
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert technical documentation writer. "
                        "Your task is to write comprehensive and well-structured documentation in RMarkdown format "
                        "for a GitHub repository. "
                        "Explain the repository’s purpose, its key features, and how the code works logically. "
                        "Highlight the importance of the project, technologies used, and possible applications. "
                        "Organize your response with sections such as 'Overview', 'Architecture', 'Core Components', "
                        "'Usage', and 'Project Significance'. "
                        "Make it eye-catching, professional, and suitable for publication."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Here is the extracted code summary from the repository:\n\n{rmd_content}\n\n"
                        "Now generate a comprehensive RMarkdown documentation file that explains this project."
                    )
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
