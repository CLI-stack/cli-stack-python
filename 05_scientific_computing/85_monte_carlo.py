"""
Script: Monte Carlo Simulation
What it does: Uses random sampling to estimate results of complex problems.
Classic example: estimate the value of π by randomly throwing darts
at a square that contains a circle.

Install: pip install numpy matplotlib
"""

try:
    import numpy as np
    import matplotlib.pyplot as plt

    def estimate_pi(n_samples):
        """
        Estimate π using the Monte Carlo method.
        Imagine a 1x1 square with a quarter circle inside.
        Points inside the circle satisfy: x² + y² <= 1
        Ratio of circle area to square area = π/4
        So: π ≈ 4 × (points inside circle) / (total points)
        """
        # Generate random (x, y) points between 0 and 1
        x = np.random.uniform(0, 1, n_samples)
        y = np.random.uniform(0, 1, n_samples)

        # Check which points fall inside the quarter circle
        distances = x**2 + y**2
        inside = distances <= 1  # True if inside circle

        # Estimate π
        pi_estimate = 4 * np.sum(inside) / n_samples
        return pi_estimate, x, y, inside

    # --- Run simulations with increasing sample sizes ---
    print("=== Monte Carlo π Estimation ===\n")
    print(f"True π = {np.pi:.8f}\n")

    sample_sizes = [100, 1000, 10000, 100000, 1000000]
    for n in sample_sizes:
        pi_est, _, _, _ = estimate_pi(n)
        error = abs(pi_est - np.pi)
        print(f"N={n:>8,}: π ≈ {pi_est:.6f}  (error: {error:.6f})")

    # --- Visualize with smaller sample ---
    n_vis = 5000
    pi_est, x, y, inside = estimate_pi(n_vis)

    plt.figure(figsize=(7, 7))
    plt.scatter(x[inside], y[inside], s=1, c="blue", alpha=0.5, label="Inside circle")
    plt.scatter(x[~inside], y[~inside], s=1, c="red", alpha=0.5, label="Outside circle")

    # Draw the quarter circle
    theta = np.linspace(0, np.pi/2, 100)
    plt.plot(np.cos(theta), np.sin(theta), "k-", linewidth=2)

    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.title(f"Monte Carlo π Estimation\nN={n_vis:,}, π ≈ {pi_est:.4f}")
    plt.legend(loc="lower left")
    plt.gca().set_aspect("equal")
    plt.tight_layout()
    plt.savefig("monte_carlo_pi.png")
    plt.close()
    print(f"\nVisualization saved: monte_carlo_pi.png")

    import os
    os.remove("monte_carlo_pi.png")

except ImportError:
    print("Install: pip install numpy matplotlib")
