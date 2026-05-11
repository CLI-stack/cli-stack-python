"""
Project: CDC/RDC HTML Dashboard Generator
Tool context: Spyglass CDC / RDC / VC CDC
What it does: Generates a self-contained HTML status dashboard for
CDC and RDC sign-off. Shows violation counts, domain map, and path table.
Suitable for posting to Confluence or sharing with the design team.

Usage:
    python 30_cdc_html_dashboard.py --output cdc_dashboard.html
"""

import argparse
from datetime import datetime

# Sample data (would be parsed from real reports in production)
SAMPLE_DATA = {
    "design":    "soc_top",
    "date":      datetime.now().strftime("%Y-%m-%d %H:%M"),
    "cdc": {
        "fatal": 1, "error": 5, "warning": 8,
        "total_crossings": 74, "synced": 73, "unsynced": 1,
    },
    "rdc": {
        "fatal": 0, "error": 3, "warning": 2,
    },
    "clock_domains": [
        {"name": "clk_core",  "freq": "500MHz", "type": "Sync",  "modules": "cpu_core, alu_unit, l1_cache"},
        {"name": "clk_axi",   "freq": "200MHz", "type": "Sync",  "modules": "dma_ctrl, axi_interconnect"},
        {"name": "clk_apb",   "freq": "100MHz", "type": "Sync",  "modules": "apb_bridge, gpio_ctrl"},
        {"name": "clk_pll",   "freq": "25MHz",  "type": "Async", "modules": "pll_ctrl"},
        {"name": "clk_uart",  "freq": "115KHz", "type": "Async", "modules": "uart_ctrl"},
        {"name": "clk_spi",   "freq": "50MHz",  "type": "Async", "modules": "spi_ctrl"},
    ],
    "top_violations": [
        {"sev": "Fatal",   "rule": "CDC_GLITCH",    "module": "clk_ctrl",  "desc": "Glitch on clock mux path"},
        {"sev": "Error",   "rule": "CDC_CONV_RULE",  "module": "cpu_core",  "desc": "Missing 2-FF sync: clk_core→clk_axi"},
        {"sev": "Error",   "rule": "CDC_CONV_RULE",  "module": "spi_ctrl",  "desc": "Missing 2-FF sync: clk_spi→clk_core"},
        {"sev": "Error",   "rule": "RDC_RESET_SYNC", "module": "uart_ctrl", "desc": "Missing reset sync: rstn_uart→rstn_core"},
    ],
}

SEV_COLOR = {"Fatal": "#e74c3c", "Error": "#e67e22", "Warning": "#f1c40f", "Info": "#3498db"}


def build_html(data):
    cdc = data["cdc"]
    rdc = data["rdc"]

    cov = cdc["synced"] / cdc["total_crossings"] * 100 if cdc["total_crossings"] else 0
    cov_color = "#27ae60" if cov >= 99 else "#e74c3c"

    domain_rows = ""
    for d in data["clock_domains"]:
        type_color = "#e67e22" if d["type"] == "Async" else "#27ae60"
        domain_rows += (
            f"<tr><td>{d['name']}</td><td>{d['freq']}</td>"
            f"<td><span style='color:{type_color};font-weight:bold'>{d['type']}</span></td>"
            f"<td>{d['modules']}</td></tr>\n"
        )

    viol_rows = ""
    for v in data["top_violations"]:
        col = SEV_COLOR.get(v["sev"], "#999")
        viol_rows += (
            f"<tr style='background:{col}22'>"
            f"<td><span style='background:{col};color:#fff;padding:2px 8px;border-radius:10px;font-size:11px'>"
            f"{v['sev']}</span></td>"
            f"<td>{v['rule']}</td><td>{v['module']}</td><td>{v['desc']}</td></tr>\n"
        )

    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>CDC/RDC Dashboard — {data['design']}</title>
<style>
body{{font-family:Arial,sans-serif;margin:0;background:#f5f5f5}}
.hdr{{background:#1a252f;color:#fff;padding:20px 30px}}
.hdr h1{{margin:0;font-size:20px}}.hdr p{{margin:4px 0;opacity:.7;font-size:13px}}
.body{{padding:20px 30px}}.row{{display:flex;gap:15px;margin-bottom:20px}}
.card{{background:#fff;border-radius:8px;padding:15px;flex:1;box-shadow:0 2px 4px rgba(0,0,0,.1)}}
.card h3{{margin:0 0 10px;font-size:13px;color:#555;text-transform:uppercase}}
.num{{font-size:28px;font-weight:bold}}.lbl{{font-size:12px;color:#777;margin-top:3px}}
.sec{{background:#fff;border-radius:8px;padding:20px;margin-bottom:20px;box-shadow:0 2px 4px rgba(0,0,0,.1)}}
.sec h2{{margin-top:0;font-size:15px;border-bottom:2px solid #eee;padding-bottom:8px}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
th{{background:#2c3e50;color:#fff;padding:8px 10px;text-align:left}}
td{{padding:7px 10px;border-bottom:1px solid #f0f0f0}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}
</style></head>
<body>
<div class="hdr">
  <h1>CDC / RDC Dashboard — {data['design']}</h1>
  <p>Generated: {data['date']}</p>
</div>
<div class="body">
  <div class="row">
    <div class="card"><h3>CDC Fatal</h3>
      <div class="num" style="color:#e74c3c">{cdc['fatal']}</div>
      <div class="lbl">Must be 0 for sign-off</div></div>
    <div class="card"><h3>CDC Error</h3>
      <div class="num" style="color:#e67e22">{cdc['error']}</div>
      <div class="lbl">Must be waived</div></div>
    <div class="card"><h3>CDC Warning</h3>
      <div class="num" style="color:#f39c12">{cdc['warning']}</div>
      <div class="lbl">Review required</div></div>
    <div class="card"><h3>RDC Error</h3>
      <div class="num" style="color:#e67e22">{rdc['error']}</div>
      <div class="lbl">Must be waived</div></div>
    <div class="card"><h3>Crossing Coverage</h3>
      <div class="num" style="color:{cov_color}">{cov:.1f}%</div>
      <div class="lbl">{cdc['synced']}/{cdc['total_crossings']} paths synchronized</div></div>
  </div>
  <div class="two">
    <div class="sec"><h2>Clock Domains ({len(data['clock_domains'])})</h2>
      <table><tr><th>Domain</th><th>Freq</th><th>Type</th><th>Modules</th></tr>
      {domain_rows}</table>
    </div>
    <div class="sec"><h2>Top Violations</h2>
      <table><tr><th>Severity</th><th>Rule</th><th>Module</th><th>Description</th></tr>
      {viol_rows}</table>
    </div>
  </div>
</div></body></html>"""
    return html


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Generate CDC/RDC HTML dashboard")
parser.add_argument("--output", default="cdc_dashboard.html")
args = parser.parse_args()

html = build_html(SAMPLE_DATA)
with open(args.output, "w") as f:
    f.write(html)

print(f"CDC/RDC Dashboard generated: {args.output}")
print(f"Open in browser: file://{args.output}")
