def generate_rmarkdown(docs):
    output = "---\ntitle: 'Project Documentation'\noutput: html_document\n---\n\n"
    for item in docs:
        output += f"## {item['type'].capitalize()}: {item['name']}\n\n"
        output += f"```{{r}}\n# {item['docstring']}\n```\n\n"
    return output
