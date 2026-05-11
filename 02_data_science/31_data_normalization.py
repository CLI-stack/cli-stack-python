"""
Script: Data Normalization and Scaling
What it does: Scales numerical data to a standard range.
Normalization is important before applying machine learning algorithms
because features with large values can overpower those with small values.

Install: pip install scikit-learn numpy
"""

try:
    import numpy as np
    from sklearn.preprocessing import MinMaxScaler, StandardScaler

    # Raw data: height (cm), weight (kg), age (years), salary ($)
    # Very different scales!
    data = np.array([
        [175, 70, 25, 50000],
        [160, 55, 35, 80000],
        [180, 85, 28, 65000],
        [165, 60, 45, 90000],
        [170, 75, 30, 55000],
    ])

    print("=== Original Data ===")
    print("(height, weight, age, salary)")
    print(data)

    # --- Min-Max Normalization (scale to 0-1 range) ---
    # Formula: (x - min) / (max - min)
    min_max_scaler = MinMaxScaler()
    normalized = min_max_scaler.fit_transform(data)

    print("\n=== Min-Max Normalized (0 to 1) ===")
    print(normalized.round(3))

    # --- Standard Scaling (mean=0, std=1) ---
    # Formula: (x - mean) / std_deviation
    # This centers data around 0 and scales by spread
    standard_scaler = StandardScaler()
    standardized = standard_scaler.fit_transform(data)

    print("\n=== Standardized (mean=0, std=1) ===")
    print(standardized.round(3))
    print(f"\nMean of standardized: {standardized.mean(axis=0).round(3)}")
    print(f"Std of standardized:  {standardized.std(axis=0).round(3)}")

    # --- Manual Min-Max normalization (to understand it) ---
    col = data[:, 0]  # just the height column
    manual_normalized = (col - col.min()) / (col.max() - col.min())
    print(f"\nManual normalized heights: {manual_normalized.round(3)}")

except ImportError:
    print("Install: pip install scikit-learn numpy")

    # Show the concept without sklearn
    data = [175, 160, 180, 165, 170]
    min_val, max_val = min(data), max(data)
    normalized = [(x - min_val) / (max_val - min_val) for x in data]
    print("Manual normalization:", [round(v, 3) for v in normalized])
