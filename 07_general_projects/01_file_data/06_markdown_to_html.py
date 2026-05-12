"""
Project: Markdown to HTML Converter
What it does: Converts a Markdown text file into an HTML webpage.
Markdown is a simple formatting language used in README files, documentation,
and blog posts. This script converts Markdown syntax to HTML tags.

Markdown → HTML examples:
  # Heading     →  <h1>Heading</h1>
  **bold**      →  <strong>bold</strong>
  `code`        →  <code>code</code>
  - list item   →  <li>list item</li>
  [link](url)   →  <a href="url">link</a>

Run: python 06_markdown_to_html.py
Run: python 06_markdown_to_html.py --input README.md --output index.html
"""

import re        # regular expressions for pattern matching
import os
import argparse


SAMPLE_MARKDOWN = """# Python Learning Guide

## Getting Started

Welcome to **Python** programming! Python is a *versatile* and beginner-friendly language.

## Key Features

- Easy to read and write
- Large standard library
- Great for data science, web, and automation
- Cross-platform (Windows, Mac, Linux)

## Code Example

```python
# Hello World in Python
print("Hello, World!")
name = input("What is your name? ")
print(f"Hello, {name}!")
```

## Useful Resources

Visit the [Python official website](https://www.python.org) for documentation.
Check out [Real Python](https://realpython.com) for tutorials.

## Next Steps

1. Install Python from python.org
2. Learn basic syntax
3. Build a small project
4. Join the community

> The best way to learn programming is by writing code every day.

---

*Happy coding!*
"""


def convert_markdown_to_html(markdown_text):
    """
    Convert markdown text to HTML.
    Each conversion step handles a specific markdown syntax element.
    """
    lines    = markdown_text.split("\n")
    html_lines = []
    in_code_block = False   # track whether we're inside a ``` code block
    in_list       = False   # track whether we're inside a bullet list
    in_ol         = False   # track whether we're inside a numbered list

    for line in lines:

        # ── Code blocks (``` fences) ──────────────────────────────────────
        if line.strip().startswith("```"):
            if not in_code_block:
                # Opening fence — start the code block
                lang = line.strip()[3:]  # get language hint (e.g. "python")
                html_lines.append(f'<pre><code class="language-{lang}">')
                in_code_block = True
            else:
                # Closing fence — end the code block
                html_lines.append("</code></pre>")
                in_code_block = False
            continue  # skip to next line

        if in_code_block:
            # Inside a code block — output as-is (preserve formatting)
            # html.escape would prevent < > from being interpreted as HTML tags
            safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            html_lines.append(safe)
            continue

        # ── Headings (# ## ###) ───────────────────────────────────────────
        heading_match = re.match(r"^(#{1,6})\s+(.*)", line)
        if heading_match:
            level   = len(heading_match.group(1))  # count the # symbols
            content = heading_match.group(2)
            html_lines.append(f"<h{level}>{content}</h{level}>")
            continue

        # ── Horizontal rule (---) ─────────────────────────────────────────
        if re.match(r"^-{3,}$", line.strip()):
            html_lines.append("<hr>")
            continue

        # ── Blockquote (> text) ───────────────────────────────────────────
        if line.startswith(">"):
            content = line[1:].strip()  # remove the leading ">"
            html_lines.append(f"<blockquote>{content}</blockquote>")
            continue

        # ── Unordered list items (- item) ─────────────────────────────────
        if re.match(r"^[-*+]\s+", line):
            content = re.sub(r"^[-*+]\s+", "", line)  # remove the "- " prefix
            if not in_list:
                html_lines.append("<ul>")     # open the list
                in_list = True
            html_lines.append(f"  <li>{content}</li>")
            continue
        elif in_list:
            html_lines.append("</ul>")        # close the list when no more items
            in_list = False

        # ── Ordered list items (1. item) ──────────────────────────────────
        if re.match(r"^\d+\.\s+", line):
            content = re.sub(r"^\d+\.\s+", "", line)  # remove "1. " prefix
            if not in_ol:
                html_lines.append("<ol>")
                in_ol = True
            html_lines.append(f"  <li>{content}</li>")
            continue
        elif in_ol:
            html_lines.append("</ol>")
            in_ol = False

        # ── Empty line → paragraph break ──────────────────────────────────
        if not line.strip():
            html_lines.append("")
            continue

        # ── Inline formatting ──────────────────────────────────────────────
        # Apply these in order: code > bold > italic > links
        processed = line

        # Inline code: `code` → <code>code</code>
        processed = re.sub(r"`([^`]+)`", r"<code>\1</code>", processed)

        # Bold: **text** → <strong>text</strong>
        processed = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", processed)

        # Italic: *text* → <em>text</em>
        processed = re.sub(r"\*(.+?)\*", r"<em>\1</em>", processed)

        # Links: [text](url) → <a href="url">text</a>
        processed = re.sub(r"\[([^\]]+)\]\(([^\)]+)\)", r'<a href="\2">\1</a>', processed)

        html_lines.append(f"<p>{processed}</p>" if processed.strip() else processed)

    # Close any open lists
    if in_list:
        html_lines.append("</ul>")
    if in_ol:
        html_lines.append("</ol>")

    return "\n".join(html_lines)


def wrap_in_html_page(body_content, title="Document"):
    """Wrap the converted HTML body in a full HTML page structure."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    body {{ font-family: -apple-system, Arial, sans-serif; max-width: 800px;
            margin: 40px auto; padding: 0 20px; line-height: 1.6; color: #333; }}
    h1, h2, h3 {{ border-bottom: 1px solid #eee; padding-bottom: 8px; }}
    code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: monospace; }}
    pre  {{ background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
    blockquote {{ border-left: 4px solid #ccc; margin: 0; padding-left: 15px; color: #666; }}
    hr   {{ border: none; border-top: 1px solid #eee; }}
    a    {{ color: #0066cc; }}
  </style>
</head>
<body>
{body_content}
</body>
</html>"""


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Convert Markdown to HTML")
parser.add_argument("--input",  help="Input .md file (default: uses sample)")
parser.add_argument("--output", default="output.html", help="Output .html file")
args = parser.parse_args()

print("=== Markdown to HTML Converter ===\n")

if args.input and os.path.exists(args.input):
    with open(args.input, "r") as f:
        md_text = f.read()
    title = os.path.splitext(os.path.basename(args.input))[0]
else:
    print("No input file given — using built-in sample markdown.\n")
    md_text = SAMPLE_MARKDOWN
    title   = "Python Learning Guide"

# Convert markdown to HTML
html_body = convert_markdown_to_html(md_text)
# Wrap in a full HTML page
full_html = wrap_in_html_page(html_body, title=title)

# Write to output file
with open(args.output, "w") as f:
    f.write(full_html)

print(f"Converted {len(md_text)} characters of Markdown → HTML")
print(f"Output saved: {args.output}")
print(f"Open in browser: file://{os.path.abspath(args.output)}")

os.remove(args.output)
print("(Output file cleaned up for demo)")
