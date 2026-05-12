"""
Project: Meeting Agenda Generator
What it does: Creates a formatted meeting agenda document from structured input.
Calculates time allocations, generates HTML output, and exports to text.
Useful for PMs, team leads, and anyone who runs regular meetings.

Run: python 28_meeting_agenda.py  (uses built-in sample agenda)
Run: python 28_meeting_agenda.py --output agenda.html
"""

import argparse
import os
from datetime import datetime, timedelta


# Sample meeting agenda data
SAMPLE_AGENDA = {
    "title":      "Q1 2024 Design Review Meeting",
    "date":       "2024-01-15",
    "time":       "14:00",
    "duration":   60,         # total meeting duration in minutes
    "location":   "Conference Room A / Zoom",
    "facilitator":"Alice Johnson",
    "attendees":  ["Alice Johnson", "Bob Smith", "Charlie Brown", "Diana Prince"],
    "items": [
        {"title": "Welcome and Introductions",        "duration": 5,  "owner": "Alice",   "type": "info"},
        {"title": "Q4 2023 Review — Key Achievements","duration": 15, "owner": "Bob",     "type": "discussion"},
        {"title": "Current Design Status Update",     "duration": 15, "owner": "Charlie", "type": "update"},
        {"title": "Blockers and Risk Review",         "duration": 10, "owner": "Diana",   "type": "action"},
        {"title": "Q1 Goals and Priorities",          "duration": 10, "owner": "Alice",   "type": "decision"},
        {"title": "Action Items and Next Steps",      "duration": 5,  "owner": "All",     "type": "action"},
    ]
}

# Colors for different agenda item types
TYPE_COLORS = {
    "info":       "#3498db",   # blue
    "discussion": "#e67e22",   # orange
    "update":     "#27ae60",   # green
    "action":     "#e74c3c",   # red
    "decision":   "#9b59b6",   # purple
}


def calculate_timeline(items, start_time_str):
    """
    Calculate the start and end time for each agenda item.
    Each item starts when the previous one ends.
    """
    # Parse the start time string "14:00" into a datetime object
    # We use today's date but only care about the time portion
    start_dt = datetime.strptime(start_time_str, "%H:%M")

    current_time = start_dt
    timeline     = []

    for item in items:
        end_time = current_time + timedelta(minutes=item["duration"])

        timeline.append({
            **item,  # copy all existing item fields (** unpacks the dict)
            "start": current_time.strftime("%H:%M"),
            "end":   end_time.strftime("%H:%M"),
        })

        current_time = end_time  # next item starts where this one ends

    return timeline, current_time.strftime("%H:%M")


def format_text_agenda(agenda):
    """Generate a plain-text formatted agenda."""
    timeline, end_time = calculate_timeline(agenda["items"], agenda["time"])

    lines = []
    lines.append("=" * 60)
    lines.append(f"  {agenda['title'].upper()}")
    lines.append("=" * 60)
    lines.append(f"  Date       : {agenda['date']}")
    lines.append(f"  Time       : {agenda['time']} – {end_time} "
                 f"({agenda['duration']} minutes)")
    lines.append(f"  Location   : {agenda['location']}")
    lines.append(f"  Facilitator: {agenda['facilitator']}")
    lines.append(f"  Attendees  : {', '.join(agenda['attendees'])}")
    lines.append("")
    lines.append("  AGENDA:")
    lines.append("  " + "─" * 56)
    lines.append(f"  {'TIME':<12} {'DURATION':>9}  {'OWNER':<12}  TOPIC")
    lines.append("  " + "─" * 56)

    for item in timeline:
        time_range = f"{item['start']}–{item['end']}"
        duration   = f"{item['duration']} min"
        print_line = (f"  {time_range:<12} {duration:>9}  "
                      f"{item['owner']:<12}  {item['title']}")
        lines.append(print_line)

    lines.append("  " + "─" * 56)

    # Check if total allocated time matches meeting duration
    total_allocated = sum(item["duration"] for item in agenda["items"])
    lines.append(f"\n  Total allocated: {total_allocated} min / {agenda['duration']} min available")

    if total_allocated > agenda["duration"]:
        lines.append(f"  ⚠️  Over by {total_allocated - agenda['duration']} minutes!")
    elif total_allocated < agenda["duration"]:
        lines.append(f"  ✓  {agenda['duration'] - total_allocated} min buffer available")
    else:
        lines.append(f"  ✓  Agenda perfectly fills the time slot")

    lines.append("")
    lines.append("  NOTES:")
    lines.append("  ───────────────────────────────────────────────────────")
    lines.append("")
    lines.append("")

    return "\n".join(lines)


def format_html_agenda(agenda):
    """Generate an HTML formatted agenda."""
    timeline, end_time = calculate_timeline(agenda["items"], agenda["time"])

    rows = ""
    for item in timeline:
        color = TYPE_COLORS.get(item["type"], "#999")
        rows += f"""
        <tr>
            <td>{item['start']}–{item['end']}</td>
            <td>{item['duration']} min</td>
            <td>{item['owner']}</td>
            <td>
                <span style="color:{color};font-weight:bold">●</span>
                {item['title']}
                <span style="background:{color}22;color:{color};font-size:11px;
                             padding:2px 6px;border-radius:8px;margin-left:8px">
                    {item['type']}
                </span>
            </td>
        </tr>"""

    attendees_html = "".join(f"<li>{a}</li>" for a in agenda["attendees"])

    return f"""<!DOCTYPE html>
<html><head><title>{agenda['title']}</title>
<style>
body{{font-family:Arial;max-width:750px;margin:30px auto;color:#333}}
.header{{background:#2c3e50;color:#fff;padding:25px;border-radius:8px 8px 0 0}}
.header h1{{margin:0;font-size:20px}} .header p{{margin:5px 0;opacity:.8}}
.body{{background:#fff;padding:25px;border:1px solid #eee;border-radius:0 0 8px 8px}}
table{{width:100%;border-collapse:collapse}}
th{{background:#34495e;color:#fff;padding:10px;text-align:left}}
td{{padding:10px;border-bottom:1px solid #f0f0f0}}
tr:hover{{background:#f9f9f9}}
.notes{{background:#fffef0;border:1px solid #f1c40f;padding:15px;
        margin-top:20px;border-radius:5px}}
</style></head>
<body>
<div class="header">
  <h1>{agenda['title']}</h1>
  <p>📅 {agenda['date']}  ⏰ {agenda['time']}–{end_time}  📍 {agenda['location']}</p>
  <p>👤 Facilitator: {agenda['facilitator']}</p>
</div>
<div class="body">
  <h3>Attendees</h3>
  <ul>{attendees_html}</ul>
  <h3>Agenda</h3>
  <table>
    <tr><th>Time</th><th>Duration</th><th>Owner</th><th>Topic</th></tr>
    {rows}
  </table>
  <div class="notes">
    <strong>📝 Notes:</strong><br><br><br>
  </div>
</div></body></html>"""


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Generate a meeting agenda document")
parser.add_argument("--output", help="Output file (.txt or .html)")
args = parser.parse_args()

print("=== Meeting Agenda Generator ===\n")

agenda = SAMPLE_AGENDA

# Always show text version in terminal
text_agenda = format_text_agenda(agenda)
print(text_agenda)

# Save to file if requested
if args.output:
    if args.output.endswith(".html"):
        with open(args.output, "w") as f:
            f.write(format_html_agenda(agenda))
        print(f"HTML agenda saved: {args.output}")
    else:
        with open(args.output, "w") as f:
            f.write(text_agenda)
        print(f"Text agenda saved: {args.output}")
