"""
Script: Pandas GroupBy and Aggregation
What it does: Groups data by a category and calculates summary statistics.
Like pivot tables in Excel — summarize data by groups.

Install: pip install pandas
"""

try:
    import pandas as pd

    # Sales data with multiple records per region
    data = {
        "region":     ["North", "South", "North", "East", "South", "East", "North", "West"],
        "salesperson":["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry"],
        "product":    ["Laptop", "Phone", "Tablet", "Laptop", "Laptop", "Phone", "Phone", "Tablet"],
        "sales":      [5000, 3000, 2000, 8000, 6000, 4000, 3500, 2500],
        "units":      [5, 10, 8, 7, 6, 12, 9, 10]
    }

    df = pd.DataFrame(data)
    print("=== Raw Sales Data ===")
    print(df)

    # --- Group by region and sum sales ---
    print("\n=== Total Sales by Region ===")
    by_region = df.groupby("region")["sales"].sum()
    print(by_region)

    # --- Group by region with multiple aggregations ---
    print("\n=== Region Summary (sum, mean, count) ===")
    summary = df.groupby("region")["sales"].agg(["sum", "mean", "count"])
    summary.columns = ["Total Sales", "Avg Sales", "Num Transactions"]
    print(summary)

    # --- Group by multiple columns ---
    print("\n=== Sales by Region and Product ===")
    multi = df.groupby(["region", "product"])["sales"].sum().reset_index()
    print(multi)

    # --- Find the top salesperson per region ---
    print("\n=== Top Salesperson per Region ===")
    top = df.loc[df.groupby("region")["sales"].idxmax()]
    print(top[["region", "salesperson", "sales"]])

    # --- Aggregate multiple columns at once ---
    print("\n=== Region: Total Sales and Total Units ===")
    totals = df.groupby("region")[["sales", "units"]].sum()
    print(totals)

except ImportError:
    print("Pandas not installed. Run: pip install pandas")
