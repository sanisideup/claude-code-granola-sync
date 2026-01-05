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
- **Zero friction**: Runs silently in the background - your meetings are always up to date

The sync is smart about incremental updates:
- First time: Syncs all meetings in your Granola cache
- Subsequent sessions: Only syncs meetings since last session
- Example: If you last synced 3 days ago, it automatically syncs the last 3 days

The hook configuration is in `.claude/settings.json` and the auto-sync script is at `scripts/auto-sync-granola.sh`.

## Architecture

This repository uses a **local sync architecture**:

1. **Data Sources**: Documents synced to `main/sources/[source-name]/` for offline access
2. **Python Sync Scripts**: Located in `scripts/`, handle data extraction and transformation
3. **Slash Commands**: Located in `.claude/commands/`, provide user-friendly interfaces

```
claude-code-granola-sync/
├── main/
│   └── sources/           # All synced data sources
│       ├── SOURCES.md     # Index of all data sources
│       └── granola/       # Meeting notes and transcripts
├── scripts/               # Python sync scripts
│   └── sync-granola.py    # Granola meetings sync
└── .claude/
    └── commands/          # Slash commands for sync operations
```

## Data Sources

- **Granola**: Meeting notes, transcripts, and AI summaries
- More sources coming soon...

See `main/sources/SOURCES.md` for detailed information about each data source.

## Development

For detailed technical documentation and guidance for AI assistants working with this codebase, see `CLAUDE.md`.

## License

MIT License - see `LICENSE` file for details.
