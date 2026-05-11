"""
Script: Pandas Basics
What it does: Introduces pandas DataFrames — the main tool for data analysis.
A DataFrame is like a spreadsheet table inside Python.

Install: pip install pandas
"""

try:
    import pandas as pd  # pd is the standard alias for pandas

    # --- Create a DataFrame from a dictionary ---
    data = {
        "name":    ["Alice", "Bob", "Charlie", "Diana", "Eve"],
        "age":     [25, 30, 35, 28, 22],
        "city":    ["NYC", "London", "Tokyo", "Sydney", "Paris"],
        "salary":  [70000, 85000, 90000, 75000, 60000],
        "active":  [True, True, False, True, True]
    }

    df = pd.DataFrame(data)  # create the DataFrame

    # --- Viewing data ---
    print("=== Full DataFrame ===")
    print(df)

    print("\n=== First 3 rows (head) ===")
    print(df.head(3))  # top N rows

    print("\n=== Last 2 rows (tail) ===")
    print(df.tail(2))  # bottom N rows

    # --- Basic info ---
    print("\n=== DataFrame Info ===")
    print(f"Shape: {df.shape}")          # (rows, columns)
    print(f"Columns: {list(df.columns)}")
    print(f"Data types:\n{df.dtypes}")

    # --- Accessing columns ---
    print("\n=== Names column ===")
    print(df["name"])                   # access one column

    print("\n=== Name and Salary ===")
    print(df[["name", "salary"]])       # access multiple columns

    # --- Basic statistics ---
    print("\n=== Salary Statistics ===")
    print(df["salary"].describe())      # count, mean, std, min, max, etc.

    # --- Access a specific cell ---
    print(f"\nAlice's salary: {df.loc[0, 'salary']}")   # row 0, column 'salary'

    # --- Create a DataFrame from CSV (commented out — needs a file) ---
    # df_from_csv = pd.read_csv("data.csv")

except ImportError:
    print("Pandas not installed. Run: pip install pandas")
