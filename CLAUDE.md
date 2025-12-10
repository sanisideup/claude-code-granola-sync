# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This repository provides tools to sync Granola meeting notes into a local git repository for AI-assisted analysis. It enables comprehensive review of product decisions, team discussions, and meeting context.

## Architecture

### Data Flow Pattern

The repository uses a **local sync architecture**:

1. **Local Sync** (versioned in git): Documents synced to `main/sources/[source-name]/` for offline access and version tracking
2. **Python Sync Scripts**: Located in `scripts/sync-[source-name].py`, handle data extraction and transformation
3. **Claude Code Slash Commands**: Located in `.claude/commands/`, provide user-friendly interfaces to sync scripts

### Directory Structure

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
        └── sync-granola.md
```

### Data Source Architecture

Each data source follows a consistent pattern:

1. **Source Directory**: `main/sources/[source-name]/`
   - Contains synced markdown files with YAML frontmatter
   - Includes `README.md` with source-specific documentation
   - Includes `.sync-config.json` with sync preferences
   - Includes `.last-sync` timestamp file

2. **Sync Script**: `scripts/sync-[source-name].py`
   - Python 3.7+ script with argparse CLI
   - Reads from local cache or API
   - Outputs structured markdown files
   - Preserves full metadata in YAML frontmatter

3. **Slash Command**: `.claude/commands/sync-[source-name].md`
   - User-friendly interface to sync script
   - Handles argument parsing
   - Provides feedback on sync status

## Common Commands

### Sync Operations

```bash
# Sync Granola meeting notes (last 7 days by default)
/sync-granola

# Sync specific time ranges
/sync-granola 30          # Last 30 days
/sync-granola all         # All meetings

# Sync specific folders
/sync-granola folder:Innovation

# Skip transcripts (faster sync)
/sync-granola --no-transcripts

# Direct script invocation
python3 scripts/sync-granola.py --days 7 --folder Innovation
```

## Key Technical Details

### Granola Sync Implementation

- **Cache Location**: `~/Library/Application Support/Granola/cache-v3.json`
- **Cache Format**: Double-encoded JSON (cache stored as string within JSON)
- **Data Structure**:
  - `state.documents`: Meeting metadata and notes
  - `state.transcripts`: Full transcripts by meeting ID
  - `state.documentPanels`: AI-generated summaries
  - `state.documentLists`: Folder organization
  - `state.documentListsMetadata`: Folder names

- **ProseMirror Parsing**: Notes stored in ProseMirror document format, requires recursive text extraction from nested node structure

- **Output Format**: Markdown with YAML frontmatter containing:
  - `granola_id`: Unique meeting identifier
  - `title`, `created_at`, `updated_at`
  - `folder`: Project/team folder
  - `duration`: Calculated from transcript timestamps
  - `participants`: Extracted from people array
  - `tags`: User-defined tags
  - `granola_url`: Deep link (format: `granola://meeting/{id}`)

- **File Naming**: `YYYY-MM-DD_Title-Slug_[8-char-id].md`

## Development Workflow

### Adding a New Data Source

1. Create source directory: `main/sources/[source-name]/`
2. Write Python sync script: `scripts/sync-[source-name].py`
3. Create slash command: `.claude/commands/sync-[source-name].md`
4. Add config file: `main/sources/[source-name]/.sync-config.json`
5. Write README: `main/sources/[source-name]/README.md`
6. Update index: `main/sources/SOURCES.md`

### Sync Script Requirements

- Python 3.7+ with standard library only (no external dependencies)
- Argparse CLI with `--days`, `--folder` options
- YAML frontmatter in all output markdown files
- Error handling with clear messages
- Last sync timestamp tracking (`.last-sync` file)
- Summary output (count of synced items, file locations)

### Markdown File Standards

- YAML frontmatter with metadata
- H1 title matching document title
- Sections: "AI Summary", "Notes", "Transcript" (as applicable)
- Clean filenames (alphanumeric, hyphens, underscores only)
- Maximum 50-character title slugs

## Git Workflow

This repository is version controlled to track changes in synced data over time.

```bash
# Typical workflow after sync
git add main/sources/[source-name]/
git commit -m "Sync [source-name]: [description]"
git push
```

