"""
Script: NumPy Basics
What it does: Introduces NumPy arrays — the foundation of data science in Python.
NumPy arrays are like lists but much faster and better for math operations.

Install: pip install numpy
"""

try:
    import numpy as np  # np is the standard alias for numpy

    # --- Creating arrays ---
    print("=== Creating Arrays ===")

    # From a Python list
    arr = np.array([1, 2, 3, 4, 5])
    print("1D array:", arr)
    print("Type:", type(arr))
    print("Data type:", arr.dtype)  # int64 = 64-bit integers

    # 2D array (matrix: rows and columns)
    matrix = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    print("\n2D array (matrix):\n", matrix)
    print("Shape:", matrix.shape)   # (rows, columns)

    # Special arrays
    zeros = np.zeros((3, 3))        # 3x3 matrix of zeros
    ones = np.ones((2, 4))          # 2x4 matrix of ones
    identity = np.eye(3)            # 3x3 identity matrix (diagonal = 1)
    range_arr = np.arange(0, 10, 2) # like range(): [0, 2, 4, 6, 8]

    print("\nZeros:\n", zeros)
    print("Ones:\n", ones)
    print("Range array:", range_arr)

    # --- Array indexing and slicing ---
    print("\n=== Indexing and Slicing ===")
    print("matrix[0]    =", matrix[0])       # first row
    print("matrix[1][2] =", matrix[1][2])    # row 1, column 2 = 6
    print("matrix[0, :]  =", matrix[0, :])   # all of row 0
    print("matrix[:, 1]  =", matrix[:, 1])   # all of column 1

    # --- Basic math on arrays ---
    print("\n=== Math Operations ===")
    a = np.array([1, 2, 3, 4])
    b = np.array([10, 20, 30, 40])

    print("a + b:", a + b)          # element-wise addition
    print("a * b:", a * b)          # element-wise multiplication
    print("a ** 2:", a ** 2)        # square each element
    print("Sum:", np.sum(a))
    print("Mean:", np.mean(a))
    print("Max:", np.max(b))

except ImportError:
    print("NumPy not installed. Run: pip install numpy")
