# Granola Meeting Sync (Local Cache)

This directory contains synced Granola meetings from the local app cache.

## Known Limitation (cache v4, starting Feb 2026)

Granola moved AI summaries and historical transcripts to server-side storage in late Jan 2026.
Meetings synced from Feb 2026 onward are metadata-only.

| Data | Available locally? |
|------|-------------------|
| Meeting metadata | Yes |
| Manual notes | Yes (but rare) |
| Folder mapping | Yes |
| AI summaries | No (moved to Granola servers) |
| Historical transcripts | No (only live recording remains in cache) |

Meetings synced starting Feb 2026 onward will be metadata-only. Pre-migration files with AI summaries and transcripts are preserved on disk.

Workaround: Use the [official Granola MCP](https://docs.granola.ai/help-center/sharing/integrations/mcp) for full meeting content (summaries + transcripts) on demand.

The local sync remains useful for meeting discovery by date, folder, title, and participants.

## Quick Start

Use the `/sync-granola` slash command in Claude Code to sync your meetings:

```bash
/sync-granola              # Sync last 7 days (default)
/sync-granola 30           # Sync last 30 days
/sync-granola all          # Sync all meetings in local cache
/sync-granola folder:Innovation  # Sync specific folder only
```

## Automatic Sync

**Good news!** Your Granola meetings sync automatically on every Claude Code session start.

When you launch Claude Code, a session start hook automatically:
1. Reads the `.last-sync` timestamp
2. Calculates how many days have passed since your last sync
3. Runs `sync-granola.py` with the appropriate `--days` parameter
4. Updates the `.last-sync` timestamp for the next session

This keeps your local meeting index current for search and discovery.

## Direct Script Usage

You can also run the sync script directly:

```bash
# Basic usage
python3 scripts/sync-granola.py --days 7

# Sync specific folder
python3 scripts/sync-granola.py --days 30 --folder Innovation

# Sync everything in local cache
python3 scripts/sync-granola.py --days 0

# Custom cache path
python3 scripts/sync-granola.py --cache-path "/custom/path/to/cache-v3.json"
```

## Folder Structure

```
granola/
├── meetings/           # Meeting files (metadata + local notes when present)
│   └── YYYY-MM-DD_Meeting-Title_<id>.md
├── transcripts/        # Legacy transcript files (pre-migration cache data)
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
- **duration**: Meeting duration (when transcript timing is available)
- **participants**: List of attendees
- **tags**: Granola tags
- **granola_url**: Deep link back to original note

## Configuration

Edit `.sync-config.json` to customize:

- Default sync window (days)
- Default folders to sync
- Filename preferences

## Cache Location

The sync reads from Granola's local cache:
- **macOS**: `~/Library/Application Support/Granola/cache-v3.json`
- **Windows**: `%APPDATA%\Granola\cache-v3.json`

No API calls are made - everything runs locally and offline.

## Need full summaries/transcripts?

Use Granola MCP for server-side content retrieval:
- Setup: https://docs.granola.ai/help-center/sharing/integrations/mcp

## Troubleshooting

**No meetings found:**
- Check that Granola is installed and has been opened at least once
- Verify cache file exists at the location above
- Try syncing `all` to see if date filters are too restrictive

**Missing AI summary or transcript on recent meetings:**
- Expected for post-Feb 2026 meetings in cache v4
- Use Granola MCP for full content

**Sync errors:**
- Check that you have read permissions on the Granola cache file
- Ensure Python 3.7+ is installed
- Check `.last-sync` file for last successful sync timestamp
