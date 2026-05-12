"""
Project: Project Scaffolder / Template Generator
What it does: Generates a complete new Python project structure with
all standard files: README, setup.py, tests folder, .gitignore, etc.
Saves time when starting a new project — just run and start coding.

Run: python 46_project_scaffolder.py my_new_project
Run: python 46_project_scaffolder.py my_api --template flask
Run: python 46_project_scaffolder.py my_data --template data
"""

import os
import argparse
from datetime import datetime

# File templates for each project type
TEMPLATES = {
    "basic": {
        "description": "Basic Python package with tests",
        "files": {
            "README.md":       lambda n: f"# {n}\n\nProject description here.\n\n## Installation\n\n```bash\npip install -e .\n```\n\n## Usage\n\n```python\nfrom {n.lower().replace('-','_')} import main\n```\n",
            "setup.py":        lambda n: f'from setuptools import setup, find_packages\n\nsetup(\n    name="{n}",\n    version="0.1.0",\n    packages=find_packages(),\n    python_requires=">=3.8",\n)\n',
            ".gitignore":      lambda n: "# Python\n__pycache__/\n*.py[cod]\n*.egg-info/\ndist/\nbuild/\n.env\n.venv/\nvenv/\n*.pyc\n\n# IDEs\n.vscode/\n.idea/\n*.swp\n",
            "requirements.txt":lambda n: "# Add your dependencies here\n# example: requests>=2.28.0\n",
            f"{{name}}/__init__.py":  lambda n: f'"""\\n{n} package\\n"""\n\n__version__ = "0.1.0"\n',
            f"{{name}}/main.py":      lambda n: f'"""Main module for {n}."""\n\n\ndef main():\n    """Entry point."""\n    print("Hello from {n}!")\n\n\nif __name__ == "__main__":\n    main()\n',
            "tests/__init__.py":     lambda n: "",
            "tests/test_main.py":    lambda n: f'"""Tests for {n}."""\nimport pytest\nfrom {n.lower().replace("-","_")}.main import main\n\n\ndef test_main(capsys):\n    """Test that main() runs without error."""\n    main()\n    captured = capsys.readouterr()\n    assert "Hello" in captured.out\n',
        }
    },
    "flask": {
        "description": "Flask web application",
        "files": {
            "README.md":        lambda n: f"# {n}\n\nFlask web application.\n\n## Run\n\n```bash\npip install -r requirements.txt\npython app.py\n```\n",
            "app.py":           lambda n: f'"""Flask application for {n}."""\nfrom flask import Flask, jsonify\n\napp = Flask(__name__)\n\n\n@app.route("/")\ndef home():\n    return jsonify({{"message": "Welcome to {n}!", "status": "running"}})\n\n\n@app.route("/health")\ndef health():\n    return jsonify({{"status": "healthy"}})\n\n\nif __name__ == "__main__":\n    app.run(debug=True)\n',
            "requirements.txt": lambda n: "flask>=2.0.0\npython-dotenv>=0.19.0\n",
            ".env":             lambda n: "# Environment variables\nFLASK_ENV=development\nDEBUG=True\n# SECRET_KEY=your-secret-key-here\n",
            ".gitignore":       lambda n: "*.pyc\n__pycache__/\n.env\n.venv/\nvenv/\n",
            "static/.gitkeep":  lambda n: "",
            "templates/.gitkeep": lambda n: "",
        }
    },
    "data": {
        "description": "Data science project with Jupyter notebooks",
        "files": {
            "README.md":        lambda n: f"# {n}\n\nData science project.\n\n## Setup\n\n```bash\npip install -r requirements.txt\njupyter notebook\n```\n",
            "requirements.txt": lambda n: "numpy>=1.21\npandas>=1.3\nmatplotlib>=3.4\nscikit-learn>=1.0\njupyter>=1.0\n",
            "notebooks/.gitkeep": lambda n: "",
            "data/raw/.gitkeep":  lambda n: "",
            "data/processed/.gitkeep": lambda n: "",
            "src/__init__.py":    lambda n: "",
            "src/data_loader.py": lambda n: f'"""Data loading utilities for {n}."""\nimport pandas as pd\n\n\ndef load_csv(filepath):\n    """Load a CSV file into a DataFrame."""\n    return pd.read_csv(filepath)\n',
            "src/analysis.py":    lambda n: '"""Analysis functions."""\nimport pandas as pd\nimport matplotlib.pyplot as plt\n\n\ndef summary_stats(df):\n    """Get summary statistics for a DataFrame."""\n    return df.describe()\n',
            ".gitignore":         lambda n: "*.pyc\n__pycache__/\n.ipynb_checkpoints/\ndata/raw/*\ndata/processed/*\n!data/raw/.gitkeep\n!data/processed/.gitkeep\n",
        }
    }
}


def create_project(project_name, template_name="basic", output_dir="."):
    """
    Create a new project directory structure from a template.
    All files are created with appropriate starter content.
    """
    template = TEMPLATES.get(template_name)
    if not template:
        print(f"Unknown template: {template_name}")
        print(f"Available templates: {', '.join(TEMPLATES.keys())}")
        return

    # Sanitize project name: lowercase, replace spaces and hyphens
    safe_name  = project_name.lower().replace(" ", "_").replace("-", "_")
    project_dir= os.path.join(output_dir, project_name)

    if os.path.exists(project_dir):
        print(f"Directory already exists: {project_dir}")
        return

    print(f"Creating project: {project_name} ({template['description']})\n")

    # Create the root project directory
    os.makedirs(project_dir)

    # Create each file defined in the template
    for file_path_template, content_func in template["files"].items():
        # Replace {name} placeholder with actual module name
        file_path = file_path_template.replace("{name}", safe_name)
        full_path = os.path.join(project_dir, file_path)

        # Create parent directories for nested files
        parent_dir = os.path.dirname(full_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        # Generate content using the template function
        content = content_func(safe_name)

        # Write the file
        with open(full_path, "w") as f:
            f.write(content)

        print(f"  Created: {file_path}")

    # Summary
    print(f"\n  Project created: {project_dir}/")
    print(f"\n  Next steps:")
    if template_name == "basic":
        print(f"    cd {project_name}")
        print(f"    python -m venv venv")
        print(f"    source venv/bin/activate  # or .\\\\venv\\\\Scripts\\\\activate on Windows")
        print(f"    pip install -e .")
        print(f"    pytest tests/")
    elif template_name == "flask":
        print(f"    cd {project_name}")
        print(f"    pip install -r requirements.txt")
        print(f"    python app.py")
    elif template_name == "data":
        print(f"    cd {project_name}")
        print(f"    pip install -r requirements.txt")
        print(f"    jupyter notebook notebooks/")

    return project_dir


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Generate a new Python project structure")
parser.add_argument("name",     nargs="?", default="my_project", help="Project name")
parser.add_argument("--template", default="basic",
                    choices=list(TEMPLATES.keys()),
                    help="Project template (default: basic)")
parser.add_argument("--output",   default=".", help="Parent directory (default: current)")
parser.add_argument("--list",     action="store_true", help="List available templates")
args = parser.parse_args()

print("=== Project Scaffolder ===\n")

if args.list:
    print("Available templates:\n")
    for name, tmpl in TEMPLATES.items():
        print(f"  {name:<10} — {tmpl['description']}")
        print(f"             Files: {', '.join(list(tmpl['files'].keys())[:4])}...")
else:
    project_dir = create_project(args.name, args.template, args.output)
    if project_dir:
        import shutil
        shutil.rmtree(project_dir)
        print(f"\n(Demo project cleaned up)")
