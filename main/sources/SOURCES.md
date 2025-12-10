# Data Sources Index

This directory contains all external data sources synced locally for AI-assisted analysis and review.

## Available Sources

### 📝 Granola Meeting Notes

**Location**: `sources/granola/`

Synced meeting notes and transcripts from Granola AI with full metadata.

**Sync Command**: `/sync-granola [options]`

**What's Included**:
- AI-generated meeting summaries
- Full transcripts with speaker identification
- Participant lists
- Meeting metadata (date, duration, folder, tags)
- Deep links back to Granola

**Use Cases**:
- Review past decisions and discussions
- Track action items across meetings
- Reference conversations in documentation
- Build context for sprint planning

---

## Sync Strategy

### Local (Versioned in Git)
✅ **Granola notes** - Synced weekly, full history tracked

### Benefits
- ✅ Offline access to critical docs
- ✅ Version control for historical tracking
- ✅ Full-text search across everything

---

## Quick Reference

| Source | Local Sync | Primary Use |
|--------|-----------|-------------|
| Granola | ✅ Yes | Meeting context, decisions |

---

## Best Practices

1. **Sync regularly**: Run `/sync-granola` weekly to keep data current
2. **Reference specific files**: Use file paths in Claude Code for precise context
3. **Combine sources**: Link Granola notes with other relevant documentation
4. **Version control**: Commit synced files to track changes over time
5. **Clean up**: Archive old meetings that are no longer relevant

---

## Contributing

To add a new data source:

1. Create folder under `sources/[source-name]/`
2. Write sync script in `scripts/sync-[source-name].py`
3. Create slash command in `.claude/commands/sync-[source-name].md`
4. Add config file in `sources/[source-name]/.sync-config.json`
5. Update this index with details
6. Document in source-specific README

---

**Last Updated**: 2025-11-28
