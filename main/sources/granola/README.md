# Granola Meeting Notes Sync

This directory contains synced Granola meeting notes and transcripts with full metadata preservation.

## Quick Start

Use the `/sync-granola` slash command in Claude Code to sync your meetings:

```bash
/sync-granola              # Sync last 7 days (default)
/sync-granola 30           # Sync last 30 days
/sync-granola all          # Sync all meetings
/sync-granola folder:Innovation  # Sync specific folder only
/sync-granola 14 --no-transcripts  # Sync last 14 days, skip transcripts
```

## Direct Script Usage

You can also run the sync script directly:

```bash
# Basic usage
python3 scripts/sync-granola.py --days 7

# Sync specific folder
python3 scripts/sync-granola.py --days 30 --folder Innovation

# Sync everything
python3 scripts/sync-granola.py --days 0

# Skip transcripts
python3 scripts/sync-granola.py --days 7 --no-transcripts

# Custom cache path
python3 scripts/sync-granola.py --cache-path "/custom/path/to/cache-v3.json"
```

## Folder Structure

```
granola/
├── meetings/           # Meeting notes with AI summaries
│   └── YYYY-MM-DD_Meeting-Title_<id>.md
├── transcripts/        # Full transcripts (separate files)
│   └── YYYY-MM-DD_Meeting-Title_<id>_transcript.md
├── .sync-config.json   # Sync configuration
├── .last-sync          # Last sync timestamp
└── README.md           # This file
```

## Metadata Preserved

Each meeting markdown file includes YAML frontmatter with:

- **granola_id**: Unique meeting identifier
- **title**: Meeting title
- **created_at**: Meeting start timestamp
- **updated_at**: Last edit timestamp
- **folder**: Project folder (Innovation, AI, Product, etc.)
- **duration**: Meeting duration (calculated from transcript)
- **participants**: List of attendees
- **tags**: Granola tags
- **granola_url**: Deep link back to original note

## Example Meeting File

```markdown
---
granola_id: c305754c-c755-4db4-9411-c171bd491d60
title: "Eng Standup"
created_at: 2025-10-27T15:30:00.000Z
updated_at: 2025-10-27T16:00:00.000Z
folder: Innovation
duration: 28m
granola_url: granola://meeting/c305754c-c755-4db4-9411-c171bd491d60
participants:
  - John Smith
  - Jane Doe
tags:
  - standup
  - engineering
---

# ⚡️Eng Standup

## AI Summary

Team discussed progress on Q4 initiatives...

## Notes

[Your manual notes here...]
```

## Configuration

Edit `.sync-config.json` to customize:

- Default sync window (days)
- Default folders to sync
- Include/exclude transcripts by default
- Filename preferences

## Cache Location

The sync reads from Granola's local cache:
- **macOS**: `~/Library/Application Support/Granola/cache-v3.json`
- **Windows**: `%APPDATA%\Granola\cache-v3.json`

No API calls are made - everything runs locally and offline.

## Troubleshooting

**No meetings found:**
- Check that Granola is installed and has been opened at least once
- Verify cache file exists at the location above
- Try syncing "all" to see if date filters are too restrictive

**Missing participants or metadata:**
- Some older meetings may not have all metadata fields
- Granola's cache structure may vary by version

**Sync errors:**
- Check that you have read permissions on the Granola cache file
- Ensure Python 3.7+ is installed
- Check `.last-sync` file for last successful sync timestamp

## Next Steps

After syncing, you can:
- Reference meeting notes directly in Claude Code
- Search across all meetings using Grep tool
- Create summaries or reports from meeting data
