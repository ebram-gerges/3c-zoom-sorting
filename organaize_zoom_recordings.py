#!/usr/bin/env python3

import os
import shutil
import argparse
from datetime import datetime
from pathlib import Path
import re

# you can edit this schedule for your schedule
# make sure you update it but do not ruin the format :)
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
""" 
    the variables under this comment are
    zoom folder == the folder zoom stores the recorded sessions
    dest folder == the folder that we will save the organaized sessions in
    time tolerance minutes == this is the gap between the actual zoom time and
    the recorded session saving time
    example: if the session ended at 5pm and the record is saved at 7pm it will
    still be considerd as this session recording
    this prevents the issue that happens because of the delay between session
    end and the saving progress to end
    """
ZOOM_FOLDER = Path.home() / "Documents" / "Zoom"
DEST_ROOT = Path.home() / "Documents" / "ZoomRecordings"
TIME_TOLERANCE_MINUTES = 120

def parse_folder_datetime(folder):
    # Example folder: "2025-07-22 14.48.00 your name' Zoom Meeting"
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
        sched_datetime = dt.replace(
            hour=sched_time_obj.hour, minute=sched_time_obj.minute, second=0
        )
        diff_minutes = abs((sched_datetime - dt).total_seconds()) / 60
        if diff_minutes <= TIME_TOLERANCE_MINUTES:
            return name
    return None



def organize(dry_run=False):
    if not ZOOM_FOLDER.exists():
        print(f"[!] Zoom folder not found: {ZOOM_FOLDER}")
        return

    session_folders = []

    for folder in ZOOM_FOLDER.iterdir():
        if not folder.is_dir():
            continue
        if "Personal Meeting Room" in folder.name:
            continue
        dt = parse_folder_datetime(folder.name)
        if not dt:
            print(f"[!] Skipping unrecognized: {folder.name}")
            continue
        session = match_session(dt)
        if not session:
            print(f"[!] No session match: {folder.name}")
            continue
        session_folders.append((dt, session, folder))

    # Sort folders chronologically
    session_folders.sort(key=lambda x: x[0])  # sort by datetime

    # Group by session name and date
    grouped = {}
    for dt, session, folder in session_folders:
        key = (session, dt.strftime("%Y-%m-%d"))
        grouped.setdefault(key, []).append((dt, folder))

    for (session, date_str), items in grouped.items():
        date_folder = DEST_ROOT / session / date_str
        for i, (dt, folder) in enumerate(items, start=1):
            dest = date_folder / f"Part {i}"
            if dry_run:
                print(f"[DRY] {folder.name} → {dest}")
            else:
                dest.mkdir(parents=True, exist_ok=True)
                shutil.move(str(folder), str(dest))
                print(f"[OK] {folder.name} → {dest}")

#you can run it with --dry-run to see the changes before doing them
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview moves")
    args = parser.parse_args()
    organize(dry_run=args.dry_run)
