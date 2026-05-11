"""
Script: Curve Fitting
What it does: Finds the best mathematical function that fits your data.
Used in engineering, physics, and data analysis to model relationships.

Install: pip install scipy numpy matplotlib
"""

try:
    import numpy as np
    from scipy.optimize import curve_fit
    import matplotlib.pyplot as plt

    np.random.seed(42)

    # --- Define a model function ---
    def linear_model(x, a, b):
        """y = ax + b"""
        return a * x + b

    def quadratic_model(x, a, b, c):
        """y = ax² + bx + c"""
        return a * x**2 + b * x + c

    def exponential_model(x, a, b):
        """y = a × e^(bx)"""
        return a * np.exp(b * x)

    # --- Generate sample data with noise ---
    x_data = np.linspace(0, 10, 50)

    # True parameters
    true_a, true_b = 2.5, 1.5
    y_data = linear_model(x_data, true_a, true_b) + np.random.normal(0, 1, 50)

    # --- Fit a linear model ---
    print("=== Linear Curve Fitting ===")
    print(f"True parameters: a={true_a}, b={true_b}")

    params, covariance = curve_fit(linear_model, x_data, y_data)
    a_fit, b_fit = params
    print(f"Fitted:          a={a_fit:.4f}, b={b_fit:.4f}")

    # Standard errors (uncertainty in the parameters)
    std_errors = np.sqrt(np.diag(covariance))
    print(f"Std error in a:  ±{std_errors[0]:.4f}")
    print(f"Std error in b:  ±{std_errors[1]:.4f}")

    # --- Fit a quadratic model to curved data ---
    print("\n=== Quadratic Curve Fitting ===")
    y_quad = quadratic_model(x_data, 0.5, -3, 10) + np.random.normal(0, 0.5, 50)
    params_q, _ = curve_fit(quadratic_model, x_data, y_quad)
    a, b, c = params_q
    print(f"Fitted: y = {a:.3f}x² + {b:.3f}x + {c:.3f}")
    print(f"True:   y = 0.500x² - 3.000x + 10.000")

    # --- Fit an exponential model ---
    print("\n=== Exponential Curve Fitting ===")
    y_exp = exponential_model(x_data, 1.0, 0.3) + np.random.normal(0, 0.5, 50)
    params_e, _ = curve_fit(exponential_model, x_data, y_exp, p0=[1, 0.1])
    # p0 = initial guess for parameters
    print(f"Fitted: y = {params_e[0]:.3f} × e^({params_e[1]:.3f}x)")
    print(f"True:   y = 1.000 × e^(0.300x)")

    print("\nCurve fitting finds the model parameters that best match observed data.")

except ImportError:
    print("Install: pip install scipy numpy matplotlib")
