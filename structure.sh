#!/bin/bash

# Create project root directory
mkdir -p flask-docgen

# Navigate into project
cd flask-docgen || exit

# Create main files
touch app.py config.py requirements.txt

# Create services directory and its files
mkdir -p services
touch services/__init__.py services/repo_analyzer.py services/doc_generator.py

# Create templates directory and index.html
mkdir -p templates
touch templates/index.html

# Create static directory and style.css
mkdir -p static
touch static/style.css

echo "✅ Flask project structure created successfully in flask-docgen/"

