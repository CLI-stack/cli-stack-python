"""
Script: Scatter Plot and Histogram
What it does: Creates scatter plots (show relationships) and histograms (show distribution).
These are two of the most useful chart types for exploring data.

Install: pip install matplotlib numpy
"""

try:
    import matplotlib.pyplot as plt
    import numpy as np

    # --- 1. Scatter Plot: Height vs Weight ---
    # Generate some realistic-looking data
    np.random.seed(42)  # seed makes random numbers reproducible
    height = np.random.normal(170, 10, 50)   # 50 values, mean=170, std=10
    weight = height * 0.4 + np.random.normal(0, 5, 50)  # weight correlates with height

    plt.figure(figsize=(8, 5))
    plt.scatter(height, weight, color="steelblue", alpha=0.6, s=60)
    # alpha = transparency (0=invisible, 1=solid), s = dot size
    plt.title("Height vs Weight")
    plt.xlabel("Height (cm)")
    plt.ylabel("Weight (kg)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("scatter_plot.png")
    plt.close()
    print("Saved: scatter_plot.png")

    # --- 2. Histogram: Exam Score Distribution ---
    scores = np.random.normal(75, 12, 200)   # 200 scores, mean=75, std=12
    scores = np.clip(scores, 0, 100)         # clip to 0-100 range

    plt.figure(figsize=(8, 5))
    plt.hist(scores, bins=20, color="coral", edgecolor="white")
    # bins = number of bars, edgecolor = bar border color
    plt.title("Exam Score Distribution")
    plt.xlabel("Score")
    plt.ylabel("Number of Students")
    plt.axvline(scores.mean(), color="red", linestyle="--", label=f"Mean: {scores.mean():.1f}")
    plt.legend()
    plt.tight_layout()
    plt.savefig("histogram.png")
    plt.close()
    print("Saved: histogram.png")

    print("\nOpen the PNG files to see the charts.")

    import os
    for f in ["scatter_plot.png", "histogram.png"]:
        if os.path.exists(f):
            os.remove(f)

except ImportError:
    print("Install: pip install matplotlib numpy")
