"""
Script: Solving Linear Equations
What it does: Solves systems of linear equations using NumPy.
Example: Solve for x and y in:
  2x + 3y = 8
  x  - y  = 1

Install: pip install numpy
"""

try:
    import numpy as np

    # --- Solve a 2-variable system ---
    print("=== Solving System of Linear Equations ===")
    print("Equations:")
    print("  2x + 3y = 8")
    print("  x  - y  = 1")

    # Put coefficients in matrix form: Ax = b
    # A contains coefficients, b contains right-hand sides
    A = np.array([[2, 3],
                  [1, -1]])
    b = np.array([8, 1])

    # Solve: x = A_inverse × b
    solution = np.linalg.solve(A, b)
    x, y = solution

    print(f"\nSolution: x = {x:.4f}, y = {y:.4f}")

    # Verify: plug back in
    print("\nVerification:")
    print(f"  2({x:.2f}) + 3({y:.2f}) = {2*x + 3*y:.4f} (should be 8)")
    print(f"  {x:.2f} - {y:.2f} = {x - y:.4f} (should be 1)")

    # --- Solve a 3-variable system ---
    print("\n=== 3-Variable System ===")
    print("Equations:")
    print("  x + y + z  = 6")
    print("  2x - y + z = 3")
    print("  x + 2y - z = 2")

    A3 = np.array([[1,  1,  1],
                   [2, -1,  1],
                   [1,  2, -1]])
    b3 = np.array([6, 3, 2])

    solution3 = np.linalg.solve(A3, b3)
    print(f"\nSolution: x={solution3[0]:.2f}, y={solution3[1]:.2f}, z={solution3[2]:.2f}")

    # Verify all equations
    print("\nVerification:")
    for i, (a_row, rhs) in enumerate(zip(A3, b3), 1):
        lhs = np.dot(a_row, solution3)
        print(f"  Equation {i}: {lhs:.4f} = {rhs} ✓")

    # --- Check if a system is solvable ---
    print("\n=== Checking Solvability ===")
    det = np.linalg.det(A3)
    print(f"Determinant: {det:.4f}")
    if abs(det) > 1e-10:
        print("System has a unique solution (det ≠ 0)")
    else:
        print("System has no unique solution (det = 0)")

except ImportError:
    print("Install: pip install numpy")

    # Show manual solution for 2x2 system
    print("\nManual solution for 2x+3y=8, x-y=1:")
    print("From equation 2: x = y + 1")
    print("Substituting:    2(y+1) + 3y = 8")
    print("                 5y = 6 → y = 1.2")
    print("                 x = y + 1 = 2.2")
