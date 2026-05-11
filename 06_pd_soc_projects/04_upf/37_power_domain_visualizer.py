"""
Project: Power Domain Hierarchy Visualizer
Tool context: Synopsys PA Compiler / UPF
What it does: Reads UPF power domain info and generates an ASCII tree
of the power domain hierarchy, showing supply sets, voltage levels,
and which modules belong to each domain.

Usage:
    python 37_power_domain_visualizer.py --upf design.upf
    python 37_power_domain_visualizer.py  (uses built-in sample)
"""

import re
import argparse

SAMPLE_UPF = """\
create_power_domain PD_TOP     -include_scope
create_power_domain PD_CPU     -elements {cpu_core alu_unit l1_cache} -supply {primary SS_CPU}
create_power_domain PD_DMA     -elements {dma_ctrl axi_interconnect} -supply {primary SS_DMA}
create_power_domain PD_PERIPH  -elements {apb_bridge uart_ctrl spi_ctrl gpio_ctrl} -supply {primary SS_PERIPH}
create_power_domain PD_PLL     -elements {pll_ctrl clk_ctrl} -atomic

create_supply_set SS_TOP    -function {power VDD}   -function {ground VSS}
create_supply_set SS_CPU    -function {power VDD}   -function {ground VSS}
create_supply_set SS_DMA    -function {power VDD}   -function {ground VSS}
create_supply_set SS_PERIPH -function {power VDD_L} -function {ground VSS}
create_supply_set SS_PLL    -function {power VDD}   -function {ground VSS}

add_power_state PD_CPU -state {ON}
add_power_state PD_CPU -state {OFF}
add_power_state PD_CPU -state {RET}
add_power_state PD_DMA -state {ON}
add_power_state PD_DMA -state {OFF}
"""

VOLTAGE_MAP = {"VDD": "1.0V", "VDD_L": "0.8V", "VSS": "0V"}


def parse_domains(text):
    domains = {}
    supply_sets = {}

    for m in re.finditer(
        r"create_power_domain\s+(\S+)(.*?)(?=\ncreate|\Z)", text, re.DOTALL
    ):
        name   = m.group(1)
        rest   = m.group(2)
        elems  = re.search(r"-elements\s+\{([^}]+)\}", rest)
        atomic = "-atomic" in rest
        domains[name] = {
            "elements": elems.group(1).strip().split() if elems else [],
            "atomic":   atomic,
            "states":   [],
        }

    for m in re.finditer(r"add_power_state\s+(\S+)\s+-state\s+\{(\S+)", text):
        domain = m.group(1)
        state  = m.group(2)
        if domain in domains:
            domains[domain]["states"].append(state)

    for m in re.finditer(r"create_supply_set\s+(\S+)(.*?)(?=\ncreate|\Z)", text, re.DOTALL):
        name  = m.group(1)
        fns   = re.findall(r"-function\s+\{(\S+)\s+(\S+)\}", m.group(2))
        pwr   = next((f[1] for f in fns if f[0] == "power"), "?")
        gnd   = next((f[1] for f in fns if f[0] == "ground"), "?")
        supply_sets[name] = {
            "power":  pwr,
            "ground": gnd,
            "voltage":VOLTAGE_MAP.get(pwr, "?"),
        }

    return domains, supply_sets


def print_tree(domains, supply_sets):
    CYN  = "\033[36m"
    GRN  = "\033[92m"
    YEL  = "\033[33m"
    RST  = "\033[0m"
    BOLD = "\033[1m"

    print("=" * 65)
    print("  POWER DOMAIN HIERARCHY")
    print("=" * 65)

    print(f"\n  {BOLD}{CYN}soc_top{RST}")

    items = list(domains.items())
    for idx, (name, info) in enumerate(items):
        is_last  = idx == len(items) - 1
        branch   = "└──" if is_last else "├──"
        subbranch= "    " if is_last else "│   "

        # Find matching supply set
        ss_name = name.replace("PD_", "SS_")
        ss      = supply_sets.get(ss_name, {})
        voltage  = ss.get("voltage", "?V")
        power_net= ss.get("power", "?")

        atomic_tag = f" {YEL}[ATOMIC]{RST}" if info["atomic"] else ""
        states_str = f"  States: {', '.join(info['states'])}" if info["states"] else ""
        pwr_str    = f"  Supply: {power_net}({voltage})" if power_net != "?" else ""

        print(f"\n  {branch} {CYN}{BOLD}{name}{RST}{atomic_tag}")
        print(f"  {subbranch} ├─ {pwr_str}  {states_str}")

        elements = info["elements"]
        if elements:
            print(f"  {subbranch} └─ Modules ({len(elements)}):")
            for ei, elem in enumerate(elements):
                el_branch = "    └──" if ei == len(elements)-1 else "    ├──"
                print(f"  {subbranch}    {el_branch} {elem}")
        else:
            print(f"  {subbranch} └─ Modules: [all (include_scope)]")

    # Stats
    total_elems = sum(len(d["elements"]) for d in domains.values())
    switchable  = sum(1 for d in domains.values() if d["states"])
    ao          = len(domains) - switchable

    print(f"\n  {'─'*50}")
    print(f"  Power Domains  : {len(domains)}")
    print(f"  Switchable PDs : {switchable} (have ON/OFF states)")
    print(f"  Always-on PDs  : {ao}")
    print(f"  Total modules  : {total_elems}")

    # Voltage summary
    voltages = set(ss.get("voltage", "?") for ss in supply_sets.values())
    print(f"  Voltage rails  : {', '.join(sorted(voltages))}")
    if len(voltages) > 1:
        print(f"  {YEL}Multi-voltage design — level shifters required at domain boundaries.{RST}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Visualize UPF power domain hierarchy")
parser.add_argument("--upf", help="UPF file path")
args = parser.parse_args()

text = open(args.upf).read() if args.upf else SAMPLE_UPF
if not args.upf:
    print("No UPF file — using sample data.\n")

domains, supply_sets = parse_domains(text)
print_tree(domains, supply_sets)
