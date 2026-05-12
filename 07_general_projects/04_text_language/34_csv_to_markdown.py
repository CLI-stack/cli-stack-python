"""
Project: CSV to Markdown Table Converter
What it does: Converts a CSV file into a nicely formatted Markdown table.
Markdown tables are used in GitHub README files, documentation, and wikis.

CSV format:
  name,age,city
  Alice,30,New York

Markdown table output:
  | name  | age | city     |
  |-------|-----|----------|
  | Alice | 30  | New York |

Run: python 34_csv_to_markdown.py
Run: python 34_csv_to_markdown.py --file data.csv --align center
"""

import csv
import os
import argparse
import io   # for using StringIO to create in-memory file-like objects


SAMPLE_CSV = """name,age,city,salary,department
Alice Johnson,30,New York,75000,Engineering
Bob Smith,25,London,60000,Sales
Charlie Brown,35,Tokyo,90000,Engineering
Diana Prince,28,Sydney,70000,Marketing
Eve Wilson,32,Paris,85000,Engineering
"""


def read_csv(filepath=None, text=None):
    """
    Read CSV data from a file or from a string.
    Returns the header row and all data rows as lists.
    """
    if filepath and os.path.exists(filepath):
        with open(filepath, newline="") as f:
            reader = csv.reader(f)
            rows   = list(reader)
    elif text:
        # io.StringIO creates an in-memory file-like object from a string
        # This lets csv.reader work on a string without creating a real file
        f      = io.StringIO(text.strip())
        reader = csv.reader(f)
        rows   = list(reader)
    else:
        return [], []

    if not rows:
        return [], []

    header    = rows[0]   # first row = column headers
    data_rows = rows[1:]  # all remaining rows = data
    return header, data_rows


def column_widths(header, rows):
    """
    Calculate the minimum column width for each column.
    Each column must be wide enough to fit its widest value.
    """
    widths = [len(h) for h in header]  # start with header widths

    for row in rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(str(cell)))  # expand if needed

    return widths


def format_cell(value, width, alignment="left"):
    """
    Pad a cell value to the required column width.
    alignment: "left" (default), "right", or "center"
    """
    value = str(value)
    if alignment == "right":
        return value.rjust(width)      # right-align (numbers look good right-aligned)
    elif alignment == "center":
        return value.center(width)     # center-align
    else:
        return value.ljust(width)      # left-align (default for text)


def to_markdown_table(header, rows, alignment="left", num_align="right"):
    """
    Convert header and rows to a Markdown table string.

    Markdown table syntax:
      | Header1 | Header2 |
      |---------|---------|   ← separator row with dashes
      | data1   | data2   |

    The separator row can include alignment markers:
      :--- = left    ---: = right    :---: = center
    """
    widths  = column_widths(header, rows)
    lines   = []

    # Determine alignment per column
    def detect_align(col_idx):
        """Auto-detect: if all values in column look numeric, right-align."""
        values = [row[col_idx] for row in rows if col_idx < len(row)]
        try:
            all(float(v.replace(",","")) for v in values if v)
            return num_align   # numeric column → right-align
        except ValueError:
            return alignment   # text column → use default

    col_aligns = [detect_align(i) for i in range(len(header))]

    # Header row
    header_cells = [format_cell(h, widths[i], col_aligns[i])
                    for i, h in enumerate(header)]
    lines.append("| " + " | ".join(header_cells) + " |")

    # Separator row (with alignment markers)
    sep_cells = []
    for i, w in enumerate(widths):
        align = col_aligns[i]
        if align == "center":
            sep_cells.append(":" + "-" * (w) + ":")    # :---:
        elif align == "right":
            sep_cells.append("-" * (w+1) + ":")         # ---:
        else:
            sep_cells.append("-" * (w+2))               # ---
    lines.append("|" + "|".join(sep_cells) + "|")

    # Data rows
    for row in rows:
        # Pad row if it has fewer cells than the header
        padded_row = list(row) + [""] * (len(header) - len(row))
        cells      = [format_cell(padded_row[i], widths[i], col_aligns[i])
                      for i in range(len(header))]
        lines.append("| " + " | ".join(cells) + " |")

    return "\n".join(lines)


def to_html_table(header, rows):
    """Also generate an HTML table version."""
    html = "<table>\n  <thead>\n    <tr>\n"
    for h in header:
        html += f"      <th>{h}</th>\n"
    html += "    </tr>\n  </thead>\n  <tbody>\n"
    for row in rows:
        html += "    <tr>\n"
        for cell in row:
            html += f"      <td>{cell}</td>\n"
        html += "    </tr>\n"
    html += "  </tbody>\n</table>"
    return html


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Convert CSV to Markdown table")
parser.add_argument("--file",  help="Input CSV file")
parser.add_argument("--align", choices=["left","right","center"], default="left")
parser.add_argument("--html",  action="store_true", help="Also output HTML version")
args = parser.parse_args()

print("=== CSV to Markdown Table Converter ===\n")

if args.file and os.path.exists(args.file):
    header, rows = read_csv(filepath=args.file)
    print(f"Input file: {args.file}")
else:
    print("Using built-in sample CSV data.\n")
    header, rows = read_csv(text=SAMPLE_CSV)

if not header:
    print("No data to convert.")
else:
    print(f"Rows: {len(rows)}  Columns: {len(header)}\n")

    md_table = to_markdown_table(header, rows, alignment=args.align)

    print("  Markdown Table:")
    print("  " + "─" * 60)
    for line in md_table.split("\n"):
        print("  " + line)

    if args.html:
        print(f"\n  HTML Table:")
        print("  " + "─" * 60)
        print(to_html_table(header, rows))
