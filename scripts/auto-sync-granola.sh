#!/bin/bash
# Auto-sync Granola meetings on session start
# Calculates days since last sync and runs sync-granola.py

set -e

# Get project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LAST_SYNC_FILE="$PROJECT_DIR/main/sources/granola/.last-sync"

# Function to calculate days between timestamps
calculate_days_since_sync() {
    local last_sync_timestamp="$1"
    local now=$(date +%s)

    # Parse ISO timestamp to epoch
    # Handle both formats: 2026-01-02T14:27:04.397566 and 2026-01-02T14:27:04+00:00
    local last_sync_epoch
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS date command
        last_sync_epoch=$(date -j -f "%Y-%m-%dT%H:%M:%S" "${last_sync_timestamp%%.*}" +%s 2>/dev/null || echo 0)
    else
        # Linux date command
        last_sync_epoch=$(date -d "${last_sync_timestamp}" +%s 2>/dev/null || echo 0)
    fi

    if [ "$last_sync_epoch" -eq 0 ]; then
        echo "0"  # Invalid timestamp, sync all
        return
    fi

    # Calculate days difference
    local diff_seconds=$((now - last_sync_epoch))
    local days=$((diff_seconds / 86400))

    # Add 1 to include partial days (e.g., if last sync was yesterday, sync 2 days to be safe)
    days=$((days + 1))

    echo "$days"
}

# Main sync logic
main() {
    local days_to_sync
    local sync_message

    if [ ! -f "$LAST_SYNC_FILE" ]; then
        # No previous sync, sync all
        days_to_sync=0
        sync_message="First sync - fetching all Granola meetings"
    else
        # Read last sync timestamp
        local last_sync_timestamp=$(cat "$LAST_SYNC_FILE" | tr -d '\n')

        # Calculate days since last sync
        days_to_sync=$(calculate_days_since_sync "$last_sync_timestamp")

        if [ "$days_to_sync" -eq 0 ] || [ "$days_to_sync" -lt 0 ]; then
            # Invalid calculation, default to 7 days
            days_to_sync=7
            sync_message="Auto-syncing last 7 days of Granola meetings (default)"
        else
            sync_message="Auto-syncing last ${days_to_sync} days of Granola meetings (since last sync)"
        fi
    fi

    # Run the sync (capture output but don't show it in hook response)
    if [ "$days_to_sync" -eq 0 ]; then
        python3 "$SCRIPT_DIR/sync-granola.py" --days 0 > /dev/null 2>&1
        sync_message="Auto-sync complete: All Granola meetings synced"
    else
        python3 "$SCRIPT_DIR/sync-granola.py" --days "$days_to_sync" > /dev/null 2>&1
        sync_message="Auto-sync complete: Synced ${days_to_sync} days of Granola meetings"
    fi

    # Return JSON with context for Claude
    echo "{\"hookSpecificOutput\": {\"hookEventName\": \"SessionStart\", \"additionalContext\": \"$sync_message\"}}"

    exit 0
}

main
