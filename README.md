# Claude Code Granola Sync

## Quick Start

```bash
# Sync Granola meetings from local cache (last 7 days)
/sync-granola

# Sync specific time ranges
/sync-granola 30          # Last 30 days
/sync-granola all         # All meetings in local cache

# Sync specific folders
/sync-granola folder:Innovation
```

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

## Granola MCP Requirements & Limitations

The Granola MCP is a separate tool that fetches meeting content directly from Granola's servers. See the [setup guide](https://docs.granola.ai/help-center/sharing/integrations/mcp).

Plan requirements:
- Granola free plan: Meeting notes only, last 30 days -- transcripts not available
- Granola paid plan: Full history + transcript access (`get_meeting_transcript` tool is paid-only)
- Claude/ChatGPT: Requires a paid account -- MCP connectors are not available on free tiers

When to use which:

| Use case | Use local sync | Use Granola MCP |
|----------|---------------|-----------------|
| Search meetings by date/title/person | Yes | No |
| Get full AI summary for a specific meeting | No (post-Feb 2026) | Yes |
| Read full transcript | No (post-Feb 2026) | Yes (paid plan only) |
| Offline / no internet | Yes | No |

## Automatic Sync

**Your meetings sync automatically!** This repository includes a session start hook that automatically syncs Granola meeting metadata every time you start Claude Code.

- **Triggers on**: Every new Claude Code session startup
- **Smart sync**: Automatically syncs all days since your last sync
- **Detailed summary**: Creates a sync report with meeting titles and date range

The sync is smart about incremental updates:
- First time: Syncs all meetings in your Granola cache
- Subsequent sessions: Only syncs meetings since last session
- Example: If you last synced 3 days ago, it automatically syncs the last 3 days

### Example Auto-Sync Output

When you start a new Claude Code session, you'll see a message like this:

```
SessionStart hook additional context: Granola auto-sync complete: 9 meeting(s) synced
Date range: 2025-12-31 to 2026-01-05
  • Product Review Meeting
  • Engineering Standup
  • Customer Discovery Call
  • Weekly Planning Session
  • Design Review
  • ...and 4 more
```

This tells you exactly what was synced automatically in the background.

### Check Last Sync

View a detailed summary of the last auto-sync:

```bash
cat main/sources/granola/.last-auto-sync
```

This shows:
- Number of meetings synced
- Date range (e.g., "2026-01-04 to 2026-01-05")
- Up to 5 meeting titles

The hook configuration is in `.claude/settings.json` and the auto-sync script is at `scripts/auto-sync-granola.sh`.

## Architecture

This repository uses a **local sync architecture** with automatic and manual sync capabilities:

### Components

1. **Data Sources**: Documents synced to `main/sources/[source-name]/` for offline access and version control
2. **Python Sync Scripts**: Located in `scripts/sync-*.py`, handle local cache extraction and transformation
3. **Auto-Sync Scripts**: Located in `scripts/auto-sync-*.sh`, triggered automatically on session start
4. **Slash Commands**: Located in `.claude/commands/`, provide user-friendly manual sync interfaces
5. **Granola MCP (external)**: Use for server-side summaries/transcripts

### Directory Structure

```
vibe-product-mgmt/
├── main/
│   └── sources/           # All synced data sources
│       ├── SOURCES.md     # Index of all data sources
│       └── granola/       # Local meeting cache sync output
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
3. **Full content retrieval**: Granola MCP → fetch server-side summaries/transcripts as needed

## Data Sources

- **Granola local cache**: Meeting metadata, folder mapping, and manual notes (when present)
- **Granola MCP**: Full AI summaries and transcripts for supported plans

See `main/sources/SOURCES.md` for detailed information about each data source.

## Development

For detailed technical documentation and guidance for AI assistants working with this codebase, see `CLAUDE.md`.

## License

MIT License - see `LICENSE` file for details.
