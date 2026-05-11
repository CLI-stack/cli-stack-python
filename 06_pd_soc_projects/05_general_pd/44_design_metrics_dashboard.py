"""
Project: Design Metrics Dashboard (All Flows)
Tool context: Cross-flow aggregator
What it does: Aggregates sign-off metrics from all flows (Lint, DFT, CDC, RDC, UPF)
into a single dashboard. Red/Yellow/Green status per gate.
The single pane of glass for tapeout sign-off tracking.

Usage:
    python 44_design_metrics_dashboard.py
    python 44_design_metrics_dashboard.py --config metrics.json
"""

import json
import argparse
from datetime import datetime

# Current design metrics (would be parsed from actual reports in production)
DEFAULT_METRICS = {
    "design":      "soc_top",
    "revision":    "RTL_FREEZE_v1.2",
    "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M"),
    "lint": {
        "fatal":    0,
        "error":    3,
        "warning":  15,
        "waivers":  12,
        "waivers_approved": 12,
        "target_fatal": 0,
        "target_error": 0,
    },
    "dft": {
        "sa_coverage":      98.78,
        "tr_coverage":      95.40,
        "ca_coverage":      92.10,
        "scan_imbalance_pct": 8.5,
        "dft_drc_errors":   0,
        "target_sa":        99.0,
        "target_tr":        96.0,
        "target_ca":        95.0,
    },
    "cdc": {
        "fatal":    1,
        "error":    5,
        "warning":  8,
        "waivers":  10,
        "crossing_coverage_pct": 98.6,
        "target_fatal": 0,
    },
    "rdc": {
        "fatal":    0,
        "error":    3,
        "warning":  2,
        "target_fatal": 0,
    },
    "upf": {
        "iso_missing":   2,
        "ls_missing":    0,
        "ret_missing":   1,
        "ao_errors":     0,
        "pa_errors":     3,
        "target_missing":0,
    },
}

STATUS_OK   = "\033[92mPASS\033[0m"
STATUS_WARN = "\033[33mWARN\033[0m"
STATUS_FAIL = "\033[91mFAIL\033[0m"
GREEN = "\033[92m"
RED   = "\033[91m"
YEL   = "\033[33m"
RST   = "\033[0m"


def gate(condition, warn_condition=None):
    if condition:
        return STATUS_OK
    if warn_condition and warn_condition():
        return STATUS_WARN
    return STATUS_FAIL


def print_dashboard(m):
    lint = m["lint"]
    dft  = m["dft"]
    cdc  = m["cdc"]
    rdc  = m["rdc"]
    upf  = m["upf"]

    print("=" * 70)
    print(f"  SOC SIGN-OFF METRICS DASHBOARD")
    print(f"  Design: {m['design']}   Rev: {m['revision']}")
    print(f"  {m['timestamp']}")
    print("=" * 70)

    print(f"\n  {'FLOW':<10} {'METRIC':<35} {'VALUE':>12} {'STATUS'}")
    print("  " + "-" * 65)

    # ── LINT ──────────────────────────────────────────────────────────────────
    def r(flow, metric, value, status):
        print(f"  {flow:<10} {metric:<35} {str(value):>12} {status}")

    r("LINT", "Fatal violations",
      lint["fatal"],
      gate(lint["fatal"] <= lint["target_fatal"]))
    r("LINT", "Error violations (unwaived)",
      lint["error"],
      gate(lint["error"] == 0))
    r("LINT", "Waivers approved",
      f"{lint['waivers_approved']}/{lint['waivers']}",
      gate(lint["waivers_approved"] == lint["waivers"]))

    # ── DFT ───────────────────────────────────────────────────────────────────
    print("  " + "─" * 65)
    r("DFT", "Stuck-at coverage",
      f"{dft['sa_coverage']:.2f}%",
      gate(dft["sa_coverage"] >= dft["target_sa"]))
    r("DFT", "Transition coverage",
      f"{dft['tr_coverage']:.2f}%",
      gate(dft["tr_coverage"] >= dft["target_tr"]))
    r("DFT", "Cell-aware coverage",
      f"{dft['ca_coverage']:.2f}%",
      gate(dft["ca_coverage"] >= dft["target_ca"]))
    r("DFT", "Scan chain imbalance",
      f"{dft['scan_imbalance_pct']:.1f}%",
      gate(dft["scan_imbalance_pct"] <= 10.0,
           lambda: dft["scan_imbalance_pct"] <= 15.0))
    r("DFT", "DFT DRC errors",
      dft["dft_drc_errors"],
      gate(dft["dft_drc_errors"] == 0))

    # ── CDC ───────────────────────────────────────────────────────────────────
    print("  " + "─" * 65)
    r("CDC", "Fatal violations",
      cdc["fatal"],
      gate(cdc["fatal"] <= cdc["target_fatal"]))
    r("CDC", "Error violations",
      cdc["error"],
      gate(cdc["error"] == 0))
    r("CDC", "Crossing coverage",
      f"{cdc['crossing_coverage_pct']:.1f}%",
      gate(cdc["crossing_coverage_pct"] >= 99.0,
           lambda: cdc["crossing_coverage_pct"] >= 95.0))

    # ── RDC ───────────────────────────────────────────────────────────────────
    print("  " + "─" * 65)
    r("RDC", "Fatal violations",
      rdc["fatal"],
      gate(rdc["fatal"] <= rdc["target_fatal"]))
    r("RDC", "Error violations",
      rdc["error"],
      gate(rdc["error"] == 0))

    # ── UPF ───────────────────────────────────────────────────────────────────
    print("  " + "─" * 65)
    r("UPF", "Missing isolation cells",
      upf["iso_missing"],
      gate(upf["iso_missing"] == 0))
    r("UPF", "Missing level shifters",
      upf["ls_missing"],
      gate(upf["ls_missing"] == 0))
    r("UPF", "Missing retention cells",
      upf["ret_missing"],
      gate(upf["ret_missing"] == 0))
    r("UPF", "Always-on cell errors",
      upf["ao_errors"],
      gate(upf["ao_errors"] == 0))

    # Overall verdict
    all_metrics = [
        lint["fatal"] <= lint["target_fatal"],
        lint["error"] == 0,
        lint["waivers_approved"] == lint["waivers"],
        dft["sa_coverage"] >= dft["target_sa"],
        dft["tr_coverage"] >= dft["target_tr"],
        dft["ca_coverage"] >= dft["target_ca"],
        dft["dft_drc_errors"] == 0,
        cdc["fatal"] == 0,
        rdc["fatal"] == 0,
        upf["iso_missing"] == 0,
        upf["ls_missing"] == 0,
        upf["ret_missing"] == 0,
    ]
    fails = sum(1 for g in all_metrics if not g)

    print("\n" + "=" * 70)
    if fails == 0:
        print(f"  {GREEN}OVERALL: TAPEOUT SIGN-OFF APPROVED ✓{RST}")
    else:
        print(f"  {RED}OVERALL: SIGN-OFF BLOCKED — {fails} gate(s) failing{RST}")
    print("=" * 70)


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Design sign-off metrics dashboard")
parser.add_argument("--config", help="Metrics JSON file")
args = parser.parse_args()

metrics = json.load(open(args.config)) if args.config else DEFAULT_METRICS
print_dashboard(metrics)
