# Zoom Recordings Organizer

This Python script helps organize Zoom recordings into session folders based on a predefined schedule. It supports Arabic and English schedules and automatically renames multiple recordings per session as Part 1, Part 2, etc.

## Features

- Automatically matches Zoom recording times with scheduled session times.
- Supports both Arabic and English schedules.
- Moves and renames recordings into structured folders.
- Supports dry-run mode to test organization logic before moving files.

## How It Works

1. You provide a session schedule in English or Arabic.
2. The script scans the download folder for Zoom recordings.
3. It compares the recording timestamps with scheduled sessions.
4. Matched recordings are moved into folders named after the session.
5. If there are multiple recordings for the same session, they are renamed as:
   - `Session Name - Part 1`
   - `Session Name - Part 2`
   - etc.

## Usage

```bash
python3 organize_zoom_recordings.py
```

For a test run without moving files:

```bash
python3 organize_zoom_recordings.py --dry-run
```

## Requirements

- Python 3.8+
- Your Zoom recordings must have standard timestamps in the filename.
- Your schedule must be accurately defined inside the script.

## License

MIT License

<p align="center"><b>💡 Crafted with care by <a href="https://github.com/ebram-gerges">Ebram Gerges</a> — Main Contributor 🚀</b></p>

