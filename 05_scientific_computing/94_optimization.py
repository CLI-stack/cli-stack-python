"""
Script: Optimization
What it does: Finds the minimum or maximum of a function.
Optimization is everywhere: minimizing cost, maximizing profit,
training machine learning models.

Install: pip install scipy numpy matplotlib
"""

try:
    import numpy as np
    from scipy.optimize import minimize, minimize_scalar
    import matplotlib.pyplot as plt

    # --- Single variable optimization ---
    print("=== Minimize a Single Variable Function ===")
    print("Find minimum of: f(x) = x² - 4x + 4 = (x-2)²\n")

    def f(x):
        return x**2 - 4*x + 4  # minimum at x=2 (answer: 0)

    result = minimize_scalar(f, method="brent")
    print(f"Minimum at:    x = {result.x:.6f} (expected: 2.0)")
    print(f"Minimum value: f(x) = {result.fun:.6f} (expected: 0.0)")
    print(f"Converged: {result.success}")

    # --- More complex function ---
    print("\n=== Minimize: f(x) = x⁴ - 3x³ + 2 ===")

    def g(x):
        return x**4 - 3*x**3 + 2

    # Try different starting points (this function has multiple minima)
    for x0 in [-2, 0, 2, 4]:
        result = minimize(g, x0=x0, method="BFGS")
        print(f"  Start x={x0:>3}: minimum at x={result.x[0]:.4f}, f(x)={result.fun:.4f}")

    # --- Multi-variable optimization ---
    print("\n=== Multi-Variable: Minimize f(x,y) = (x-1)² + (y-2)² ===")
    print("Minimum should be at x=1, y=2\n")

    def f_multivar(params):
        x, y = params
        return (x - 1)**2 + (y - 2)**2  # minimum at (1, 2)

    result = minimize(
        f_multivar,
        x0=[0, 0],    # starting guess
        method="Nelder-Mead"
    )
    x_opt, y_opt = result.x
    print(f"Optimal x: {x_opt:.6f} (expected: 1.0)")
    print(f"Optimal y: {y_opt:.6f} (expected: 2.0)")
    print(f"Min value: {result.fun:.6f} (expected: 0.0)")

    # --- Real example: find the best price to maximize revenue ---
    print("\n=== Real Example: Optimal Pricing ===")
    print("Demand = 1000 - 50 × price")
    print("Revenue = price × demand\n")

    def revenue(price_list):
        price = price_list[0]
        demand = 1000 - 50 * price
        if demand < 0:
            return 1e10     # penalty: price too high
        return -price * demand  # negative because we maximize (minimize negative)

    result = minimize(revenue, x0=[10], bounds=[(0, 20)])
    opt_price = result.x[0]
    opt_demand = 1000 - 50 * opt_price
    print(f"Optimal price:  ${opt_price:.2f}")
    print(f"Expected demand: {opt_demand:.0f} units")
    print(f"Max revenue:    ${opt_price * opt_demand:,.0f}")

except ImportError:
    print("Install: pip install scipy numpy")
