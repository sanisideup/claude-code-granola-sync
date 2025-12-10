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
