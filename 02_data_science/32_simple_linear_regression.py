"""
Script: Simple Linear Regression
What it does: Finds the line of best fit through data points.
Used to predict a continuous value (like price, temperature) based on one input.
Example: predict house price based on size.

Install: pip install scikit-learn numpy matplotlib
"""

try:
    import numpy as np
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_squared_error, r2_score
    import matplotlib.pyplot as plt

    # --- Sample data: house size (sqft) vs price ($) ---
    house_size = np.array([800, 1000, 1200, 1500, 1800, 2000, 2200, 2500]).reshape(-1, 1)
    # reshape(-1, 1) converts 1D array to column vector (required by sklearn)
    price = np.array([150000, 200000, 230000, 280000, 330000, 380000, 410000, 470000])

    # --- Create and train the model ---
    model = LinearRegression()
    model.fit(house_size, price)  # fit = train the model on data

    # --- Model parameters ---
    print("=== Model Parameters ===")
    print(f"Slope (coefficient): ${model.coef_[0]:.2f} per sqft")
    # slope = how much price increases per sqft
    print(f"Intercept: ${model.intercept_:.2f}")
    # intercept = base price when size = 0

    # --- Predictions ---
    predictions = model.predict(house_size)

    print("\n=== Actual vs Predicted ===")
    for size, actual, predicted in zip(house_size.flatten(), price, predictions):
        print(f"  Size: {size} sqft | Actual: ${actual:,} | Predicted: ${predicted:,.0f}")

    # --- Model accuracy metrics ---
    r2 = r2_score(price, predictions)
    # R² = how well the model fits (0 to 1, closer to 1 = better)
    print(f"\nR² Score: {r2:.4f} (higher = better fit)")
    print(f"RMSE: ${mean_squared_error(price, predictions)**0.5:,.0f}")

    # --- Predict a new value ---
    new_size = np.array([[1600]])
    predicted_price = model.predict(new_size)[0]
    print(f"\nPredicted price for 1600 sqft: ${predicted_price:,.0f}")

    # --- Create and save a chart ---
    plt.figure(figsize=(8, 5))
    plt.scatter(house_size, price, color="blue", label="Actual prices")
    plt.plot(house_size, predictions, color="red", linewidth=2, label="Regression line")
    plt.title("House Size vs Price")
    plt.xlabel("Size (sqft)")
    plt.ylabel("Price ($)")
    plt.legend()
    plt.tight_layout()
    plt.savefig("linear_regression.png")
    plt.close()
    print("Chart saved: linear_regression.png")

    import os
    os.remove("linear_regression.png")

except ImportError:
    print("Install: pip install scikit-learn numpy matplotlib")
