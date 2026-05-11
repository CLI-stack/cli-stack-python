"""
Script: Numerical Integration
What it does: Calculates the area under a curve (definite integral)
using numerical methods. Integration is fundamental in physics, engineering, and ML.

Install: pip install numpy scipy matplotlib
"""

try:
    import numpy as np
    from scipy import integrate
    import matplotlib.pyplot as plt

    # --- Define a function to integrate ---
    def f(x):
        return x**2 + 2*x + 1  # f(x) = x² + 2x + 1

    # --- Method 1: Simple Riemann Sum (rectangle approximation) ---
    def riemann_sum(func, a, b, n=1000):
        """Approximate integral using n rectangles."""
        dx = (b - a) / n                        # width of each rectangle
        x_values = np.linspace(a, b - dx, n)   # left edges of rectangles
        areas = func(x_values) * dx             # height × width for each
        return np.sum(areas)

    a, b = 0, 3  # integration bounds

    print(f"=== Integrating f(x) = x² + 2x + 1 from {a} to {b} ===\n")

    # Exact answer (from calculus): [x³/3 + x² + x] from 0 to 3 = 9 + 9 + 3 = 21
    exact = 21
    print(f"Exact answer: {exact}")

    # Riemann sums with different n
    for n in [10, 100, 1000, 10000]:
        approx = riemann_sum(f, a, b, n)
        error = abs(approx - exact)
        print(f"Riemann sum (n={n:>5}): {approx:.6f}  error: {error:.8f}")

    # --- Method 2: SciPy's adaptive integration (much more accurate) ---
    print("\n=== SciPy Integration ===")
    result, error_estimate = integrate.quad(f, a, b)
    print(f"scipy.integrate.quad: {result:.10f}")
    print(f"Error estimate:       {error_estimate:.2e}")

    # --- Integrate other functions ---
    print("\n=== More Integration Examples ===")

    # ∫ sin(x) dx from 0 to π = 2
    sin_result, _ = integrate.quad(np.sin, 0, np.pi)
    print(f"∫ sin(x) dx [0,π] = {sin_result:.6f} (exact: 2.0)")

    # ∫ e^(-x²) dx from -∞ to ∞ = √π
    gauss_result, _ = integrate.quad(lambda x: np.exp(-x**2), -np.inf, np.inf)
    print(f"∫ e^(-x²) dx [-∞,∞] = {gauss_result:.6f} (√π = {np.sqrt(np.pi):.6f})")

except ImportError:
    print("Install: pip install numpy scipy matplotlib")

    # Show concept with pure Python
    print("\nRiemann sum with pure Python:")
    def f(x): return x**2 + 2*x + 1
    a, b, n = 0, 3, 1000
    dx = (b - a) / n
    total = sum(f(a + i*dx) * dx for i in range(n))
    print(f"∫ x²+2x+1 dx [0,3] ≈ {total:.4f} (exact: 21)")
