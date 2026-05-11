"""
Script: Advanced Statistics with SciPy
What it does: Performs statistical tests that go beyond basic statistics.
Hypothesis testing, distributions, and confidence intervals.

Install: pip install scipy numpy
"""

try:
    import numpy as np
    from scipy import stats

    # --- Hypothesis Testing ---
    # Question: Is the average height different from 170cm?
    print("=== One-Sample T-Test ===")
    heights = [168, 172, 175, 165, 178, 170, 166, 173, 171, 169, 174, 177]
    print(f"Heights: {heights}")
    print(f"Sample mean: {np.mean(heights):.2f} cm")

    # T-test compares sample mean to a known value
    t_stat, p_value = stats.ttest_1samp(heights, popmean=170)
    print(f"T-statistic: {t_stat:.4f}")
    print(f"P-value: {p_value:.4f}")

    alpha = 0.05  # significance level (5%)
    if p_value < alpha:
        print(f"P < {alpha}: Reject H0 — mean is significantly different from 170cm")
    else:
        print(f"P >= {alpha}: Fail to reject H0 — no significant difference from 170cm")

    # --- Two-Sample T-Test ---
    print("\n=== Two-Sample T-Test (Compare Two Groups) ===")
    group_a = [85, 90, 78, 92, 88, 76, 95, 82]  # treatment group
    group_b = [72, 75, 68, 80, 71, 73, 77, 79]  # control group

    t_stat, p_value = stats.ttest_ind(group_a, group_b)
    print(f"Group A mean: {np.mean(group_a):.2f}")
    print(f"Group B mean: {np.mean(group_b):.2f}")
    print(f"P-value: {p_value:.6f}")
    print("Groups are significantly different!" if p_value < 0.05 else "No significant difference.")

    # --- Pearson Correlation ---
    print("\n=== Pearson Correlation ===")
    study_hours = [2, 4, 6, 8, 10, 3, 5, 7, 9, 1]
    exam_scores  = [55, 65, 70, 85, 95, 60, 70, 80, 90, 45]

    corr, p_val = stats.pearsonr(study_hours, exam_scores)
    print(f"Correlation coefficient: {corr:.4f}")
    print(f"P-value: {p_val:.6f}")
    print("Strong positive correlation!" if corr > 0.7 else "Weak or moderate correlation.")

    # --- Confidence Interval ---
    print("\n=== 95% Confidence Interval for Mean ===")
    data = np.array(heights)
    ci = stats.t.interval(
        confidence=0.95,            # 95% confidence level
        df=len(data) - 1,           # degrees of freedom
        loc=np.mean(data),          # sample mean
        scale=stats.sem(data)       # standard error of the mean
    )
    print(f"Sample mean: {np.mean(data):.2f} cm")
    print(f"95% CI: ({ci[0]:.2f}, {ci[1]:.2f}) cm")

except ImportError:
    print("Install: pip install scipy numpy")
