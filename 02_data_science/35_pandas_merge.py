"""
Script: Pandas Merge (Join Tables)
What it does: Combines two DataFrames based on a common column.
Similar to SQL JOIN — very common when data comes from different sources.

Install: pip install pandas
"""

try:
    import pandas as pd

    # --- Two separate tables ---
    # Orders table
    orders = pd.DataFrame({
        "order_id":   [101, 102, 103, 104, 105],
        "customer_id":[1,   2,   1,   3,   2  ],
        "product":    ["Laptop", "Phone", "Mouse", "Tablet", "Keyboard"],
        "amount":     [1200, 800, 40, 500, 80]
    })

    # Customers table
    customers = pd.DataFrame({
        "customer_id": [1,       2,        3      ],
        "name":        ["Alice", "Bob",    "Charlie"],
        "city":        ["NYC",   "London", "Tokyo" ]
    })

    print("=== Orders Table ===")
    print(orders)
    print("\n=== Customers Table ===")
    print(customers)

    # --- Inner Join: only matching records ---
    # Like: "show me only orders that have a matching customer"
    inner = pd.merge(orders, customers, on="customer_id", how="inner")
    print("\n=== Inner Join (matching only) ===")
    print(inner)

    # --- Left Join: all orders + customer info where available ---
    left = pd.merge(orders, customers, on="customer_id", how="left")
    print("\n=== Left Join (all orders) ===")
    print(left)

    # --- Total spending per customer ---
    spending = inner.groupby("name")["amount"].sum().reset_index()
    spending.columns = ["Customer", "Total Spent"]
    spending = spending.sort_values("Total Spent", ascending=False)
    print("\n=== Total Spending per Customer ===")
    print(spending)

    # --- Merge on different column names ---
    products = pd.DataFrame({
        "prod_name": ["Laptop", "Phone", "Mouse", "Tablet"],
        "category":  ["Computers", "Phones", "Accessories", "Computers"]
    })

    enriched = pd.merge(orders, products, left_on="product", right_on="prod_name", how="left")
    print("\n=== Orders with Category ===")
    print(enriched[["order_id", "product", "category", "amount"]])

except ImportError:
    print("Install: pip install pandas")
