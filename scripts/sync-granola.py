#!/usr/bin/env python3
"""
Granola Notes Sync Script
Syncs Granola meeting notes and transcripts into the project folder structure.
Preserves metadata: participants, timestamps, folders, duration, etc.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


class GranolaSync:
    """Handles syncing Granola notes to local markdown files with metadata."""

    def __init__(self, cache_path: Optional[str] = None):
        """Initialize the sync with Granola cache path."""
        self.cache_path = cache_path or os.path.expanduser(
            "~/Library/Application Support/Granola/cache-v3.json"
        )
        self.output_dir = Path(__file__).parent.parent / "main" / "sources" / "granola"
        self.meetings_dir = self.output_dir / "meetings"
        self.transcripts_dir = self.output_dir / "transcripts"
        self.last_sync_file = self.output_dir / ".last-sync"

        # Create directories if they don't exist
        self.meetings_dir.mkdir(parents=True, exist_ok=True)
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)

        # Cache for transcripts (loaded once)
        self.transcripts_cache = None

    def load_cache(self) -> Dict:
        """Load and parse Granola's cache file."""
        if not os.path.exists(self.cache_path):
            print(f"Error: Granola cache not found at {self.cache_path}")
            print("Please check your Granola installation or update the path.")
            sys.exit(1)

        with open(self.cache_path, 'r') as f:
            data = json.load(f)

        # Handle double-encoded JSON (cache is stored as string)
        if 'cache' in data and isinstance(data['cache'], str):
            cache_str = data['cache']
            return json.loads(cache_str)
        elif 'cache' in data:
            return data['cache']
        else:
            return data

    def _extract_prosemirror_text(self, prosemirror_doc: Dict) -> str:
        """Extract plain text from ProseMirror document format."""
        if not prosemirror_doc or not isinstance(prosemirror_doc, dict):
            return ""

        content = prosemirror_doc.get('content', [])
        if not content:
            return ""

        text_parts = []

        def extract_text_recursive(node):
            """Recursively extract text from ProseMirror nodes."""
            if isinstance(node, dict):
                # If node has text, add it
                if 'text' in node:
                    return node['text']

                # If node has content, recurse
                if 'content' in node and isinstance(node['content'], list):
                    node_texts = []
                    for child in node['content']:
                        child_text = extract_text_recursive(child)
                        if child_text:
                            node_texts.append(child_text)

                    # Add line breaks between block elements
                    node_type = node.get('type', '')
                    if node_type in ['paragraph', 'heading']:
                        return '\n'.join(node_texts) if node_texts else ''
                    else:
                        return ' '.join(node_texts) if node_texts else ''

            return ""

        for node in content:
            text = extract_text_recursive(node)
            if text:
                text_parts.append(text)

        return '\n\n'.join(text_parts)

    def parse_meeting(self, meeting_data: Dict, transcript_data: Optional[List] = None,
                     folder_mapping: Optional[Dict] = None,
                     panels_dict: Optional[Dict] = None) -> Dict:
        """Extract and structure meeting data from Granola's cache format."""
        # Extract basic info
        meeting_id = meeting_data.get('id', '')
        title = meeting_data.get('title', 'Untitled Meeting')
        created_at = meeting_data.get('created_at', '')
        updated_at = meeting_data.get('updated_at', '')

        # Extract notes - prioritize markdown version (what Granola exports)
        notes_markdown = meeting_data.get('notes_markdown', '')
        notes_plain = meeting_data.get('notes_plain', '')

        # Use markdown if available, fallback to plain, then ProseMirror
        if notes_markdown:
            notes_text = notes_markdown
        elif notes_plain:
            notes_text = notes_plain
        else:
            # Fall back to extracting from ProseMirror format
            notes_prosemirror = meeting_data.get('notes', {})
            notes_text = self._extract_prosemirror_text(notes_prosemirror)

        # Extract AI summaries from documentPanels
        ai_summaries = []
        if panels_dict and meeting_id in panels_dict:
            meeting_panels = panels_dict[meeting_id]
            for panel_id, panel in meeting_panels.items():
                panel_content = panel.get('content', {})
                if isinstance(panel_content, dict):
                    summary_text = self._extract_prosemirror_text(panel_content)
                    if summary_text:
                        ai_summaries.append(summary_text)

        # Combine all AI summaries
        overview = '\n\n---\n\n'.join(ai_summaries) if ai_summaries else ''

        # Extract people/participants
        people = meeting_data.get('people', [])
        participants = []
        if people:
            for person in people:
                if isinstance(person, dict):
                    name = person.get('name') or person.get('email', '')
                    if name:
                        participants.append(name)

        # Get transcript if provided
        transcript_text = ""
        duration = "Unknown"
        if transcript_data:
            transcript_text = self._format_transcript(transcript_data)
            duration = self._calculate_duration(transcript_data)

        # Extract folder from mapping
        folder = "Uncategorized"
        if folder_mapping and meeting_id in folder_mapping:
            folder = folder_mapping[meeting_id]

        # Tags
        tags = meeting_data.get('tags', [])
        if tags and isinstance(tags, list):
            tags = [tag for tag in tags if isinstance(tag, str)]
        else:
            tags = []

        return {
            'id': meeting_id,
            'title': title,
            'created_at': created_at,
            'updated_at': updated_at,
            'folder': folder,
            'participants': participants,
            'tags': tags,
            'duration': duration,
            'transcript': transcript_text,
            'notes': notes_text,
            'ai_summary': overview,
            'granola_url': f"granola://meeting/{meeting_id}"
        }

    def _format_transcript(self, transcript_data: List) -> str:
        """Format transcript with speaker labels from Granola format."""
        if not transcript_data:
            return ""

        lines = []
        current_source = None
        current_text = []

        for entry in transcript_data:
            if isinstance(entry, dict):
                source = entry.get('source', 'unknown')
                text = entry.get('text', '').strip()

                if not text:
                    continue

                # Group consecutive utterances from same source
                if source == current_source:
                    current_text.append(text)
                else:
                    # Output previous source's text
                    if current_source and current_text:
                        speaker_label = "🎤 You" if current_source == "microphone" else "💬 System"
                        lines.append(f"**{speaker_label}**: {' '.join(current_text)}")

                    # Start new source
                    current_source = source
                    current_text = [text]

        # Don't forget the last group
        if current_source and current_text:
            speaker_label = "🎤 You" if current_source == "microphone" else "💬 System"
            lines.append(f"**{speaker_label}**: {' '.join(current_text)}")

        return "\n\n".join(lines)

    def _calculate_duration(self, transcript_data: List) -> str:
        """Calculate meeting duration from transcript timestamps."""
        if not transcript_data or len(transcript_data) < 2:
            return "Unknown"

        try:
            # Parse ISO timestamps
            first_ts_str = transcript_data[0].get('start_timestamp', '')
            last_ts_str = transcript_data[-1].get('end_timestamp', '')

            if not first_ts_str or not last_ts_str:
                return "Unknown"

            first_ts = datetime.fromisoformat(first_ts_str.replace('Z', '+00:00'))
            last_ts = datetime.fromisoformat(last_ts_str.replace('Z', '+00:00'))

            duration = last_ts - first_ts
            duration_seconds = int(duration.total_seconds())

            if duration_seconds <= 0:
                return "Unknown"

            hours = duration_seconds // 3600
            minutes = (duration_seconds % 3600) // 60

            if hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        except (TypeError, KeyError, ValueError):
            return "Unknown"

    def create_markdown(self, meeting: Dict) -> str:
        """Create markdown file with frontmatter for a meeting."""
        # Create YAML frontmatter
        frontmatter = [
            "---",
            f"granola_id: {meeting['id']}",
            f"title: \"{meeting['title']}\"",
            f"created_at: {meeting['created_at']}",
            f"updated_at: {meeting['updated_at']}",
            f"folder: {meeting['folder']}",
            f"duration: {meeting['duration']}",
            f"granola_url: {meeting['granola_url']}"
        ]

        if meeting['participants']:
            frontmatter.append("participants:")
            for participant in meeting['participants']:
                frontmatter.append(f"  - {participant}")

        if meeting['tags']:
            frontmatter.append("tags:")
            for tag in meeting['tags']:
                frontmatter.append(f"  - {tag}")

        frontmatter.append("---")
        frontmatter.append("")

        # Create content
        content = [
            f"# {meeting['title']}",
            "",
        ]

        if meeting['ai_summary']:
            content.extend([
                "## AI Summary",
                "",
                meeting['ai_summary'],
                ""
            ])

        if meeting['notes']:
            content.extend([
                "## Notes",
                "",
                meeting['notes'],
                ""
            ])

        return "\n".join(frontmatter + content)

    def create_transcript_markdown(self, meeting: Dict) -> Optional[str]:
        """Create separate transcript markdown file."""
        if not meeting['transcript']:
            return None

        frontmatter = [
            "---",
            f"granola_id: {meeting['id']}",
            f"title: \"{meeting['title']}\"",
            f"created_at: {meeting['created_at']}",
            f"duration: {meeting['duration']}",
            "---",
            ""
        ]

        content = [
            f"# {meeting['title']} - Transcript",
            "",
            meeting['transcript']
        ]

        return "\n".join(frontmatter + content)

    def sync_meetings(self, days: Optional[int] = 7, folder: Optional[str] = None,
                     include_transcripts: bool = True):
        """Sync meetings from Granola cache to local markdown files."""
        print(f"Loading Granola cache from: {self.cache_path}")
        cache_data = self.load_cache()

        # Get meetings from cache (they're in state.documents)
        state = cache_data.get('state', {})
        meetings_dict = state.get('documents', {})
        transcripts_dict = state.get('transcripts', {})
        doc_panels = state.get('documentPanels', {})

        # Build folder mapping from documentLists
        doc_lists_metadata = state.get('documentListsMetadata', {})
        doc_lists = state.get('documentLists', {})

        meeting_to_folder = {}
        for list_id, meetings_in_list in doc_lists.items():
            folder_name = doc_lists_metadata.get(list_id, {}).get('title', 'Unknown')
            for meeting_id in meetings_in_list:
                meeting_to_folder[meeting_id] = folder_name

        # Convert dict to list if needed
        if isinstance(meetings_dict, dict):
            meetings_data = list(meetings_dict.values())
        else:
            meetings_data = meetings_dict

        print(f"Found {len(meetings_data)} total meetings in cache")
        print(f"Found {len(transcripts_dict)} transcripts in cache")
        print(f"Found {len(doc_lists_metadata)} folders in cache")
        print(f"Found {len(doc_panels)} meetings with AI panels")

        # Filter by date if specified
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
            filtered_meetings = []

            for meeting_data in meetings_data:
                created_at = meeting_data.get('created_at', '')
                if created_at:
                    try:
                        meeting_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        if meeting_date.replace(tzinfo=None) >= cutoff_date:
                            filtered_meetings.append(meeting_data)
                    except ValueError:
                        continue

            meetings_data = filtered_meetings
            print(f"Filtered to {len(meetings_data)} meetings from last {days} days")

        # Process each meeting
        synced_count = 0
        for meeting_data in meetings_data:
            try:
                # Get transcript for this meeting if available
                meeting_id = meeting_data.get('id', '')
                transcript_data = transcripts_dict.get(meeting_id, [])

                # Parse meeting with transcript, folder mapping, and AI panels
                meeting = self.parse_meeting(meeting_data, transcript_data, meeting_to_folder, doc_panels)

                # Filter by folder if specified
                if folder and meeting['folder'] != folder:
                    continue

                # Create safe filename
                date_str = meeting['created_at'][:10] if meeting['created_at'] else 'unknown'
                safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else ''
                                    for c in meeting['title'])
                safe_title = safe_title.strip()[:50]  # Limit length

                # Save meeting notes
                meeting_filename = f"{date_str}_{safe_title}_{meeting['id'][:8]}.md"
                meeting_path = self.meetings_dir / meeting_filename

                markdown_content = self.create_markdown(meeting)
                with open(meeting_path, 'w') as f:
                    f.write(markdown_content)

                # Save transcript separately if requested
                if include_transcripts and meeting['transcript']:
                    transcript_filename = f"{date_str}_{safe_title}_{meeting['id'][:8]}_transcript.md"
                    transcript_path = self.transcripts_dir / transcript_filename

                    transcript_content = self.create_transcript_markdown(meeting)
                    if transcript_content:
                        with open(transcript_path, 'w') as f:
                            f.write(transcript_content)

                synced_count += 1
                print(f"✓ Synced: {meeting['title']}")

            except Exception as e:
                print(f"✗ Error processing meeting: {e}")
                continue

        # Update last sync timestamp
        with open(self.last_sync_file, 'w') as f:
            f.write(datetime.now().isoformat())

        print(f"\n✅ Sync complete! Synced {synced_count} meetings")
        print(f"   Notes: {self.meetings_dir}")
        print(f"   Transcripts: {self.transcripts_dir}")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Sync Granola meeting notes to local markdown files')
    parser.add_argument('--days', type=int, default=7,
                       help='Number of days to sync (default: 7, use 0 for all)')
    parser.add_argument('--folder', type=str,
                       help='Only sync meetings from this folder')
    parser.add_argument('--no-transcripts', action='store_true',
                       help='Skip syncing transcripts (notes only)')
    parser.add_argument('--cache-path', type=str,
                       help='Custom path to Granola cache file')

    args = parser.parse_args()

    syncer = GranolaSync(cache_path=args.cache_path)

    days = None if args.days == 0 else args.days
    syncer.sync_meetings(
        days=days,
        folder=args.folder,
        include_transcripts=not args.no_transcripts
    )


if __name__ == '__main__':
    main()
