"""
Script: Matplotlib Charts
What it does: Creates basic charts — line, bar, and pie charts.
Charts are essential for visualizing and understanding data.

Install: pip install matplotlib
Note: Charts are saved as PNG files (no display window needed).
"""

try:
    import matplotlib.pyplot as plt  # plt is the standard alias

    # --- 1. Line Chart: Monthly Sales ---
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    sales =  [12000, 15000, 13000, 17000, 20000, 18000]

    plt.figure(figsize=(8, 4))           # set figure size (width, height in inches)
    plt.plot(months, sales, marker="o", color="blue", linewidth=2)
    plt.title("Monthly Sales")           # chart title
    plt.xlabel("Month")                  # x-axis label
    plt.ylabel("Sales ($)")              # y-axis label
    plt.grid(True)                       # show grid lines
    plt.tight_layout()
    plt.savefig("line_chart.png")        # save to file
    plt.close()
    print("Saved: line_chart.png")

    # --- 2. Bar Chart: Product Revenue ---
    products = ["Laptop", "Phone", "Tablet", "Monitor"]
    revenue =  [50000, 30000, 20000, 15000]
    colors = ["steelblue", "coral", "mediumseagreen", "gold"]

    plt.figure(figsize=(8, 4))
    plt.bar(products, revenue, color=colors)
    plt.title("Product Revenue")
    plt.xlabel("Product")
    plt.ylabel("Revenue ($)")
    plt.tight_layout()
    plt.savefig("bar_chart.png")
    plt.close()
    print("Saved: bar_chart.png")

    # --- 3. Pie Chart: Market Share ---
    brands = ["Apple", "Samsung", "Xiaomi", "Others"]
    share =  [30, 25, 20, 25]

    plt.figure(figsize=(6, 6))
    plt.pie(share, labels=brands, autopct="%1.1f%%", startangle=90)
    # autopct shows percentage, startangle rotates starting position
    plt.title("Smartphone Market Share")
    plt.savefig("pie_chart.png")
    plt.close()
    print("Saved: pie_chart.png")

    print("\nAll 3 charts created! Open the PNG files to view them.")

    # Clean up
    import os
    for f in ["line_chart.png", "bar_chart.png", "pie_chart.png"]:
        if os.path.exists(f):
            os.remove(f)

except ImportError:
    print("Install: pip install matplotlib")
