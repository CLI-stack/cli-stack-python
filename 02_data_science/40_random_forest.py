"""
Script: Random Forest Classifier
What it does: Trains a Random Forest — an ensemble of many Decision Trees.
It typically outperforms a single tree because it combines many predictions
(like getting the opinion of many experts instead of one).

Install: pip install scikit-learn
"""

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report

    # Load iris dataset
    iris = load_iris()
    X, y = iris.data, iris.target

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # --- Train Random Forest ---
    rf = RandomForestClassifier(
        n_estimators=100,    # number of trees in the forest
        max_depth=4,         # max depth of each tree
        random_state=42
    )
    rf.fit(X_train, y_train)

    # --- Evaluate ---
    y_pred = rf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Random Forest Accuracy: {accuracy:.2%}")

    print("\n=== Classification Report ===")
    print(classification_report(y_test, y_pred, target_names=iris.target_names))

    # --- Feature importance ---
    print("=== Feature Importance ===")
    importances = rf.feature_importances_
    for name, imp in sorted(zip(iris.feature_names, importances), key=lambda x: -x[1]):
        bar = "#" * int(imp * 60)
        print(f"  {name:<30} {imp:.3f}  {bar}")

    # --- Out-of-bag (OOB) score ---
    rf_oob = RandomForestClassifier(n_estimators=100, oob_score=True, random_state=42)
    rf_oob.fit(X_train, y_train)
    print(f"\nOut-of-Bag Score: {rf_oob.oob_score_:.2%}")
    # OOB uses data not seen during training to estimate accuracy

    # --- Predict probabilities ---
    sample = X_test[:3]
    proba = rf.predict_proba(sample)
    print("\n=== Prediction Probabilities (first 3 test samples) ===")
    for i, prob in enumerate(proba):
        predicted = iris.target_names[prob.argmax()]
        print(f"  Sample {i+1}: {dict(zip(iris.target_names, prob.round(2)))} → {predicted}")

except ImportError:
    print("Install: pip install scikit-learn")
