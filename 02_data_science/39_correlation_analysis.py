"""
Script: Correlation Analysis
What it does: Measures how strongly two variables are related.
Correlation ranges from -1 to +1:
  +1 = perfect positive relationship (as one goes up, so does the other)
   0 = no relationship
  -1 = perfect negative relationship (as one goes up, the other goes down)

Install: pip install pandas numpy matplotlib
"""

try:
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt

    # Dataset: student study hours, sleep hours, and exam scores
    np.random.seed(42)
    n = 50  # number of students

    study_hours = np.random.uniform(1, 10, n)
    # Exam score strongly correlates with study hours (+noise)
    exam_score = study_hours * 7 + np.random.normal(0, 5, n)
    exam_score = np.clip(exam_score, 0, 100)

    sleep_hours = np.random.uniform(4, 10, n)
    # Stress is negatively related to sleep (-correlation)
    stress_level = -sleep_hours * 0.8 + np.random.normal(10, 1, n)

    # Build DataFrame
    df = pd.DataFrame({
        "study_hours": study_hours,
        "exam_score":  exam_score,
        "sleep_hours": sleep_hours,
        "stress_level": stress_level
    })

    print("=== Sample Data ===")
    print(df.head())

    # --- Compute correlation matrix ---
    print("\n=== Correlation Matrix ===")
    corr_matrix = df.corr()
    print(corr_matrix.round(3))

    # --- Interpret specific correlations ---
    print("\n=== Key Correlations ===")
    r = corr_matrix.loc["study_hours", "exam_score"]
    print(f"Study Hours ↔ Exam Score: {r:.3f} (strong positive)")

    r2 = corr_matrix.loc["sleep_hours", "stress_level"]
    print(f"Sleep Hours ↔ Stress:     {r2:.3f} (negative: more sleep = less stress)")

    # --- Visualize correlation as heatmap ---
    plt.figure(figsize=(6, 5))
    plt.imshow(corr_matrix, cmap="coolwarm", vmin=-1, vmax=1)
    plt.colorbar(label="Correlation")
    plt.xticks(range(len(corr_matrix)), corr_matrix.columns, rotation=45)
    plt.yticks(range(len(corr_matrix)), corr_matrix.columns)
    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.savefig("correlation_heatmap.png")
    plt.close()
    print("\nHeatmap saved: correlation_heatmap.png")

    import os
    os.remove("correlation_heatmap.png")

except ImportError:
    print("Install: pip install pandas numpy matplotlib")
