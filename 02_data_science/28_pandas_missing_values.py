"""
Script: Handling Missing Values in Pandas
What it does: Detects and fixes missing data (NaN values) in a DataFrame.
Real-world data always has gaps — this is how you clean it up.

Install: pip install pandas numpy
"""

try:
    import pandas as pd
    import numpy as np  # np.nan represents a missing value

    # Dataset with intentional missing values
    data = {
        "name":   ["Alice", "Bob", None, "Diana", "Eve"],
        "age":    [25, np.nan, 35, 28, np.nan],
        "salary": [70000, 85000, np.nan, 75000, 60000],
        "city":   ["NYC", "London", "Tokyo", None, "Paris"]
    }

    df = pd.DataFrame(data)
    print("=== Original Data (with missing values) ===")
    print(df)

    # --- Detect missing values ---
    print("\n=== Missing Value Map (True = missing) ===")
    print(df.isnull())

    print("\n=== Count of missing values per column ===")
    print(df.isnull().sum())

    print(f"\nTotal missing values: {df.isnull().sum().sum()}")

    # --- Drop rows with any missing value ---
    df_dropped = df.dropna()  # drops any row that has at least one NaN
    print("\n=== After dropping rows with missing values ===")
    print(df_dropped)

    # --- Fill missing numbers with the column mean ---
    df_filled = df.copy()
    df_filled["age"] = df_filled["age"].fillna(df_filled["age"].mean())
    df_filled["salary"] = df_filled["salary"].fillna(df_filled["salary"].median())

    # Fill missing text with a placeholder
    df_filled["name"] = df_filled["name"].fillna("Unknown")
    df_filled["city"] = df_filled["city"].fillna("Not specified")

    print("\n=== After filling missing values ===")
    print(df_filled)

    # --- Fill with forward fill (use previous row's value) ---
    df_ffill = df.fillna(method="ffill")  # forward fill
    print("\n=== Forward fill ===")
    print(df_ffill)

except ImportError:
    print("Install: pip install pandas numpy")
