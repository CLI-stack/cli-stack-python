"""
Project: Sign-Off Checklist Generator
Tool context: Cross-flow (Lint/DFT/CDC/RDC/UPF/Physical)
What it does: Generates a sign-off checklist document (HTML or text)
that tracks which tasks are complete, in-progress, or pending.
Updates checklist status based on input config. Useful for milestone reviews.

Usage:
    python 47_signoff_checklist_generator.py --format html --output signoff.html
    python 47_signoff_checklist_generator.py --format text
"""

import argparse
from datetime import datetime

CHECKLIST = [
    # (flow, item, status, assignee, notes)
    # status: done / in_progress / pending / blocked
    ("LINT", "Run SpyGlass Lint on final RTL",                "done",        "alice",   ""),
    ("LINT", "Resolve all Fatal violations",                   "done",        "alice",   ""),
    ("LINT", "Waive and approve all Error violations",         "in_progress", "alice",   "3 waivers pending approval"),
    ("LINT", "Resolve Warning violations (target < 20)",       "in_progress", "alice",   "15 remaining"),

    ("DFT",  "Complete scan insertion (DFTMAX)",               "done",        "bob",     ""),
    ("DFT",  "Run ATPG stuck-at patterns (target ≥ 99%)",     "done",        "bob",     "98.78% — need +0.22%"),
    ("DFT",  "Run ATPG transition patterns (target ≥ 96%)",   "in_progress", "bob",     "95.4% — under target"),
    ("DFT",  "Validate all MBIST memories pass",               "in_progress", "bob",     "1/5 memory failing"),
    ("DFT",  "Verify scan chain imbalance < 10%",             "done",        "bob",     "8.5% — OK"),

    ("CDC",  "Run Spyglass CDC on final netlist",              "done",        "charlie", ""),
    ("CDC",  "Resolve all Fatal CDC violations",               "in_progress", "charlie", "1 fatal remaining: CDC_GLITCH"),
    ("CDC",  "Waive all Error CDC violations",                 "pending",     "charlie", "Waiting on Fatal fix first"),
    ("CDC",  "Run RDC analysis",                               "done",        "charlie", ""),
    ("CDC",  "Resolve RDC Error violations",                   "in_progress", "charlie", "3 remaining"),

    ("UPF",  "Complete UPF coding and review",                 "done",        "diana",   ""),
    ("UPF",  "Run PA Compiler checks",                         "done",        "diana",   ""),
    ("UPF",  "Insert all missing isolation cells (target=0)",  "in_progress", "diana",   "2 still missing"),
    ("UPF",  "Insert all missing level shifters (target=0)",   "done",        "diana",   ""),
    ("UPF",  "Define retention for all switchable FFs",        "in_progress", "diana",   "1 missing"),
    ("UPF",  "Verify AO cell placement",                       "done",        "diana",   ""),

    ("TIMING","Complete STA for all corners",                  "done",        "eve",     ""),
    ("TIMING","Close setup timing (WNS ≥ 0)",                  "blocked",     "eve",     "WNS = -0.05ns — needs ECO"),
    ("TIMING","Close hold timing (WNS ≥ 0)",                   "done",        "eve",     ""),
    ("TIMING","Resolve max transition violations",              "done",        "eve",     ""),

    ("PD",   "DRC clean",                                      "done",        "frank",   ""),
    ("PD",   "LVS clean",                                      "done",        "frank",   ""),
    ("PD",   "Antenna violations resolved",                    "in_progress", "frank",   "12 remaining"),
    ("PD",   "Power/ground connectivity verified",             "done",        "frank",   ""),
    ("PD",   "EMIR analysis complete",                         "pending",     "frank",   ""),
]

STATUS_ICON = {
    "done":        "✓",
    "in_progress": "►",
    "pending":     "○",
    "blocked":     "✗",
}
STATUS_COLOR_HTML = {
    "done":        "#27ae60",
    "in_progress": "#e67e22",
    "pending":     "#95a5a6",
    "blocked":     "#e74c3c",
}


def generate_text(checklist, design="soc_top"):
    done  = sum(1 for _, _, s, _, _ in checklist if s == "done")
    total = len(checklist)

    print(f"Sign-Off Checklist — {design}")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Progress: {done}/{total} items done ({done/total*100:.0f}%)\n")

    current_flow = None
    for flow, item, status, assignee, notes in checklist:
        if flow != current_flow:
            print(f"\n  ── {flow} ──")
            current_flow = flow
        icon = STATUS_ICON.get(status, "?")
        note_str = f"  [{notes}]" if notes else ""
        print(f"    [{icon}] {item}")
        print(f"        Owner: {assignee}  Status: {status.upper()}{note_str}")


def generate_html(checklist, design="soc_top"):
    done  = sum(1 for _, _, s, _, _ in checklist if s == "done")
    total = len(checklist)
    pct   = done / total * 100

    rows = ""
    current_flow = None
    for flow, item, status, assignee, notes in checklist:
        if flow != current_flow:
            rows += (f"<tr style='background:#2c3e50;color:#fff'>"
                     f"<td colspan='4'><strong>{flow}</strong></td></tr>\n")
            current_flow = flow
        color = STATUS_COLOR_HTML.get(status, "#999")
        icon  = STATUS_ICON.get(status, "?")
        notes_html = f"<br><small style='color:#777'>{notes}</small>" if notes else ""
        rows += (
            f"<tr><td>{item}{notes_html}</td>"
            f"<td><span style='color:{color};font-size:18px'>{icon}</span>"
            f" <strong style='color:{color}'>{status.upper()}</strong></td>"
            f"<td>{assignee}</td></tr>\n"
        )

    html = f"""<!DOCTYPE html><html>
<head><title>Sign-Off Checklist — {design}</title>
<style>
body{{font-family:Arial;margin:30px;background:#f5f5f5}}
.header{{background:#1a252f;color:#fff;padding:20px;border-radius:8px;margin-bottom:20px}}
.header h1{{margin:0;font-size:20px}}.header p{{margin:4px 0;opacity:.8}}
.progress-bar{{background:#ddd;border-radius:10px;height:20px;margin:10px 0}}
.progress-fill{{background:#27ae60;height:100%;border-radius:10px;width:{pct:.0f}%}}
table{{width:100%;border-collapse:collapse;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 4px rgba(0,0,0,.1)}}
th{{background:#34495e;color:#fff;padding:10px;text-align:left}}
td{{padding:9px 12px;border-bottom:1px solid #eee}}
</style></head>
<body>
<div class="header">
  <h1>Sign-Off Checklist — {design}</h1>
  <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}  |
     Progress: {done}/{total} ({pct:.0f}%)</p>
  <div class="progress-bar"><div class="progress-fill"></div></div>
</div>
<table>
<tr><th>Checklist Item</th><th>Status</th><th>Owner</th></tr>
{rows}
</table></body></html>"""
    return html


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Generate sign-off checklist")
parser.add_argument("--format", choices=["text","html"], default="text")
parser.add_argument("--output", default="signoff_checklist.html")
parser.add_argument("--design", default="soc_top")
args = parser.parse_args()

if args.format == "html":
    html = generate_html(CHECKLIST, args.design)
    with open(args.output, "w") as f:
        f.write(html)
    print(f"HTML checklist generated: {args.output}")
else:
    generate_text(CHECKLIST, args.design)
