"""
Script: Decision Tree Classifier
What it does: Trains a Decision Tree — a model that makes decisions
by asking a series of yes/no questions about the features.
Easy to understand and visualize.

Install: pip install scikit-learn
"""

try:
    from sklearn.tree import DecisionTreeClassifier, export_text
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score

    # Load the iris dataset
    iris = load_iris()
    X, y = iris.data, iris.target

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # --- Train the Decision Tree ---
    tree = DecisionTreeClassifier(
        max_depth=3,       # limit depth to avoid overfitting
        random_state=42
    )
    tree.fit(X_train, y_train)

    # --- Evaluate ---
    y_pred = tree.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Decision Tree Accuracy: {accuracy:.2%}")

    # --- View the tree as text ---
    print("\n=== Decision Tree Structure ===")
    tree_text = export_text(tree, feature_names=iris.feature_names)
    print(tree_text)

    # --- Feature importance (which features are most useful?) ---
    print("=== Feature Importance ===")
    for name, importance in zip(iris.feature_names, tree.feature_importances_):
        bar = "#" * int(importance * 50)  # visual bar
        print(f"  {name:<25} {importance:.3f}  {bar}")

    # --- Predict a single sample ---
    sample = [[5.1, 3.5, 1.4, 0.2]]
    pred = tree.predict(sample)[0]
    proba = tree.predict_proba(sample)[0]  # probability for each class
    print(f"\nPrediction for {sample[0]}: {iris.target_names[pred]}")
    print(f"Probabilities: {dict(zip(iris.target_names, proba.round(2)))}")

except ImportError:
    print("Install: pip install scikit-learn")
