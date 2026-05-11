"""
Script: Train-Test Split and Cross Validation
What it does: Shows how to properly evaluate a machine learning model
by splitting data into training and testing sets.
Never test a model on the same data you trained it on — that would be cheating!

Install: pip install scikit-learn numpy
"""

try:
    import numpy as np
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.datasets import load_iris
    from sklearn.neighbors import KNeighborsClassifier

    # Load data
    iris = load_iris()
    X, y = iris.data, iris.target

    print(f"Total samples: {len(X)}")

    # --- Simple Train-Test Split ---
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,     # 20% for testing
        random_state=42,   # ensures reproducible split
        stratify=y         # keep same class ratio in train/test
    )

    print(f"\nTraining set:  {len(X_train)} samples ({len(X_train)/len(X)*100:.0f}%)")
    print(f"Test set:      {len(X_test)} samples ({len(X_test)/len(X)*100:.0f}%)")

    # Check class distribution is balanced
    print("\nClass distribution in test set:")
    for i, name in enumerate(iris.target_names):
        count = (y_test == i).sum()
        print(f"  {name}: {count}")

    # --- Train and evaluate ---
    model = KNeighborsClassifier(n_neighbors=3)
    model.fit(X_train, y_train)
    test_accuracy = model.score(X_test, y_test)
    print(f"\nTest accuracy: {test_accuracy:.2%}")

    # --- Cross-Validation (more reliable) ---
    # Splits data into K folds, trains K times, averages the results
    # This gives a more honest estimate of real-world performance
    cv_scores = cross_val_score(model, X, y, cv=5)  # 5-fold cross-validation
    print(f"\n=== 5-Fold Cross Validation ===")
    for i, score in enumerate(cv_scores, 1):
        print(f"  Fold {i}: {score:.2%}")
    print(f"  Mean: {cv_scores.mean():.2%} (+/- {cv_scores.std():.2%})")

    # --- Compare different K values ---
    print("\n=== Best K for KNN ===")
    for k in [1, 3, 5, 7, 9]:
        knn = KNeighborsClassifier(n_neighbors=k)
        scores = cross_val_score(knn, X, y, cv=5)
        print(f"  K={k}: {scores.mean():.2%}")

except ImportError:
    print("Install: pip install scikit-learn numpy")
