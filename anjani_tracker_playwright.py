#!/usr/bin/env python3
"""
Anjani Courier Package Tracker (Playwright version)
Tracks packages on https://trackcourier.io/anjani-courier-tracking
Uses Playwright to handle dynamic JavaScript content
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from datetime import datetime
import sys
import json
import re


class AnjaniTrackerPlaywright:
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
                page.goto(url, wait_until='networkidle', timeout=30000)

                # Wait for content to load (wait for tracking data to appear)
                try:
                    # Wait for either the status bar or checkpoint data to load
                    page.wait_for_selector('text=/IN TRANSIT|DELIVERED|PENDING|OUT FOR DELIVERY/i', timeout=10000)
                except PlaywrightTimeoutError:
                    # If status doesn't appear, continue anyway
                    pass

                # Extract the page content
                page_text = page.inner_text('body')

                # Extract status
                status_patterns = [
                    r'(IN TRANSIT|IN-TRANSIT)',
                    r'(DELIVERED)',
                    r'(PENDING)',
                    r'(OUT FOR DELIVERY)'
                ]

                for pattern in status_patterns:
                    match = re.search(pattern, page_text, re.IGNORECASE)
                    if match:
                        tracking_info['status'] = match.group(1).upper().replace('-', ' ')
                        break

                # Extract checkpoints using the list structure
                try:
                    # Wait for the checkpoint list to load
                    page.wait_for_timeout(3000)

                    # Try to find checkpoint list items
                    # The checkpoints are in a list structure
                    checkpoint_elements = page.query_selector_all('ul li, .checkpoint-list li, div[class*="checkpoint"]')

                    if not checkpoint_elements:
                        # Fallback: parse from text content
                        lines = page_text.split('\n')
                        date_pattern = r'(\d{1,2}-(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-\d{4})'
                        time_pattern = r'(\d{1,2}:\d{2}\s*(?:AM|PM))'

                        temp_checkpoints = []
                        i = 0
                        while i < len(lines):
                            line = lines[i].strip()
                            date_match = re.search(date_pattern, line)

                            if date_match:
                                date_str = date_match.group(1)
                                time_str = ''
                                activity_str = ''
                                location_str = ''

                                # Extract time if present
                                time_match = re.search(time_pattern, line)
                                if time_match:
                                    time_str = time_match.group(1)

                                # Look ahead to gather activity and location
                                look_ahead = 1
                                while i + look_ahead < len(lines) and look_ahead <= 3:
                                    next_line = lines[i + look_ahead].strip()

                                    if not next_line or re.search(date_pattern, next_line):
                                        break

                                    if 'Anjani Courier' in next_line:
                                        look_ahead += 1
                                        continue

                                    # Check if it's a location (usually contains city/area names or has hyphens)
                                    if '-' in next_line and not re.search(date_pattern, next_line):
                                        location_str = next_line
                                    elif not activity_str:
                                        activity_str = next_line
                                    elif not location_str:
                                        location_str = next_line

                                    look_ahead += 1

                                temp_checkpoints.append({
                                    'date': date_str,
                                    'time': time_str,
                                    'activity': activity_str,
                                    'location': location_str
                                })

                            i += 1

                        # Deduplicate and add to tracking info
                        seen = set()
                        for cp in temp_checkpoints:
                            key = f"{cp['date']}-{cp['time']}-{cp['activity']}"
                            if key not in seen:
                                seen.add(key)
                                tracking_info['checkpoints'].append(cp)

                except Exception as e:
                    print(f"Warning: Error parsing checkpoints: {str(e)}")

                # Close browser
                browser.close()

        except PlaywrightTimeoutError:
            tracking_info['error'] = 'Timeout loading tracking page'
        except Exception as e:
            tracking_info['error'] = f'Error: {str(e)}'

        return tracking_info

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


def main():
    """Main function for CLI usage"""
    if len(sys.argv) < 2:
        print("=" * 70)
        print("🚚 Anjani Courier Package Tracker")
        print("=" * 70)
        print("\nUsage:")
        print("  python3 anjani_tracker_playwright.py <tracking_number> [tracking_number2 ...]")
        print("\nExample:")
        print("  python3 anjani_tracker_playwright.py 1566745519")
        print("\nOptions:")
        print("  --show-browser    Show browser window (default: headless)")
        print("\nNote: Requires Playwright. Install with:")
        print("  uv pip install playwright")
        print("  uv run playwright install chromium")
        print("=" * 70)
        sys.exit(1)

    # Parse arguments
    args = sys.argv[1:]
    show_browser = '--show-browser' in args
    if show_browser:
        args.remove('--show-browser')

    tracking_numbers = args

    if not tracking_numbers:
        print("❌ Error: No tracking numbers provided")
        sys.exit(1)

    tracker = AnjaniTrackerPlaywright(headless=not show_browser)

    print(f"\n🔍 Tracking {len(tracking_numbers)} package(s)...\n")

    for tracking_number in tracking_numbers:
        tracking_info = tracker.track(tracking_number)
        tracker.print_tracking_info(tracking_info)

        # Optional: Save to JSON file
        # with open(f'tracking_{tracking_number}.json', 'w') as f:
        #     json.dump(tracking_info, f, indent=2)


if __name__ == "__main__":
    main()
