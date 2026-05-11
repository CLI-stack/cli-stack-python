"""
Project: Lint HTML Dashboard Generator
Tool context: Spyglass Lint / Questa Lint
What it does: Generates a self-contained HTML dashboard from lint results.
Includes severity pie chart, top modules/rules, and a full violation table.
Can be shared via email or posted to a team wiki/confluence page.

Usage:
    python 08_lint_dashboard_html.py --report lint.rpt --output lint_dashboard.html
"""

import re
import argparse
from collections import Counter
from datetime import datetime

SAMPLE_REPORT = """\
Fatal|W_COMB_LOOP|fifo_ctrl|rtl/fifo_ctrl.v:134|Combinational loop detected
Error|W_NET_NO_LOAD|cpu_core|rtl/cpu_core.v:245|Net has no load
Error|W_NET_NO_LOAD|cpu_core|rtl/cpu_core.v:312|Net has no load
Error|W_MUX_SEL_UNDRIVEN|apb_bridge|rtl/apb_bridge.v:67|Mux select undriven
Warning|W_REGS_NO_RESET|alu_unit|rtl/alu_unit.v:88|Register has no reset
Warning|W_REGS_NO_RESET|dma_ctrl|rtl/dma_ctrl.v:120|Register has no reset
Warning|W_PORT_UNCONNECTED|soc_top|rtl/soc_top.v:200|Port unconnected
Info|W_CONST_DRIVER|dma_ctrl|rtl/dma_ctrl.v:55|Signal driven by constant
"""

SEV_CSS = {
    "Fatal":   "#e74c3c",
    "Error":   "#e67e22",
    "Warning": "#f1c40f",
    "Info":    "#3498db",
}
SEV_RANK = {"Fatal": 0, "Error": 1, "Warning": 2, "Info": 3}


def parse_violations(text):
    pattern = re.compile(r"^(Fatal|Error|Warning|Info)\|(\S+)\|(\S+)\|(.+):(\d+)\|(.+)$")
    violations = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = pattern.match(line)
        if m:
            violations.append({
                "severity": m.group(1), "rule":    m.group(2),
                "module":   m.group(3), "file":    m.group(4),
                "line":     int(m.group(5)), "message": m.group(6),
            })
    return sorted(violations, key=lambda v: SEV_RANK.get(v["severity"], 9))


def build_html(violations, design_name="soc_top"):
    sev_counts  = Counter(v["severity"] for v in violations)
    rule_counts = Counter(v["rule"]     for v in violations)
    mod_counts  = Counter(v["module"]   for v in violations)
    total       = len(violations)
    timestamp   = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Build violation table rows
    table_rows = ""
    for v in violations:
        color = SEV_CSS.get(v["severity"], "#fff")
        table_rows += (
            f'<tr style="background:{color}22">'
            f'<td><span class="badge" style="background:{color}">{v["severity"]}</span></td>'
            f'<td>{v["rule"]}</td><td>{v["module"]}</td>'
            f'<td>{v["file"]}:{v["line"]}</td>'
            f'<td>{v["message"]}</td></tr>\n'
        )

    # Build top-rules and top-modules rows
    def top_rows(counter, top=8):
        rows = ""
        max_c = counter.most_common(1)[0][1] if counter else 1
        for name, cnt in counter.most_common(top):
            bar_w = int(200 * cnt / max_c)
            rows += (f'<tr><td>{name}</td><td>{cnt}</td>'
                     f'<td><div style="width:{bar_w}px;height:14px;background:#2980b9;border-radius:3px"></div></td></tr>\n')
        return rows

    sev_badges = "".join(
        f'<div class="stat-card" style="border-left:5px solid {SEV_CSS.get(s,"#999")}">'
        f'<div class="stat-num" style="color:{SEV_CSS.get(s,"#999")}">{sev_counts.get(s,0)}</div>'
        f'<div class="stat-lbl">{s}</div></div>'
        for s in ["Fatal", "Error", "Warning", "Info"]
    )

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Lint Dashboard — {design_name}</title>
  <style>
    body{{font-family:Arial,sans-serif;margin:0;background:#f5f5f5;color:#333}}
    .header{{background:#2c3e50;color:#fff;padding:20px 30px}}
    .header h1{{margin:0;font-size:22px}} .header p{{margin:4px 0;opacity:.7;font-size:13px}}
    .content{{padding:20px 30px}}
    .stat-row{{display:flex;gap:15px;margin-bottom:25px}}
    .stat-card{{background:#fff;border-radius:8px;padding:15px 20px;flex:1;box-shadow:0 2px 4px rgba(0,0,0,.1)}}
    .stat-num{{font-size:32px;font-weight:bold}} .stat-lbl{{font-size:13px;color:#777;margin-top:4px}}
    .section{{background:#fff;border-radius:8px;padding:20px;margin-bottom:20px;box-shadow:0 2px 4px rgba(0,0,0,.1)}}
    .section h2{{margin-top:0;font-size:16px;border-bottom:2px solid #eee;padding-bottom:8px}}
    table{{width:100%;border-collapse:collapse;font-size:13px}}
    th{{background:#34495e;color:#fff;padding:8px 10px;text-align:left}}
    td{{padding:7px 10px;border-bottom:1px solid #f0f0f0}}
    .badge{{display:inline-block;color:#fff;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:bold}}
    .two-col{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}
  </style>
</head>
<body>
<div class="header">
  <h1>Lint Dashboard — {design_name}</h1>
  <p>Generated: {timestamp} &nbsp;|&nbsp; Total violations: {total}</p>
</div>
<div class="content">
  <div class="stat-row">{sev_badges}</div>
  <div class="two-col">
    <div class="section"><h2>Top Rules</h2>
      <table><tr><th>Rule</th><th>Count</th><th>Bar</th></tr>{top_rows(rule_counts)}</table>
    </div>
    <div class="section"><h2>Top Modules</h2>
      <table><tr><th>Module</th><th>Count</th><th>Bar</th></tr>{top_rows(mod_counts)}</table>
    </div>
  </div>
  <div class="section"><h2>All Violations</h2>
    <table>
      <tr><th>Severity</th><th>Rule</th><th>Module</th><th>File:Line</th><th>Message</th></tr>
      {table_rows}
    </table>
  </div>
</div>
</body></html>"""
    return html


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Generate HTML lint dashboard")
parser.add_argument("--report",  help="Lint report file")
parser.add_argument("--output",  default="lint_dashboard.html")
parser.add_argument("--design",  default="soc_top")
args = parser.parse_args()

text = open(args.report).read() if args.report else SAMPLE_REPORT
if not args.report:
    print("No report file given — using sample data.\n")

violations = parse_violations(text)
html       = build_html(violations, args.design)

with open(args.output, "w") as f:
    f.write(html)

print(f"Dashboard generated: {args.output}  ({len(violations)} violations)")
print(f"Open in a browser: file://{args.output}")
