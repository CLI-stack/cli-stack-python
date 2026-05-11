"""
Script: Matrix Operations with NumPy
What it does: Performs common matrix math operations.
Matrices are used in graphics, machine learning, physics simulations, and more.

Install: pip install numpy
"""

try:
    import numpy as np

    # --- Creating matrices ---
    print("=== Creating Matrices ===")
    A = np.array([[1, 2, 3],
                  [4, 5, 6],
                  [7, 8, 9]])

    B = np.array([[9, 8, 7],
                  [6, 5, 4],
                  [3, 2, 1]])

    print("Matrix A:\n", A)
    print("Matrix B:\n", B)

    # --- Basic operations ---
    print("\n=== Element-wise Operations ===")
    print("A + B:\n", A + B)        # add corresponding elements
    print("A - B:\n", A - B)        # subtract
    print("A * B:\n", A * B)        # multiply each element

    # --- Matrix multiplication (dot product) ---
    print("\n=== Matrix Multiplication (A @ B) ===")
    result = A @ B                  # @ operator = matrix multiply
    print(result)
    # Same as: np.dot(A, B)

    # --- Matrix properties ---
    print("\n=== Matrix Properties ===")
    C = np.array([[4, 7], [2, 6]])
    print("Matrix C:\n", C)
    print("Transpose:\n", C.T)               # flip rows and columns
    print("Determinant:", np.linalg.det(C))  # determinant

    # Inverse matrix (C × C_inv = Identity matrix)
    C_inv = np.linalg.inv(C)
    print("Inverse:\n", C_inv.round(4))

    # Verify: C × C_inv should equal the identity matrix
    identity = C @ C_inv
    print("C × C_inv (should be identity):\n", identity.round(2))

    # --- Eigenvalues and Eigenvectors ---
    print("\n=== Eigenvalues ===")
    eigenvalues, eigenvectors = np.linalg.eig(C)
    print(f"Eigenvalues: {eigenvalues.round(4)}")

    # --- Statistics on matrix ---
    print("\n=== Matrix Statistics ===")
    print(f"Sum of all elements: {A.sum()}")
    print(f"Row sums:    {A.sum(axis=1)}")   # axis=1 means across columns
    print(f"Column sums: {A.sum(axis=0)}")   # axis=0 means across rows
    print(f"Mean:        {A.mean():.2f}")
    print(f"Max:         {A.max()}")
    print(f"Min:         {A.min()}")

except ImportError:
    print("Install: pip install numpy")
