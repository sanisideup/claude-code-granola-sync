# Sync Granola meetings from local cache into the project folder with metadata preservation.

# Arguments

The command accepts optional arguments from the user: `$ARGUMENTS`

## Argument formats:
- No arguments: sync last 7 days (default)
- Number like `30` or `30d`: sync last N days
- `--all` or `all`: sync all meetings
- `folder:FolderName`: sync only meetings from specific folder (e.g., `folder:Innovation`)
- `--no-transcripts`: optional legacy flag (transcripts may not exist in cache v4)

# Instructions

Run the Granola sync script with the appropriate arguments:

1. Parse the `$ARGUMENTS` to determine sync options
2. Build the command with proper flags:
   - If `$ARGUMENTS` is empty: use default (last 7 days)
   - If `$ARGUMENTS` contains a number: use `--days N`
   - If `$ARGUMENTS` contains `--all` or `all`: use `--days 0`
   - If `$ARGUMENTS` contains `folder:X`: extract folder name and use `--folder X`
   - If `$ARGUMENTS` contains `--no-transcripts`: add the flag

3. Execute the sync script: `python3 scripts/sync-granola.py [flags]`

4. After sync completes, provide a summary:
   - Number of meetings synced
   - Location of saved files
   - Any errors encountered

# Examples

**User input**: `/sync-granola`
**Command**: `python3 scripts/sync-granola.py --days 7`

**User input**: `/sync-granola 30`
**Command**: `python3 scripts/sync-granola.py --days 30`

**User input**: `/sync-granola all`
**Command**: `python3 scripts/sync-granola.py --days 0`

**User input**: `/sync-granola folder:Innovation`
**Command**: `python3 scripts/sync-granola.py --days 7 --folder Innovation`

**User input**: `/sync-granola 14 --no-transcripts`
**Command**: `python3 scripts/sync-granola.py --days 14 --no-transcripts`

# Expected Output

After syncing, show the user:
1. ✅ Success message with count of synced meetings
2. 📁 File locations:
   - Meeting notes: `main/sources/granola/meetings/`
   - Transcripts: `main/sources/granola/transcripts/` (legacy/pre-migration only)
3. 📊 Brief summary of what was synced (date range, folders if filtered)
4. ⚠️ Any warnings (especially metadata-only cache detection)

# Notes

- The script reads from Granola's local cache: `~/Library/Application Support/Granola/cache-v3.json`
- For post-Feb 2026 meetings, local cache may contain metadata only
- AI summaries + historical transcripts are server-side in Granola cache v4
- Use Granola MCP for full content retrieval:
  - https://docs.granola.ai/help-center/sharing/integrations/mcp
- Each meeting is saved as markdown with YAML frontmatter containing metadata (ID, title, dates, participants, folder, tags, link)
- Last sync timestamp is tracked in `.last-sync` file
