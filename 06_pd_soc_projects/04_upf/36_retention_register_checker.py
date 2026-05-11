"""
Project: Retention Register Checker
Tool context: Synopsys PA Compiler / Cadence Voltus
What it does: Checks which flip-flops in each power domain have retention
strategy defined (save/restore), and flags ones that don't.
Retention is required for state-preserving power-down (sleep modes).

Usage:
    python 36_retention_register_checker.py --report retention.rpt
"""

import re
import argparse
from collections import Counter, defaultdict

SAMPLE_REPORT = """\
# Retention Register Report — PA Compiler
# Design: soc_top
# Power Domain: PD_CPU (switchable — retention required)

RETENTION STRATEGY: save_restore
RETENTION CELL: RDFFRQ

REGISTERS WITH RETENTION:
  cpu_core/pc_reg[31:0]        CELL: RDFFRQ   SAVE_EN: save_en_cpu   RESTORE_EN: restore_en_cpu
  cpu_core/sp_reg[31:0]        CELL: RDFFRQ   SAVE_EN: save_en_cpu   RESTORE_EN: restore_en_cpu
  cpu_core/status_reg[7:0]     CELL: RDFFRQ   SAVE_EN: save_en_cpu   RESTORE_EN: restore_en_cpu
  alu_unit/acc_reg[31:0]       CELL: RDFFRQ   SAVE_EN: save_en_cpu   RESTORE_EN: restore_en_cpu

REGISTERS WITHOUT RETENTION:
  cpu_core/dbg_reg[31:0]       REASON: No retention cell — content lost on power-down
  cpu_core/trace_buf[127:0]    REASON: No retention cell — content lost on power-down
  alu_unit/temp_reg[31:0]      REASON: Intentionally excluded (don't-care on wake-up)

RETENTION SUMMARY:
  Total registers in PD_CPU    : 7
  With retention               : 4
  Without retention            : 3
    Intentional (excluded)     : 1
    Unintentional (missing)    : 2
"""


def parse_retention(text):
    with_ret = []
    without_ret = []

    for m in re.finditer(
        r"(\S+/\S+)\s+CELL:\s*(\S+)\s+SAVE_EN:\s*(\S+)\s+RESTORE_EN:\s*(\S+)", text
    ):
        with_ret.append({
            "reg":        m.group(1),
            "cell":       m.group(2),
            "save_en":    m.group(3),
            "restore_en": m.group(4),
        })

    # Parse without-retention section
    in_without = False
    for line in text.splitlines():
        if "WITHOUT RETENTION" in line:
            in_without = True
            continue
        if in_without and re.match(r"\s+\S+/\S+", line):
            parts = line.strip().split()
            if parts:
                reason_m = re.search(r"REASON:\s*(.+)", line)
                without_ret.append({
                    "reg":    parts[0],
                    "reason": reason_m.group(1) if reason_m else "Unknown",
                    "intentional": "Intentional" in (reason_m.group(1) if reason_m else ""),
                })
        elif in_without and "SUMMARY" in line:
            break

    summary = {}
    for key, pat in [
        ("total",        r"Total registers.*:\s*(\d+)"),
        ("with_ret",     r"With retention\s*:\s*(\d+)"),
        ("without_ret",  r"Without retention\s*:\s*(\d+)"),
        ("intentional",  r"Intentional.*:\s*(\d+)"),
        ("unintentional",r"Unintentional.*:\s*(\d+)"),
    ]:
        m = re.search(pat, text)
        if m:
            summary[key] = int(m.group(1))

    return with_ret, without_ret, summary


def print_report(with_ret, without_ret, summary):
    GREEN = "\033[92m"
    RED   = "\033[91m"
    YEL   = "\033[33m"
    RST   = "\033[0m"

    total  = summary.get("total", len(with_ret) + len(without_ret))
    with_n = summary.get("with_ret", len(with_ret))
    miss   = summary.get("unintentional", 0)
    pct    = with_n / total * 100 if total else 0

    print("=" * 65)
    print("  RETENTION REGISTER CHECK REPORT")
    print("=" * 65)
    print(f"\n  Total registers        : {total}")
    print(f"  With retention         : {GREEN}{with_n}{RST}  ({pct:.1f}%)")
    print(f"  Without retention      : {len(without_ret)}")
    print(f"    Intentional excluded : {summary.get('intentional', 0)}")
    print(f"    {RED}Unintentional missing : {miss}{RST}")

    print(f"\n  Registers WITH Retention:")
    print(f"  {'REGISTER':<40} {'CELL':<12} {'SAVE_EN':<15} {'RESTORE_EN'}")
    print("  " + "-" * 85)
    for r in with_ret:
        print(f"  {r['reg']:<40} {GREEN}{r['cell']:<12}{RST} {r['save_en']:<15} {r['restore_en']}")

    print(f"\n  Registers WITHOUT Retention:")
    print(f"  {'REGISTER':<40} {'INTENTIONAL':<14} {'REASON'}")
    print("  " + "-" * 85)
    for r in without_ret:
        intent = f"{YEL}YES{RST}" if r["intentional"] else f"{RED}NO{RST}"
        print(f"  {r['reg']:<40} {intent:<22} {r['reason'][:50]}")

    unint = [r for r in without_ret if not r["intentional"]]
    if unint:
        print(f"\n  {RED}Action Required — {len(unint)} register(s) missing retention unintentionally:{RST}")
        for r in unint:
            print(f"    {r['reg']}")
        print(f"\n  Fix: Add retention cell in UPF using:")
        print(f"    set_retention <domain> -elements {{{unint[0]['reg'].split('/')[0]}}} \\")
        print(f"        -save_condition {{save_en}} -restore_condition {{restore_en}}")
    else:
        print(f"\n  {GREEN}All non-excluded registers have retention. ✓{RST}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Check retention register configuration")
parser.add_argument("--report", help="Retention register report file")
args = parser.parse_args()

text = open(args.report).read() if args.report else SAMPLE_REPORT
if not args.report:
    print("No report file — using sample data.\n")

with_ret, without_ret, summary = parse_retention(text)
print_report(with_ret, without_ret, summary)
