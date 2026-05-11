"""
Script: Classification with Machine Learning
What it does: Trains a model to classify items into categories.
Example: classify an iris flower species based on petal and sepal measurements.
Uses the famous Iris dataset — a classic beginner ML example.

Install: pip install scikit-learn
"""

try:
    from sklearn.datasets import load_iris       # built-in sample dataset
    from sklearn.model_selection import train_test_split
    from sklearn.neighbors import KNeighborsClassifier  # K-Nearest Neighbors
    from sklearn.metrics import accuracy_score, classification_report

    # --- Load the Iris dataset ---
    iris = load_iris()
    X = iris.data    # features: sepal length, sepal width, petal length, petal width
    y = iris.target  # labels: 0=setosa, 1=versicolor, 2=virginica

    print("=== Iris Dataset ===")
    print(f"Total samples: {len(X)}")
    print(f"Features: {iris.feature_names}")
    print(f"Classes: {iris.target_names}")
    print(f"\nFirst 5 rows:\n{X[:5]}")

    # --- Split into training and test sets ---
    # 80% for training, 20% for testing
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"\nTraining samples: {len(X_train)}")
    print(f"Testing samples:  {len(X_test)}")

    # --- Train the model ---
    # KNN classifies based on the K nearest data points
    model = KNeighborsClassifier(n_neighbors=3)
    model.fit(X_train, y_train)  # train on training data

    # --- Evaluate the model ---
    y_pred = model.predict(X_test)  # predict on test data
    accuracy = accuracy_score(y_test, y_pred)

    print(f"\n=== Model Accuracy: {accuracy:.2%} ===")
    print("\nDetailed Report:")
    print(classification_report(y_test, y_pred, target_names=iris.target_names))

    # --- Predict a new flower ---
    new_flower = [[5.1, 3.5, 1.4, 0.2]]  # [sepal_l, sepal_w, petal_l, petal_w]
    prediction = model.predict(new_flower)[0]
    print(f"New flower prediction: {iris.target_names[prediction]}")

except ImportError:
    print("Install: pip install scikit-learn")
