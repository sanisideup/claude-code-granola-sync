# Claude Code Granola Sync

## Quick Start

```bash
# Sync Granola meeting notes (last 7 days)
/sync-granola

# Sync specific time ranges
/sync-granola 30          # Last 30 days
/sync-granola all         # All meetings

# Sync specific folders
/sync-granola folder:Innovation
```

## Automatic Sync

**Your meetings sync automatically!** This repository includes a session start hook that automatically syncs Granola meetings every time you start Claude Code.

- **Triggers on**: Every new Claude Code session startup
- **Smart sync**: Automatically syncs all days since your last sync
- **Detailed summary**: Creates a sync report with meeting titles, date range, and transcript status

The sync is smart about incremental updates:
- First time: Syncs all meetings in your Granola cache
- Subsequent sessions: Only syncs meetings since last session
- Example: If you last synced 3 days ago, it automatically syncs the last 3 days

### Example Auto-Sync Output

When you start a new Claude Code session, you'll see a message like this:

```
SessionStart hook additional context: Granola auto-sync complete: 9 meeting(s) synced
Date range: 2025-12-31 to 2026-01-05
with transcripts
  • Product Review Meeting
  • Engineering Standup
  • Customer Discovery Call
  • Weekly Planning Session
  • Design Review
  • ...and 4 more
```

This tells you exactly what was synced automatically in the background, so you can immediately start working with fresh meeting data.

### Check Last Sync

View a detailed summary of the last auto-sync:

```bash
cat main/sources/granola/.last-auto-sync
```

This shows:
- Number of meetings synced
- Date range (e.g., "2026-01-04 to 2026-01-05")
- Up to 5 meeting titles
- Whether transcripts were included

The hook configuration is in `.claude/settings.json` and the auto-sync script is at `scripts/auto-sync-granola.sh`.

## Architecture

This repository uses a **local sync architecture** with automatic and manual sync capabilities:

### Components

1. **Data Sources**: Documents synced to `main/sources/[source-name]/` for offline access and version control
2. **Python Sync Scripts**: Located in `scripts/sync-*.py`, handle data extraction and transformation
3. **Auto-Sync Scripts**: Located in `scripts/auto-sync-*.sh`, triggered automatically on session start
4. **Slash Commands**: Located in `.claude/commands/`, provide user-friendly manual sync interfaces

### Directory Structure

```
vibe-product-mgmt/
├── main/
│   └── sources/           # All synced data sources
│       ├── SOURCES.md     # Index of all data sources
│       └── granola/       # Meeting notes and transcripts
│           ├── README.md
│           ├── .sync-config.json
│           ├── .last-sync          # Timestamp of last sync
│           └── .last-auto-sync     # Auto-sync summary notification
├── scripts/
│   ├── sync-granola.py            # Manual sync script
│   └── auto-sync-granola.sh       # Auto-sync hook script
└── .claude/
    ├── settings.json              # Hook configuration
    └── commands/
        └── sync-granola.md        # Slash command for manual sync
```

### Sync Flow

1. **Automatic**: SessionStart hook → `auto-sync-granola.sh` → syncs since last session
2. **Manual**: `/sync-granola` command → `sync-granola.py` → syncs specified range

## Data Sources

- **Granola**: Meeting notes, transcripts, and AI summaries
- More sources coming soon...

See `main/sources/SOURCES.md` for detailed information about each data source.

## Development

For detailed technical documentation and guidance for AI assistants working with this codebase, see `CLAUDE.md`.

## License

MIT License - see `LICENSE` file for details.
