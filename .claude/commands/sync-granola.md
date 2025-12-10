# Sync Granola meeting notes and transcripts into the project folder with full metadata preservation.

# Arguments

The command accepts optional arguments from the user: `$ARGUMENTS`

## Argument formats:
- No arguments: sync last 7 days (default)
- Number like `30` or `30d`: sync last N days
- `--all` or `all`: sync all meetings
- `folder:FolderName`: sync only meetings from specific folder (e.g., `folder:Innovation`)
- `--no-transcripts`: skip syncing transcripts (notes only)

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
   - Transcripts: `main/sources/granola/transcripts/`
3. 📊 Brief summary of what was synced (date range, folders if filtered)
4. ⚠️ Any errors or warnings

# Notes

- The script reads from Granola's local cache: `~/Library/Application Support/Granola/cache-v3.json`
- Each meeting is saved as markdown with YAML frontmatter containing:
  - Meeting ID, title, dates
  - Participants list
  - Folder/project association
  - Duration
  - Tags
  - Link back to Granola
- Transcripts are saved separately for easier navigation
- Last sync timestamp is tracked in `.last-sync` file
