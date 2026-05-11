"""
Script: K-Means Clustering
What it does: Groups similar data points together automatically.
Unlike classification, clustering doesn't need labeled data —
it discovers groups on its own (unsupervised learning).

Install: pip install scikit-learn numpy matplotlib
"""

try:
    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn.cluster import KMeans
    from sklearn.datasets import make_blobs  # generates sample clustered data

    # --- Generate sample data with 3 natural clusters ---
    X, true_labels = make_blobs(
        n_samples=150,     # 150 data points
        centers=3,          # 3 cluster centers
        cluster_std=0.8,    # how spread out each cluster is
        random_state=42
    )

    print(f"Generated {len(X)} data points")
    print(f"Data shape: {X.shape} (150 points, 2 features each)")

    # --- Apply K-Means ---
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    kmeans.fit(X)  # find the clusters

    # Get cluster assignments for each point
    cluster_labels = kmeans.labels_
    # Get the center of each cluster
    centers = kmeans.cluster_centers_

    print(f"\nCluster centers:\n{centers.round(2)}")
    print(f"\nCluster sizes:")
    for i in range(3):
        count = (cluster_labels == i).sum()
        print(f"  Cluster {i}: {count} points")

    # --- Predict which cluster a new point belongs to ---
    new_point = np.array([[0, 0]])
    cluster = kmeans.predict(new_point)[0]
    print(f"\nNew point (0, 0) belongs to cluster: {cluster}")

    # --- Visualize ---
    colors = ["red", "blue", "green"]
    plt.figure(figsize=(8, 6))

    for i in range(3):
        mask = cluster_labels == i
        plt.scatter(X[mask, 0], X[mask, 1], c=colors[i], alpha=0.5, label=f"Cluster {i}")

    plt.scatter(centers[:, 0], centers[:, 1], c="black", marker="x", s=200,
                linewidths=3, label="Centers")
    plt.title("K-Means Clustering Result")
    plt.legend()
    plt.tight_layout()
    plt.savefig("kmeans_clusters.png")
    plt.close()
    print("\nChart saved: kmeans_clusters.png")

    import os
    os.remove("kmeans_clusters.png")

except ImportError:
    print("Install: pip install scikit-learn numpy matplotlib")
