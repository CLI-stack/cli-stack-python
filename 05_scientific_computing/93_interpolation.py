"""
Script: Data Interpolation
What it does: Estimates values between known data points.
Like drawing a smooth line through scatter plot points.
Used in signal processing, graphics, and scientific data analysis.

Install: pip install scipy numpy matplotlib
"""

try:
    import numpy as np
    from scipy import interpolate
    import matplotlib.pyplot as plt

    # --- Known data points (sparse) ---
    x_known = np.array([0, 1, 2, 4, 6, 8, 10])
    y_known = np.array([1, 2.5, 2, 3, 4.5, 4, 5])

    # Dense x values for interpolating
    x_dense = np.linspace(0, 10, 200)

    print("=== Known Data Points ===")
    for x, y in zip(x_known, y_known):
        print(f"  ({x:.1f}, {y:.1f})")

    # --- Method 1: Linear Interpolation ---
    linear_interp = interpolate.interp1d(x_known, y_known, kind="linear")
    y_linear = linear_interp(x_dense)
    print("\nLinear interpolation: connects points with straight lines")

    # --- Method 2: Cubic Spline (smoother) ---
    cubic_interp = interpolate.interp1d(x_known, y_known, kind="cubic")
    y_cubic = cubic_interp(x_dense)
    print("Cubic spline: smooth curve through the points")

    # --- Method 3: Nearest Neighbor ---
    nearest_interp = interpolate.interp1d(x_known, y_known, kind="nearest")
    y_nearest = nearest_interp(x_dense)
    print("Nearest neighbor: steps, snaps to closest known value")

    # --- Estimate specific values ---
    print("\n=== Interpolated Values ===")
    test_points = [1.5, 3.0, 5.0, 7.0, 9.5]
    print(f"{'x':<8} {'Linear':>10} {'Cubic':>10}")
    for x in test_points:
        lin_val = float(linear_interp(x))
        cub_val = float(cubic_interp(x))
        print(f"x={x:<6} {lin_val:>10.3f} {cub_val:>10.3f}")

    # --- Visualize ---
    plt.figure(figsize=(10, 5))
    plt.scatter(x_known, y_known, s=100, zorder=5, label="Known points", color="black")
    plt.plot(x_dense, y_linear, "--", label="Linear", linewidth=1.5)
    plt.plot(x_dense, y_cubic, "-", label="Cubic spline", linewidth=2)
    plt.plot(x_dense, y_nearest, ":", label="Nearest neighbor", linewidth=1.5)
    plt.legend()
    plt.title("Interpolation Methods Comparison")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("interpolation.png")
    plt.close()
    print("\nVisualization saved: interpolation.png")

    import os
    os.remove("interpolation.png")

except ImportError:
    print("Install: pip install scipy numpy matplotlib")
