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
    local sync_output
    local sync_message

    if [ ! -f "$LAST_SYNC_FILE" ]; then
        # No previous sync, sync all
        days_to_sync=0
    else
        # Read last sync timestamp
        local last_sync_timestamp=$(cat "$LAST_SYNC_FILE" | tr -d '\n')

        # Calculate days since last sync
        days_to_sync=$(calculate_days_since_sync "$last_sync_timestamp")

        if [ "$days_to_sync" -eq 0 ] || [ "$days_to_sync" -lt 0 ]; then
            # Invalid calculation, default to 7 days
            days_to_sync=7
        fi
    fi

    # Run the sync and capture output
    if [ "$days_to_sync" -eq 0 ]; then
        sync_output=$(python3 "$SCRIPT_DIR/sync-granola.py" --days 0 2>&1)
    else
        sync_output=$(python3 "$SCRIPT_DIR/sync-granola.py" --days "$days_to_sync" 2>&1)
    fi

    # Extract synced meeting titles from output
    local meeting_titles=$(echo "$sync_output" | grep "✓ Synced:" | sed 's/✓ Synced: //' | head -10)
    local meeting_count=$(echo "$sync_output" | grep "✓ Synced:" | wc -l | tr -d ' ')

    # Check if transcripts were synced (sync-granola.py syncs transcripts by default)
    local has_transcripts="with transcripts"

    # Build summary message
    if [ "$meeting_count" -eq 0 ]; then
        sync_message="Granola auto-sync: No new meetings to sync"
    else
        # Calculate date range
        local today=$(date "+%Y-%m-%d")
        local start_date
        if [ "$days_to_sync" -eq 0 ]; then
            start_date="all time"
        else
            # Calculate start date (days_to_sync days ago)
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS date command
                start_date=$(date -v-${days_to_sync}d "+%Y-%m-%d")
            else
                # Linux date command
                start_date=$(date -d "${days_to_sync} days ago" "+%Y-%m-%d")
            fi
        fi

        # Build meeting list (show up to 5)
        local meeting_list=""
        local count=0
        while IFS= read -r title; do
            if [ -n "$title" ]; then
                meeting_list="${meeting_list}\n  • ${title}"
                count=$((count + 1))
                if [ $count -ge 5 ]; then
                    break
                fi
            fi
        done <<< "$meeting_titles"

        # Add "and X more" if there are more meetings
        local remaining=$((meeting_count - count))
        if [ $remaining -gt 0 ]; then
            meeting_list="${meeting_list}\n  • ...and ${remaining} more"
        fi

        # Format the final message
        if [ "$days_to_sync" -eq 0 ]; then
            sync_message="Granola auto-sync complete: ${meeting_count} meeting(s) synced (all time) ${has_transcripts}${meeting_list}"
        else
            sync_message="Granola auto-sync complete: ${meeting_count} meeting(s) synced\nDate range: ${start_date} to ${today}\n${has_transcripts}${meeting_list}"
        fi
    fi

    # Write to a notification file for user reference
    local notification_file="$PROJECT_DIR/main/sources/granola/.last-auto-sync"
    echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" > "$notification_file"
    echo -e "$sync_message" >> "$notification_file"
    echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >> "$notification_file"

    # Try to write directly to the terminal (bypassing stdout/stderr capture)
    if [ -w /dev/tty ]; then
        echo "" > /dev/tty
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" > /dev/tty
        echo -e "$sync_message" > /dev/tty
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" > /dev/tty
        echo "" > /dev/tty
    fi

    # Return JSON with the actual sync message for Claude to display
    # Escape the message for JSON (replace quotes and newlines)
    local json_message=$(echo -e "$sync_message" | sed 's/"/\\"/g' | awk '{printf "%s\\n", $0}' | sed 's/\\n$//')
    echo "{\"hookSpecificOutput\": {\"hookEventName\": \"SessionStart\", \"additionalContext\": \"$json_message\"}}"

    exit 0
}

main
