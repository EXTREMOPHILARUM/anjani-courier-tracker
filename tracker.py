#!/usr/bin/env python3
"""
Anjani Courier Package Tracker (Final Version)
Tracks packages on https://trackcourier.io/anjani-courier-tracking
Uses Playwright to handle dynamic JavaScript content
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from datetime import datetime
import sys
import json
import re
import requests


class AnjaniTracker:
    """Tracker for Anjani Courier packages using Playwright"""

    BASE_URL = "https://trackcourier.io/track-and-trace/anjani-courier"

    def __init__(self, headless=True):
        """
        Initialize the tracker

        Args:
            headless: Run browser in headless mode (default: True)
        """
        self.headless = headless

    def track(self, tracking_number):
        """
        Track a package by tracking number

        Args:
            tracking_number: The tracking ID to look up

        Returns:
            dict: Tracking information including status and checkpoints
        """
        url = f"{self.BASE_URL}/{tracking_number}"

        tracking_info = {
            'tracking_number': tracking_number,
            'courier': 'Anjani Courier',
            'status': None,
            'checkpoints': [],
            'url': url,
            'fetched_at': datetime.now().isoformat(),
            'error': None
        }

        try:
            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch(headless=self.headless)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )
                page = context.new_page()

                # Navigate to tracking page
                page.goto(url, wait_until='networkidle', timeout=60000)

                # Wait for content to load - site takes long to load dynamic content
                page.wait_for_timeout(20000)

                # Extract status
                page_text = page.inner_text('body')
                status_patterns = [
                    (r'IN TRANSIT|IN-TRANSIT', 'IN TRANSIT'),
                    (r'DELIVERED', 'DELIVERED'),
                    (r'PENDING', 'PENDING'),
                    (r'OUT FOR DELIVERY', 'OUT FOR DELIVERY')
                ]

                for pattern, status_name in status_patterns:
                    if re.search(pattern, page_text, re.IGNORECASE):
                        tracking_info['status'] = status_name
                        break

                # Extract checkpoints using JavaScript
                try:
                    checkpoint_texts = page.evaluate('''
                        () => {
                            return Array.from(document.querySelectorAll('ul li'))
                                .map(function(li) { return li.innerText; })
                                .filter(function(text) {
                                    if (!text) return false;
                                    var months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                                    for (var i = 0; i < months.length; i++) {
                                        if (text.indexOf('-' + months[i] + '-') > -1) {
                                            return true;
                                        }
                                    }
                                    return false;
                                });
                        }
                    ''')

                    # Debug: print what we got
                    if not checkpoint_texts:
                        # Try alternative selector
                        all_text = page.inner_text('body')
                        if 'Jan-2026' in all_text or 'BANDRA' in all_text:
                            # Data is there but not extracted, parse from full text
                            lines = all_text.split('\n')
                            temp_text = []
                            for i, line in enumerate(lines):
                                if re.search(r'\d{1,2}-(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-\d{4}', line):
                                    # Collect this line and next few lines
                                    block = []
                                    for j in range(min(5, len(lines) - i)):
                                        block.append(lines[i + j])
                                    temp_text.append('\n'.join(block))
                            checkpoint_texts = temp_text

                    # Parse checkpoint texts
                    for cp_text in checkpoint_texts:
                        checkpoint = self._parse_checkpoint(cp_text)
                        if checkpoint['date']:
                            tracking_info['checkpoints'].append(checkpoint)

                except Exception as e:
                    tracking_info['error'] = f'Error extracting checkpoints: {str(e)}'

                # Close browser
                browser.close()

        except PlaywrightTimeoutError:
            tracking_info['error'] = 'Timeout loading tracking page'
        except Exception as e:
            tracking_info['error'] = f'Error: {str(e)}'

        return tracking_info

    def _parse_checkpoint(self, text):
        """Parse a checkpoint text into structured data"""
        checkpoint = {
            'date': '',
            'time': '',
            'activity': '',
            'location': ''
        }

        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # Extract date
        date_pattern = r'(\d{1,2}-(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-\d{4})'
        for line in lines:
            date_match = re.search(date_pattern, line)
            if date_match:
                checkpoint['date'] = date_match.group(1)
                break

        # Extract time
        time_pattern = r'(\d{1,2}:\d{2}\s*(?:AM|PM))'
        for line in lines:
            time_match = re.search(time_pattern, line)
            if time_match:
                checkpoint['time'] = time_match.group(1)
                break

        # Extract activity and location
        activity_candidates = []
        location_candidates = []

        for line in lines:
            # Skip lines that are just the date, time, or courier name
            if line == checkpoint['date']:
                continue
            if checkpoint['time'] and line == checkpoint['time']:
                continue
            if 'Anjani Courier' == line:
                continue

            # Lines with dashes (like BANDRA-EAST) are likely locations
            if '-' in line and not re.search(date_pattern, line):
                location_candidates.append(line)
            # Status/activity indicators
            elif re.search(r'\[.*?\]|IN TRANSIT|DELIVERED|ON WAY|IN |OUT', line, re.IGNORECASE):
                activity_candidates.append(line)
            # Other lines
            else:
                # If it looks like a place name (all caps or contains common location words)
                if line.isupper() or any(word in line.upper() for word in ['EAST', 'WEST', 'NORTH', 'SOUTH', 'NAGAR', 'ROAD']):
                    location_candidates.append(line)
                else:
                    activity_candidates.append(line)

        # Assign activity and location
        if activity_candidates:
            checkpoint['activity'] = ' - '.join(activity_candidates)
        if location_candidates:
            checkpoint['location'] = location_candidates[0]

        return checkpoint

    def track_multiple(self, tracking_numbers):
        """
        Track multiple packages

        Args:
            tracking_numbers: List of tracking IDs

        Returns:
            list: List of tracking information dicts
        """
        results = []
        for tracking_number in tracking_numbers:
            result = self.track(tracking_number)
            results.append(result)
        return results

    def print_tracking_info(self, tracking_info):
        """Pretty print tracking information"""
        if tracking_info.get('error'):
            print(f"❌ Error: {tracking_info['error']}")
            if not tracking_info.get('checkpoints'):
                return

        print("\n" + "="*70)
        print(f"📦 Tracking Number: {tracking_info['tracking_number']}")
        print(f"🚚 Courier: {tracking_info['courier']}")

        if tracking_info['status']:
            status_emoji = {
                'DELIVERED': '✅',
                'IN TRANSIT': '🚛',
                'PENDING': '⏳',
                'OUT FOR DELIVERY': '🚚'
            }
            emoji = status_emoji.get(tracking_info['status'], '📍')
            print(f"{emoji} Status: {tracking_info['status']}")

        print(f"🔗 URL: {tracking_info['url']}")
        print(f"🕐 Fetched: {tracking_info['fetched_at']}")

        if tracking_info['checkpoints']:
            print(f"\n📋 Tracking History ({len(tracking_info['checkpoints'])} events):")
            print("-" * 70)

            for i, checkpoint in enumerate(tracking_info['checkpoints'], 1):
                print(f"\n[{i}] {checkpoint.get('date', 'N/A')}", end='')
                if checkpoint.get('time'):
                    print(f" at {checkpoint['time']}", end='')
                print()

                if checkpoint.get('activity'):
                    print(f"    📝 Activity: {checkpoint['activity']}")
                if checkpoint.get('location'):
                    print(f"    📍 Location: {checkpoint['location']}")
        else:
            print("\n⚠️  No tracking checkpoints found")

        print("="*70 + "\n")

    def save_to_json(self, tracking_info, filename=None):
        """Save tracking info to JSON file"""
        if not filename:
            filename = f"tracking_{tracking_info['tracking_number']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filename, 'w') as f:
            json.dump(tracking_info, f, indent=2)

        print(f"💾 Saved tracking data to: {filename}")

    def send_to_google_chat(self, tracking_info, webhook_url):
        """
        Send tracking notification to Google Chat webhook

        Args:
            tracking_info: Dictionary containing tracking information
            webhook_url: Google Chat webhook URL

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Build the message text
            status_emoji = {
                'DELIVERED': '✅',
                'IN TRANSIT': '🚛',
                'PENDING': '⏳',
                'OUT FOR DELIVERY': '🚚'
            }

            emoji = status_emoji.get(tracking_info.get('status', ''), '📍')

            # Build title with optional label
            title = f"📦 Package Update - {tracking_info['tracking_number']}"
            if tracking_info.get('label'):
                title = f"📦 {tracking_info['label']} ({tracking_info['tracking_number']})"

            message_lines = [
                f"*{title}*",
                f"{emoji} *Status:* {tracking_info.get('status', 'Unknown')}",
                f"🚚 *Courier:* {tracking_info['courier']}",
            ]

            # Add latest checkpoint if available
            if tracking_info.get('checkpoints') and len(tracking_info['checkpoints']) > 0:
                latest = tracking_info['checkpoints'][0]
                message_lines.append("")
                message_lines.append("*Latest Update:*")
                message_lines.append(f"📅 {latest.get('date', 'N/A')} {latest.get('time', '')}")
                if latest.get('activity'):
                    message_lines.append(f"📝 {latest['activity']}")
                if latest.get('location'):
                    message_lines.append(f"📍 {latest['location']}")

            # Add tracking URL
            message_lines.append("")
            message_lines.append(f"🔗 <{tracking_info['url']}|View Full Tracking>")

            # Create Google Chat message payload
            payload = {
                "text": "\n".join(message_lines)
            }

            # Send POST request to webhook
            response = requests.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json; charset=UTF-8'},
                timeout=10
            )

            if response.status_code == 200:
                print(f"💬 Sent notification to Google Chat")
                return True
            else:
                print(f"❌ Failed to send to Google Chat: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Error sending to Google Chat: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error sending to Google Chat: {str(e)}")
            return False

    @staticmethod
    def load_state(state_file='tracking_state.json'):
        """
        Load tracking state from JSON file

        Args:
            state_file: Path to state file (default: tracking_state.json)

        Returns:
            dict: Dictionary with tracking IDs as keys and tracking info as values
        """
        try:
            with open(state_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            print(f"⚠️  Warning: Could not parse {state_file}, starting fresh")
            return {}

    @staticmethod
    def save_state(state, state_file='tracking_state.json'):
        """
        Save tracking state to JSON file

        Args:
            state: Dictionary with tracking IDs as keys
            state_file: Path to state file (default: tracking_state.json)
        """
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

    @staticmethod
    def has_changes(old_info, new_info):
        """
        Compare two tracking info dictionaries to detect changes

        Args:
            old_info: Previous tracking information
            new_info: New tracking information

        Returns:
            tuple: (bool, list) - (has_changes, list of change descriptions)
        """
        changes = []

        # Check if status changed
        old_status = old_info.get('status')
        new_status = new_info.get('status')
        if old_status != new_status:
            changes.append(f"Status changed: {old_status} → {new_status}")

        # Check if new checkpoints were added
        old_checkpoints = old_info.get('checkpoints', [])
        new_checkpoints = new_info.get('checkpoints', [])

        # Compare number of checkpoints
        if len(new_checkpoints) > len(old_checkpoints):
            num_new = len(new_checkpoints) - len(old_checkpoints)
            changes.append(f"{num_new} new checkpoint(s) added")

        # Compare latest checkpoint details (if both have checkpoints)
        if old_checkpoints and new_checkpoints:
            old_latest = old_checkpoints[0]
            new_latest = new_checkpoints[0]

            # Check if the latest checkpoint is different
            if (old_latest.get('date') != new_latest.get('date') or
                old_latest.get('time') != new_latest.get('time') or
                old_latest.get('activity') != new_latest.get('activity') or
                old_latest.get('location') != new_latest.get('location')):
                changes.append("Latest checkpoint updated")

        # If we previously had no checkpoints but now we do
        if not old_checkpoints and new_checkpoints:
            changes.append("Initial tracking information available")

        return (len(changes) > 0, changes)


def main():
    """Main function for CLI usage"""
    if len(sys.argv) < 2:
        print("=" * 70)
        print("🚚 Anjani Courier Package Tracker")
        print("=" * 70)
        print("\nUsage:")
        print("  python3 anjani_tracker_final.py <tracking_number> [options]")
        print("\nExample:")
        print("  python3 anjani_tracker_final.py 1566745519")
        print("  python3 anjani_tracker_final.py 1566745519 --save-json")
        print("  python3 anjani_tracker_final.py 1566745519 1566745520 --show-browser")
        print("  python3 anjani_tracker_final.py 1566745519 --webhook=<webhook_url>")
        print("\nOptions:")
        print("  --show-browser          Show browser window (default: headless)")
        print("  --save-json             Save results to JSON file")
        print("  --webhook=<url>         Send notification to Google Chat webhook")
        print("\nNote: Requires Playwright. Install with:")
        print("  uv pip install playwright")
        print("  uv run playwright install chromium")
        print("=" * 70)
        sys.exit(1)

    # Parse arguments
    args = sys.argv[1:]
    show_browser = '--show-browser' in args
    save_json = '--save-json' in args

    # Extract webhook URL if provided
    webhook_url = None
    for arg in args:
        if arg.startswith('--webhook='):
            webhook_url = arg.split('=', 1)[1]
            break

    # Remove option flags to get tracking numbers
    tracking_numbers = [arg for arg in args if not arg.startswith('--')]

    if not tracking_numbers:
        print("❌ Error: No tracking numbers provided")
        sys.exit(1)

    tracker = AnjaniTracker(headless=not show_browser)

    print(f"\n🔍 Tracking {len(tracking_numbers)} package(s)...\n")

    for tracking_number in tracking_numbers:
        tracking_info = tracker.track(tracking_number)
        tracker.print_tracking_info(tracking_info)

        if save_json and not tracking_info.get('error'):
            tracker.save_to_json(tracking_info)

        if webhook_url and not tracking_info.get('error'):
            tracker.send_to_google_chat(tracking_info, webhook_url)


if __name__ == "__main__":
    main()
