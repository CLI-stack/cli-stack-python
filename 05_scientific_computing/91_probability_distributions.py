"""
Script: Probability Distributions
What it does: Generates and visualizes common statistical distributions.
Distributions describe how likely different values are to occur.

Install: pip install numpy matplotlib scipy
"""

try:
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy import stats

    np.random.seed(42)
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle("Common Probability Distributions", fontsize=14)

    # --- 1. Normal (Gaussian) Distribution ---
    ax = axes[0, 0]
    mean, std = 0, 1
    data = np.random.normal(mean, std, 1000)
    x = np.linspace(-4, 4, 100)
    ax.hist(data, bins=30, density=True, alpha=0.6, color="steelblue", label="Samples")
    ax.plot(x, stats.norm.pdf(x, mean, std), "r-", linewidth=2, label="PDF")
    ax.set_title(f"Normal Distribution (μ={mean}, σ={std})")
    ax.legend()
    print("Normal: Bell-shaped. Most values cluster around the mean.")
    print(f"  Mean: {data.mean():.3f}, Std: {data.std():.3f}")

    # --- 2. Uniform Distribution ---
    ax = axes[0, 1]
    data_unif = np.random.uniform(0, 10, 1000)  # equal probability between 0-10
    ax.hist(data_unif, bins=20, density=True, alpha=0.6, color="coral", label="Samples")
    ax.axhline(y=0.1, color="r", linewidth=2, label="PDF (flat)")
    ax.set_title("Uniform Distribution [0, 10]")
    ax.legend()
    print("\nUniform: All values equally likely.")
    print(f"  Min: {data_unif.min():.2f}, Max: {data_unif.max():.2f}, Mean: {data_unif.mean():.2f}")

    # --- 3. Binomial Distribution ---
    ax = axes[1, 0]
    n_trials, p_success = 20, 0.5  # 20 coin flips, 50% heads probability
    data_binom = np.random.binomial(n_trials, p_success, 1000)
    x = np.arange(0, 21)
    ax.hist(data_binom, bins=range(21), density=True, alpha=0.6, color="mediumseagreen")
    ax.set_title(f"Binomial (n={n_trials}, p={p_success}) — coin flips")
    ax.set_xlabel("Number of heads in 20 flips")
    print(f"\nBinomial: Count of successes in n trials.")
    print(f"  Expected heads: {n_trials*p_success:.0f}, Actual mean: {data_binom.mean():.2f}")

    # --- 4. Poisson Distribution ---
    ax = axes[1, 1]
    lambda_rate = 3  # average 3 events per time period
    data_poisson = np.random.poisson(lambda_rate, 1000)
    ax.hist(data_poisson, bins=range(12), density=True, alpha=0.6, color="gold")
    ax.set_title(f"Poisson (λ={lambda_rate}) — events per interval")
    ax.set_xlabel("Number of events")
    print(f"\nPoisson: Count of rare events (calls per hour, defects per item).")
    print(f"  λ={lambda_rate}, Actual mean: {data_poisson.mean():.2f}")

    plt.tight_layout()
    plt.savefig("distributions.png")
    plt.close()
    print("\nAll 4 distributions saved: distributions.png")

    import os
    os.remove("distributions.png")

except ImportError:
    print("Install: pip install numpy matplotlib scipy")
