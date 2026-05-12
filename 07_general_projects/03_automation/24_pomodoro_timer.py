"""
Project: Pomodoro Technique Timer
What it does: Implements the Pomodoro time management technique.
The Pomodoro Technique is a productivity method:
  1. Work focused for 25 minutes (one "Pomodoro")
  2. Take a 5-minute short break
  3. After 4 Pomodoros, take a 15-minute long break
  4. Repeat

Named after the tomato-shaped kitchen timer (pomodoro = Italian for tomato).

Run: python 24_pomodoro_timer.py  (starts a full Pomodoro session)
Run: python 24_pomodoro_timer.py --work 25 --short-break 5 --long-break 15
Run: python 24_pomodoro_timer.py --quick  (2-min demo mode)
"""

import time
import argparse
from datetime import datetime


def format_time(total_seconds):
    """Convert seconds into MM:SS format for the timer display."""
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes:02d}:{seconds:02d}"


def play_alert():
    """
    Play a terminal bell sound to alert the user when time is up.
    \a is the ASCII BEL character — makes a beep sound in most terminals.
    The sound only works if your terminal has audio enabled.
    """
    print("\a", end="", flush=True)  # beep


def run_timer(label, duration_seconds, color_code="\033[92m"):
    """
    Run a countdown timer that displays the remaining time.

    label:           name shown in the display (e.g., "WORK", "BREAK")
    duration_seconds: total time in seconds
    color_code:      ANSI color for the timer display
    """
    RESET = "\033[0m"
    BOLD  = "\033[1m"

    print(f"\n  {BOLD}{color_code}━━━ {label} ━━━{RESET}")
    start_time = datetime.now()
    end_time   = datetime.now().replace(
        second=datetime.now().second,  # will be overridden by the sleep
    )

    try:
        for remaining in range(duration_seconds, -1, -1):
            # Calculate percentage complete for the progress bar
            elapsed  = duration_seconds - remaining
            pct      = elapsed / duration_seconds if duration_seconds > 0 else 1
            bar_len  = int(30 * pct)     # progress bar is 30 chars wide
            bar      = "█" * bar_len + "░" * (30 - bar_len)

            # Display: TIME REMAINING [progress bar] PERCENTAGE
            time_str = format_time(remaining)
            print(f"\r  {color_code}{time_str}{RESET}  [{bar}]  {pct*100:.0f}%",
                  end="", flush=True)

            if remaining > 0:
                time.sleep(1)  # wait 1 second before updating again

    except KeyboardInterrupt:
        print(f"\n\n  Timer interrupted!")
        return False

    # Timer finished
    print(f"\n  {BOLD}{color_code}✓ {label} COMPLETE!{RESET}")
    play_alert()
    return True


def run_pomodoro_session(work_min, short_break_min, long_break_min,
                         pomodoros_per_set=4):
    """
    Run a full Pomodoro work session in a loop.

    The session alternates between:
      - work periods (25 min default)
      - short breaks (5 min after each work period)
      - long break (15 min after every 4 Pomodoros)
    """
    RED   = "\033[91m"
    GREEN = "\033[92m"
    BLUE  = "\033[94m"
    BOLD  = "\033[1m"
    RST   = "\033[0m"

    # Convert minutes to seconds for the timer
    work_sec        = work_min * 60
    short_break_sec = short_break_min * 60
    long_break_sec  = long_break_min * 60

    pomodoro_count = 0   # total Pomodoros completed this session
    session_start  = datetime.now()

    print(f"\n{'='*55}")
    print(f"  {BOLD}POMODORO TIMER{RST}")
    print(f"  Work: {work_min}min | Short Break: {short_break_min}min | "
          f"Long Break: {long_break_min}min")
    print(f"  Long break after every {pomodoros_per_set} Pomodoros")
    print(f"  Started: {session_start.strftime('%H:%M:%S')}")
    print(f"{'='*55}")
    print(f"\n  Press Ctrl+C to stop at any time.")

    while True:
        pomodoro_count += 1
        print(f"\n  ┌─ Pomodoro #{pomodoro_count} ─────────────────────────┐")

        # ── Work period ────────────────────────────────────────────────────
        print(f"  │  Task: Focus! No distractions.                  │")
        print(f"  └──────────────────────────────────────────────────┘")

        completed = run_timer(f"WORK #{pomodoro_count}", work_sec, color_code=RED)
        if not completed:
            break

        # ── Break time ─────────────────────────────────────────────────────
        # Every 4 Pomodoros = long break; otherwise short break
        if pomodoro_count % pomodoros_per_set == 0:
            print(f"\n  {BOLD}🎉 {pomodoros_per_set} Pomodoros done! Take a long break.{RST}")
            completed = run_timer("LONG BREAK", long_break_sec, color_code=BLUE)
        else:
            remaining_until_long = pomodoros_per_set - (pomodoro_count % pomodoros_per_set)
            print(f"\n  ({remaining_until_long} more Pomodoros until long break)")
            completed = run_timer("SHORT BREAK", short_break_sec, color_code=GREEN)

        if not completed:
            break

        # ── Prompt before next Pomodoro ────────────────────────────────────
        try:
            input(f"\n  Press Enter to start Pomodoro #{pomodoro_count + 1}... ")
        except (EOFError, KeyboardInterrupt):
            break

    # Session summary
    elapsed = datetime.now() - session_start
    total_focus_min = pomodoro_count * work_min
    print(f"\n{'='*55}")
    print(f"  SESSION SUMMARY")
    print(f"  Pomodoros completed : {pomodoro_count}")
    print(f"  Total focus time    : {total_focus_min} minutes")
    print(f"  Session duration    : {int(elapsed.total_seconds() // 60)} minutes")
    print(f"  Ended: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*55}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Pomodoro Technique timer")
parser.add_argument("--work",        type=int, default=25, help="Work duration (minutes)")
parser.add_argument("--short-break", type=int, default=5,  help="Short break (minutes)")
parser.add_argument("--long-break",  type=int, default=15, help="Long break (minutes)")
parser.add_argument("--quick",       action="store_true",
                    help="Quick demo mode (2-min work, 30-sec breaks)")
args = parser.parse_args()

if args.quick:
    # Demo mode: very short intervals so we can see it work quickly
    run_pomodoro_session(
        work_min=0,          # 0 minutes = will use 10 seconds
        short_break_min=0,
        long_break_min=0,
    )
    # Override to use seconds for demo
    print("Demo mode: using 10s work, 5s breaks")
    run_timer("WORK #1 (demo)",   10, "\033[91m")
    run_timer("SHORT BREAK (demo)", 5, "\033[92m")
    run_timer("WORK #2 (demo)",   10, "\033[91m")
    run_timer("SHORT BREAK (demo)", 5, "\033[92m")
else:
    run_pomodoro_session(
        work_min=args.work,
        short_break_min=vars(args)["short_break"],
        long_break_min=vars(args)["long_break"],
    )
