"""
Project: UPF File Parser
Tool context: Synopsys PA Compiler / Cadence Voltus / Mentor Calibre
What it does: Parses a UPF (Unified Power Format) file and extracts
power domains, supply sets, supply nets, and domain hierarchy.
Gives a structured summary of the power intent.

Usage:
    python 31_upf_parser.py --upf design.upf
"""

import re
import argparse
from collections import defaultdict

SAMPLE_UPF = """\
# UPF File — soc_top
# Version: UPF 2.1

set_design_top soc_top

# Supply nets
create_supply_net VDD   -domain soc_top
create_supply_net VDD_L -domain soc_top
create_supply_net VSS   -domain soc_top

# Supply ports
create_supply_port VDD   -direction in -domain soc_top
create_supply_port VDD_L -direction in -domain soc_top
create_supply_port VSS   -direction in -domain soc_top

# Power domains
create_power_domain PD_TOP  -include_scope
create_power_domain PD_CPU  -elements {cpu_core alu_unit l1_cache}
create_power_domain PD_DMA  -elements {dma_ctrl}
create_power_domain PD_PERIPH -elements {apb_bridge uart_ctrl spi_ctrl gpio_ctrl}
create_power_domain PD_PLL  -elements {pll_ctrl clk_ctrl} -atomic

# Supply sets
create_supply_set SS_TOP   -function {power VDD}   -function {ground VSS}
create_supply_set SS_CPU   -function {power VDD}   -function {ground VSS}
create_supply_set SS_DMA   -function {power VDD}   -function {ground VSS}
create_supply_set SS_PERIPH -function {power VDD_L} -function {ground VSS}
create_supply_set SS_PLL   -function {power VDD}   -function {ground VSS}

# Associate supply sets with power domains
associate_supply_set SS_TOP    -handle PD_TOP.primary
associate_supply_set SS_CPU    -handle PD_CPU.primary
associate_supply_set SS_DMA    -handle PD_DMA.primary
associate_supply_set SS_PERIPH -handle PD_PERIPH.primary
associate_supply_set SS_PLL    -handle PD_PLL.primary

# Power state table
add_power_state PD_CPU -state {ON  -supply_expr {power == {FULL_ON, 1.0}}}
add_power_state PD_CPU -state {OFF -supply_expr {power == {OFF}}}
add_power_state PD_DMA -state {ON  -supply_expr {power == {FULL_ON, 1.0}}}
add_power_state PD_DMA -state {OFF -supply_expr {power == {OFF}}}
"""


def parse_upf(text):
    results = {
        "design":         None,
        "supply_nets":    [],
        "supply_ports":   [],
        "power_domains":  [],
        "supply_sets":    [],
        "associations":   [],
        "power_states":   defaultdict(list),
    }

    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#") or not line:
            continue

        # Design top
        m = re.match(r"set_design_top\s+(\S+)", line)
        if m:
            results["design"] = m.group(1)

        # Supply nets
        m = re.match(r"create_supply_net\s+(\S+)\s+-domain\s+(\S+)", line)
        if m:
            results["supply_nets"].append({"name": m.group(1), "domain": m.group(2)})

        # Supply ports
        m = re.match(r"create_supply_port\s+(\S+)\s+-direction\s+(\S+)\s+-domain\s+(\S+)", line)
        if m:
            results["supply_ports"].append({"name": m.group(1), "dir": m.group(2), "domain": m.group(3)})

        # Power domains
        m = re.match(r"create_power_domain\s+(\S+)(.*)", line)
        if m:
            name   = m.group(1)
            rest   = m.group(2)
            elems  = re.search(r"-elements\s+\{([^}]+)\}", rest)
            atomic = "-atomic" in rest
            results["power_domains"].append({
                "name":    name,
                "elements":elems.group(1).strip().split() if elems else ["*"],
                "atomic":  atomic,
            })

        # Supply sets
        m = re.match(r"create_supply_set\s+(\S+)(.*)", line)
        if m:
            name = m.group(1)
            fns  = re.findall(r"-function\s+\{(\S+)\s+(\S+)\}", m.group(2))
            results["supply_sets"].append({"name": name, "functions": fns})

        # Associations
        m = re.match(r"associate_supply_set\s+(\S+)\s+-handle\s+(\S+)", line)
        if m:
            results["associations"].append({"supply_set": m.group(1), "handle": m.group(2)})

        # Power states
        m = re.match(r"add_power_state\s+(\S+)\s+-state\s+\{(\S+)", line)
        if m:
            results["power_states"][m.group(1)].append(m.group(2))

    return results


def print_upf_summary(upf):
    CYN = "\033[36m"
    GRN = "\033[92m"
    RST = "\033[0m"

    print("=" * 65)
    print(f"  UPF POWER INTENT SUMMARY — {upf['design']}")
    print("=" * 65)

    print(f"\n  Supply Nets  ({len(upf['supply_nets'])}): "
          + ", ".join(n["name"] for n in upf["supply_nets"]))
    print(f"  Supply Ports ({len(upf['supply_ports'])}): "
          + ", ".join(p["name"] for p in upf["supply_ports"]))

    print(f"\n  Power Domains ({len(upf['power_domains'])}):")
    print(f"  {'DOMAIN':<15} {'ATOMIC':<8} {'ELEMENTS'}")
    print("  " + "-" * 65)
    for pd in upf["power_domains"]:
        atomic = "YES" if pd["atomic"] else "NO"
        elems  = ", ".join(pd["elements"][:4])
        if len(pd["elements"]) > 4:
            elems += f" ... (+{len(pd['elements'])-4})"
        print(f"  {CYN}{pd['name']:<15}{RST} {atomic:<8} {elems}")

    print(f"\n  Supply Sets ({len(upf['supply_sets'])}):")
    for ss in upf["supply_sets"]:
        fns = "  ".join(f"{f[0]}:{f[1]}" for f in ss["functions"])
        print(f"    {ss['name']:<15}  {fns}")

    print(f"\n  Domain-SupplySet Associations:")
    for a in upf["associations"]:
        print(f"    {a['supply_set']:<15} → {a['handle']}")

    print(f"\n  Power States per Domain:")
    for domain, states in upf["power_states"].items():
        print(f"    {domain:<15} : {', '.join(states)}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Parse and summarize a UPF file")
parser.add_argument("--upf", help="UPF file path")
args = parser.parse_args()

text = open(args.upf).read() if args.upf else SAMPLE_UPF
if not args.upf:
    print("No UPF file — using sample data.\n")

upf = parse_upf(text)
print_upf_summary(upf)
