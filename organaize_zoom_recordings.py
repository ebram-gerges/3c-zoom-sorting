#!/usr/bin/env python3

import os
import shutil
import argparse
from datetime import datetime
from pathlib import Path
import re
import sys

# === 🗓️ Session Schedule ===
SESSION_SCHEDULE = {
    "Monday": [
        ("11:00am", "Scratch Senior 2s"),
        ("5:00pm",  "HTML CSS Senior 1s"),
    ],
    "Tuesday": [
        ("2:00pm",  "Python Senior 2s"),
        ("6:00pm",  "Scratch Senior 2s"),
    ],
    "Wednesday": [
        ("3:00pm",  "Scratch Senior 4s"),
    ],
}

# === 📁 Configuration ===
ZOOM_FOLDER = Path.home() / "Documents" / "Zoom"
DEST_ROOT = Path.home() / "Documents" / "ZoomRecordings"
TIME_TOLERANCE_MINUTES = 120

# === 🎨 Colors ===
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

def sanitize_filename(name):
    """Remove illegal characters for Windows compatibility."""
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def print_fancy_usage():
    print(f"""
{BOLD}{CYAN}📦 Zoom Session Organizer{RESET}

{YELLOW}Usage:{RESET}
    python3 organize_zoom.py [--dry-run | --cp-only | --mv]

{YELLOW}Options:{RESET}
    {GREEN}--dry-run{RESET}   🧐 Preview the planned moves without modifying any files.
    {GREEN}--cp-only{RESET}   📋 Copy recordings to organized folders instead of moving.
    {GREEN}--mv{RESET}        ✂️ Move recordings to the organized folder structure (destructive).

{YELLOW}Example:{RESET}
    {CYAN}$ python3 organize_zoom.py --dry-run{RESET}
    """)

def parse_folder_datetime(folder):
    m = re.match(r"(\d{4}-\d{2}-\d{2}) (\d{2})\.(\d{2})\.(\d{2})", folder)
    if not m:
        return None
    date_str, h, mi, s = m.groups()
    try:
        return datetime.strptime(f"{date_str} {h}:{mi}:{s}", "%Y-%m-%d %H:%M:%S")
    except:
        return None

def match_session(dt):
    day = dt.strftime("%A")
    if day not in SESSION_SCHEDULE:
        return None
    for sched_time, name in SESSION_SCHEDULE[day]:
        sched_time_obj = datetime.strptime(sched_time, "%I:%M%p").time()
        sched_datetime = dt.replace(hour=sched_time_obj.hour, minute=sched_time_obj.minute, second=0)
        diff_minutes = abs((sched_datetime - dt).total_seconds()) / 60
        if diff_minutes <= TIME_TOLERANCE_MINUTES:
            return name
    return None

def organize(mode):
    header_icon = {
        "dry-run": "🔍",
        "cp-only": "📋",
        "mv": "✂️"
    }.get(mode, "🌀")

    print(f"{BOLD}{MAGENTA}{header_icon} Starting Zoom Recording Organizer in '{mode}' mode...{RESET}\n")

    if not ZOOM_FOLDER.exists():
        print(f"{RED}[✘] Zoom folder not found:{RESET} {ZOOM_FOLDER}")
        return

    session_folders = []

    for folder in ZOOM_FOLDER.iterdir():
        if not folder.is_dir():
            continue
        if "Personal Meeting Room" in folder.name:
            continue
        dt = parse_folder_datetime(folder.name)
        if not dt:
            print(f"{YELLOW}[⚠️] Skipping unrecognized folder:{RESET} {folder.name}")
            continue
        session = match_session(dt)
        if not session:
            print(f"{YELLOW}[⚠️] No session match for:{RESET} {folder.name}")
            continue
        session_folders.append((dt, session, folder))

    if not session_folders:
        print(f"{RED}[!] No valid Zoom recordings found to organize.{RESET}")
        return

    session_folders.sort(key=lambda x: x[0])

    grouped = {}
    for dt, session, folder in session_folders:
        key = (session, dt.strftime("%Y-%m-%d"))
        grouped.setdefault(key, []).append((dt, folder))

    for (session, date_str), items in grouped.items():
        safe_session = sanitize_filename(session)
        safe_date = sanitize_filename(date_str)
        date_folder = DEST_ROOT / safe_session / safe_date

        for i, (dt, folder) in enumerate(items, start=1):
            dest = date_folder / f"Part {i}"
            action_str = f"{CYAN}{folder.name}{RESET} → {GREEN}{dest}{RESET}"

            if mode == "dry-run":
                print(f"🧭 [DRY-RUN] Would move {action_str}")
                continue

            try:
                dest.mkdir(parents=True, exist_ok=True)

                if mode == "cp-only":
                    shutil.copytree(folder, dest, dirs_exist_ok=True)
                    print(f"📁 [COPIED]  {action_str}")
                elif mode == "mv":
                    shutil.move(str(folder), str(dest))
                    print(f"🚚 [MOVED]   {action_str}")

            except Exception as e:
                print(f"{RED}[ERROR] Failed to process {folder.name}: {e}{RESET}")

    print(f"\n{BOLD}{GREEN}✅ Finished organizing Zoom recordings in '{mode}' mode.{RESET}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="🧹 Organize Zoom recordings into named sessions based on your weekly schedule.",
        add_help=False
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dry-run", action="store_true", help="Preview planned moves without touching files")
    group.add_argument("--cp-only", action="store_true", help="Copy instead of move (safe mode)")
    group.add_argument("--mv", action="store_true", help="Move files (destructive)")

    parser.add_argument("-h", "--help", action="store_true", help="Show this help message and exit")

    args = parser.parse_args()

    if args.help:
        parser.print_help()
        print_fancy_usage()
        sys.exit(0)

    if not any([args.dry_run, args.cp_only, args.mv]):
        print_fancy_usage()
        sys.exit(1)

    if args.dry_run:
        organize("dry-run")
    elif args.cp_only:
        organize("cp-only")
    elif args.mv:
        organize("mv")
