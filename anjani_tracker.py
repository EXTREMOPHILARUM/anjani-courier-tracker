#!/usr/bin/env python3
"""
Anjani Courier Package Tracker
Tracks packages on https://trackcourier.io/anjani-courier-tracking
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sys
import json


class AnjaniTracker:
    """Tracker for Anjani Courier packages"""

    BASE_URL = "https://trackcourier.io/track-and-trace/anjani-courier"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def track(self, tracking_number):
        """
        Track a package by tracking number

        Args:
            tracking_number: The tracking ID to look up

        Returns:
            dict: Tracking information including status and checkpoints
        """
        url = f"{self.BASE_URL}/{tracking_number}"

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract tracking information
            tracking_info = {
                'tracking_number': tracking_number,
                'courier': 'Anjani Courier',
                'status': None,
                'checkpoints': [],
                'url': url,
                'fetched_at': datetime.now().isoformat()
            }

            # Get status from the page
            # The status is typically in a div or section with specific classes
            # Looking for "IN TRANSIT", "DELIVERED", etc.
            page_text = soup.get_text()

            # Try to find status indicators
            if 'IN TRANSIT' in page_text.upper() or 'IN-TRANSIT' in page_text.upper():
                tracking_info['status'] = 'IN TRANSIT'
            elif 'DELIVERED' in page_text.upper():
                tracking_info['status'] = 'DELIVERED'
            elif 'PENDING' in page_text.upper():
                tracking_info['status'] = 'PENDING'
            elif 'OUT FOR DELIVERY' in page_text.upper():
                tracking_info['status'] = 'OUT FOR DELIVERY'

            # Extract checkpoint data from the timeline
            # Checkpoints usually have date, time, location, and activity

            # Look for table rows or divs containing checkpoint data
            # The format appears to be: Date | Activity | Location

            # Try multiple selectors to find checkpoint information
            checkpoint_elements = (
                soup.find_all('div', class_='checkpoint') or
                soup.find_all('tr', class_='checkpoint') or
                soup.find_all('div', recursive=True)
            )

            # Parse checkpoints from the visible text structure
            # Based on the screenshot, checkpoints appear in a specific format
            lines = page_text.split('\n')
            current_checkpoint = {}

            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue

                # Look for date patterns (DD-MMM-YYYY)
                if '-' in line and any(month in line for month in
                    ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):

                    # Check if this line contains time (HH:MM AM/PM)
                    if 'AM' in line or 'PM' in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            current_checkpoint = {
                                'date': parts[0],
                                'time': ' '.join(parts[1:3]) if len(parts) >= 3 else parts[1],
                                'activity': ' '.join(parts[3:]) if len(parts) > 3 else '',
                                'location': ''
                            }
                    else:
                        current_checkpoint = {
                            'date': line.split()[0] if line.split() else line,
                            'time': '',
                            'activity': ' '.join(line.split()[1:]) if len(line.split()) > 1 else '',
                            'location': ''
                        }

                    # Look ahead for location in next lines
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line and 'Anjani Courier' in next_line:
                            current_checkpoint['activity'] = next_line
                        if i + 2 < len(lines):
                            location_line = lines[i + 2].strip()
                            if location_line and location_line not in ['Anjani Courier', '']:
                                current_checkpoint['location'] = location_line

                    if current_checkpoint.get('date'):
                        tracking_info['checkpoints'].append(current_checkpoint.copy())

            return tracking_info

        except requests.RequestException as e:
            return {
                'error': f'Failed to fetch tracking data: {str(e)}',
                'tracking_number': tracking_number
            }
        except Exception as e:
            return {
                'error': f'Failed to parse tracking data: {str(e)}',
                'tracking_number': tracking_number
            }

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
        if 'error' in tracking_info:
            print(f"❌ Error: {tracking_info['error']}")
            return

        print("\n" + "="*60)
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
            print("-" * 60)

            for i, checkpoint in enumerate(tracking_info['checkpoints'], 1):
                print(f"\n[{i}] {checkpoint.get('date', 'N/A')}", end='')
                if checkpoint.get('time'):
                    print(f" at {checkpoint['time']}", end='')
                print()

                if checkpoint.get('activity'):
                    print(f"    Activity: {checkpoint['activity']}")
                if checkpoint.get('location'):
                    print(f"    Location: {checkpoint['location']}")
        else:
            print("\n⚠️  No tracking checkpoints found")

        print("="*60 + "\n")


def main():
    """Main function for CLI usage"""
    if len(sys.argv) < 2:
        print("Usage: python3 anjani_tracker.py <tracking_number> [tracking_number2 ...]")
        print("Example: python3 anjani_tracker.py 1566745519")
        sys.exit(1)

    tracking_numbers = sys.argv[1:]
    tracker = AnjaniTracker()

    print(f"\n🔍 Tracking {len(tracking_numbers)} package(s)...\n")

    for tracking_number in tracking_numbers:
        tracking_info = tracker.track(tracking_number)
        tracker.print_tracking_info(tracking_info)

        # Optional: Save to JSON file
        # with open(f'tracking_{tracking_number}.json', 'w') as f:
        #     json.dump(tracking_info, f, indent=2)


if __name__ == "__main__":
    main()
