"""
Project: ATPG Pattern Analyzer
Tool context: Synopsys TetraMAX / DFTMAX / Mentor FastScan
What it does: Analyzes ATPG test pattern counts by type (stuck-at, transition,
IDDQ, path delay). Helps engineers understand test time and pattern file size
for each test mode. Outputs a time estimate based on ATE clock rate.

Usage:
    python 13_atpg_pattern_analyzer.py --report atpg_patterns.rpt
    python 13_atpg_pattern_analyzer.py --report atpg_patterns.rpt --ate-freq 100
"""

import re
import argparse

# Simulated TetraMAX pattern summary report
SAMPLE_REPORT = """\
# TetraMAX ATPG Pattern Summary
# Design: soc_top

==================================================
PATTERN COUNT BY FAULT MODEL
==================================================

Test mode             : Internal_Scan
Fault model           : Stuck-at (SA)
Total patterns        : 4215
  Random patterns     : 1200
  Deterministic patterns: 3015
Fault coverage        : 98.78%
Pattern file          : soc_top_sa.stil

Test mode             : Internal_Scan
Fault model           : Transition (TR)
Total patterns        : 2876
  Launch-on-shift     : 1450
  Launch-on-capture   : 1426
Fault coverage        : 95.40%
Pattern file          : soc_top_tr.stil

Test mode             : Internal_Scan
Fault model           : Cell-Aware (CA)
Total patterns        : 1542
Fault coverage        : 92.10%
Pattern file          : soc_top_ca.stil

Test mode             : IDDQ
Fault model           : IDDQ
Total patterns        : 64
Pattern file          : soc_top_iddq.stil

==================================================
SCAN CHAIN INFO
==================================================
Longest chain         : 6995 cells
ATE clock frequency   : 50 MHz
"""


def parse_pattern_report(text):
    """Extract pattern blocks for each fault model."""
    models = []
    current = None

    for line in text.splitlines():
        line = line.strip()
        if line.startswith("Fault model"):
            if current:
                models.append(current)
            current = {
                "fault_model": re.search(r":\s*(.+)", line).group(1).strip(),
                "patterns":    0,
                "coverage":    None,
                "file":        None,
                "test_mode":   None,
            }
        elif current:
            m_mode  = re.search(r"Test mode\s*:\s*(.+)", line)
            m_pats  = re.search(r"^Total patterns\s*:\s*(\d+)", line)
            m_cov   = re.search(r"Fault coverage\s*:\s*([\d.]+)%", line)
            m_file  = re.search(r"Pattern file\s*:\s*(\S+)", line)
            if m_mode:  current["test_mode"]   = m_mode.group(1).strip()
            if m_pats:  current["patterns"]    = int(m_pats.group(1))
            if m_cov:   current["coverage"]    = float(m_cov.group(1))
            if m_file:  current["file"]        = m_file.group(1).strip()

    if current:
        models.append(current)

    # Extract chain length and ATE freq
    chain_m = re.search(r"Longest chain\s*:\s*(\d+)", text)
    freq_m  = re.search(r"ATE clock frequency\s*:\s*(\d+)\s*MHz", text)

    chain_len  = int(chain_m.group(1)) if chain_m else 6000
    ate_freq   = int(freq_m.group(1))  if freq_m  else 50

    return models, chain_len, ate_freq


def estimate_test_time(patterns, chain_len, ate_freq_mhz):
    """
    Test time estimate:
      load_time  = chain_len / ate_freq  (seconds per pattern)
      total_time = patterns × load_time
    """
    cycles_per_pattern = chain_len + 10    # +10 for capture/apply
    time_per_pattern   = cycles_per_pattern / (ate_freq_mhz * 1e6)  # seconds
    total_time_s       = patterns * time_per_pattern
    return total_time_s


def print_analysis(models, chain_len, ate_freq, override_freq=None):
    if override_freq:
        ate_freq = override_freq

    GREEN = "\033[92m"
    YEL   = "\033[33m"
    RST   = "\033[0m"

    print("=" * 65)
    print("  ATPG PATTERN ANALYSIS REPORT")
    print("=" * 65)
    print(f"\n  Longest scan chain : {chain_len:,} cells")
    print(f"  ATE clock frequency: {ate_freq} MHz")
    print()

    total_patterns = sum(m["patterns"] for m in models)
    total_time_s   = sum(estimate_test_time(m["patterns"], chain_len, ate_freq) for m in models)

    print(f"  {'FAULT MODEL':<22} {'PATTERNS':>9} {'COVERAGE':>10} "
          f"{'EST TIME':>10} {'FILE'}")
    print("  " + "-" * 75)

    for m in models:
        t = estimate_test_time(m["patterns"], chain_len, ate_freq)
        cov_str = f"{m['coverage']:.2f}%" if m["coverage"] else "N/A"
        time_str = f"{t:.3f}s"
        print(f"  {m['fault_model']:<22} {m['patterns']:>9,} {cov_str:>10} "
              f"{time_str:>10} {m['file'] or 'N/A'}")

    print("  " + "-" * 75)
    total_min = total_time_s / 60
    print(f"  {'TOTAL':<22} {total_patterns:>9,} {'':>10} "
          f"{total_min:>9.2f}m")

    print(f"\n  Estimated total ATE test time: {total_time_s:.2f} s  "
          f"({total_min:.2f} min) at {ate_freq} MHz")

    if total_min > 5:
        print(f"  {YEL}Note: Test time > 5 min — consider increasing ATE frequency "
              f"or optimizing patterns.{RST}")
    else:
        print(f"  {GREEN}Test time within acceptable range.{RST}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Analyze ATPG pattern counts and test time")
parser.add_argument("--report",   help="ATPG pattern report file")
parser.add_argument("--ate-freq", type=int, help="Override ATE clock frequency (MHz)")
args = parser.parse_args()

text = open(args.report).read() if args.report else SAMPLE_REPORT
if not args.report:
    print("No report file — using sample data.\n")

models, chain_len, ate_freq = parse_pattern_report(text)
print_analysis(models, chain_len, ate_freq, override_freq=args.ate_freq)
