"""
Script: Pandas Filter and Sort
What it does: Shows how to filter rows by condition and sort data.
These are the most common operations when exploring a dataset.

Install: pip install pandas
"""

try:
    import pandas as pd

    # Create sample sales data
    data = {
        "product":  ["Laptop", "Phone", "Tablet", "Monitor", "Keyboard", "Mouse"],
        "category": ["Electronics", "Electronics", "Electronics", "Accessories", "Accessories", "Accessories"],
        "price":    [1200, 800, 500, 350, 80, 40],
        "stock":    [50, 200, 75, 30, 150, 300],
        "rating":   [4.5, 4.8, 4.2, 4.0, 4.6, 4.3]
    }

    df = pd.DataFrame(data)
    print("=== All Products ===")
    print(df)

    # --- Filter: products with price over 400 ---
    print("\n=== Products with price > $400 ===")
    expensive = df[df["price"] > 400]  # condition inside []
    print(expensive)

    # --- Filter: multiple conditions ---
    print("\n=== Electronics with rating >= 4.5 ===")
    top_electronics = df[(df["category"] == "Electronics") & (df["rating"] >= 4.5)]
    print(top_electronics)

    # --- Filter using isin() ---
    print("\n=== Specific products ===")
    selected = df[df["product"].isin(["Laptop", "Mouse", "Keyboard"])]
    print(selected)

    # --- Sort by price (ascending) ---
    print("\n=== Sorted by Price (low to high) ===")
    print(df.sort_values("price"))

    # --- Sort by price (descending) ---
    print("\n=== Sorted by Price (high to low) ===")
    print(df.sort_values("price", ascending=False))

    # --- Sort by multiple columns ---
    print("\n=== Sorted by Category then Rating ===")
    print(df.sort_values(["category", "rating"], ascending=[True, False]))

    # --- Reset index after filtering ---
    filtered = df[df["price"] > 400].reset_index(drop=True)
    print("\n=== Filtered with reset index ===")
    print(filtered)

except ImportError:
    print("Pandas not installed. Run: pip install pandas")
