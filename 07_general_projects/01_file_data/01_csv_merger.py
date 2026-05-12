"""
Project: CSV File Merger
What it does: Combines multiple CSV files into one single CSV file.
Very common task when data comes from different sources (monthly reports,
different departments, etc.) and you want one unified dataset.

Run: python 01_csv_merger.py  (uses auto-generated sample files)
Run: python 01_csv_merger.py --folder /path/to/csvs --output merged.csv
"""

import csv       # built-in module for reading/writing CSV files
import os        # for file path operations
import argparse  # for command-line argument parsing
from pathlib import Path  # modern way to work with file paths


def create_sample_csv_files():
    """Create a few sample CSV files so we can demonstrate the merger."""
    samples = {
        "sales_jan.csv": [
            ["name", "product", "amount", "month"],
            ["Alice", "Laptop",  1200, "January"],
            ["Bob",   "Phone",    800, "January"],
        ],
        "sales_feb.csv": [
            ["name", "product", "amount", "month"],
            ["Charlie", "Tablet",  500, "February"],
            ["Diana",   "Monitor", 350, "February"],
        ],
        "sales_mar.csv": [
            ["name", "product", "amount", "month"],
            ["Eve",   "Keyboard", 80,  "March"],
            ["Frank", "Mouse",    40,  "March"],
            ["Grace", "Headset", 120,  "March"],
        ],
    }

    # Write each sample CSV file to disk
    for filename, rows in samples.items():
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)  # writerows() writes all rows at once
        print(f"  Created sample: {filename}")

    return list(samples.keys())


def merge_csv_files(csv_files, output_path):
    """
    Merge a list of CSV files into a single output file.

    Strategy:
      - Read the header from the FIRST file
      - For every subsequent file, skip its header row (to avoid duplicates)
      - Write all data rows into the output file
    """
    header_written = False  # track whether we've written the column headers yet
    total_rows     = 0      # count how many data rows we merge

    # Open the output file for writing
    # newline="" prevents Python from adding extra blank lines on Windows
    with open(output_path, "w", newline="") as out_file:
        writer = csv.writer(out_file)

        for csv_file in csv_files:
            print(f"  Merging: {csv_file}")

            with open(csv_file, "r", newline="") as in_file:
                reader = csv.reader(in_file)  # reader reads one row at a time

                # next() reads the FIRST row — which is always the header
                header = next(reader)

                # Only write the header once (from the first file)
                if not header_written:
                    writer.writerow(header)    # write header to output
                    header_written = True
                    print(f"    Header: {header}")

                # Write all the remaining data rows (skip duplicated headers)
                row_count = 0
                for row in reader:
                    writer.writerow(row)
                    row_count += 1

                total_rows += row_count
                print(f"    Rows: {row_count}")

    print(f"\n  Done! {total_rows} total rows merged into: {output_path}")
    return total_rows


def read_and_display(filepath, max_rows=10):
    """Read and print the merged CSV for verification."""
    print(f"\n  Preview of '{filepath}':")
    print(f"  {'NAME':<12} {'PRODUCT':<12} {'AMOUNT':>8} {'MONTH'}")
    print("  " + "-" * 50)

    with open(filepath, "r") as f:
        reader = csv.DictReader(f)  # DictReader uses the header row as column names
        for i, row in enumerate(reader):
            if i >= max_rows:
                print(f"  ... ({i} more rows)")
                break
            # Access columns by name instead of index (more readable)
            print(f"  {row['name']:<12} {row['product']:<12} "
                  f"${int(row['amount']):>7,} {row['month']}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Merge multiple CSV files into one")
parser.add_argument("--folder", help="Folder containing CSV files (default: current dir)")
parser.add_argument("--output", default="merged_output.csv", help="Output filename")
args = parser.parse_args()

print("=== CSV File Merger ===\n")

if args.folder and os.path.isdir(args.folder):
    # Find all .csv files in the given folder
    # Path.glob() searches for files matching a pattern
    csv_files = sorted(Path(args.folder).glob("*.csv"))
    csv_files = [str(f) for f in csv_files]  # convert Path objects to strings
else:
    print("Creating sample CSV files...\n")
    csv_files = create_sample_csv_files()
    print()

if not csv_files:
    print("No CSV files found!")
else:
    print(f"Found {len(csv_files)} CSV files to merge:\n")
    merge_csv_files(csv_files, args.output)
    read_and_display(args.output)

    # Clean up sample files if we created them
    if not args.folder:
        for f in csv_files:
            os.remove(f)
        os.remove(args.output)
        print("\n  (Sample files cleaned up)")
