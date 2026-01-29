#!/usr/bin/env python3
"""
Automated Package Monitoring Script
Tracks packages and sends Google Chat notifications only when changes are detected
Designed to run via GitHub Actions or cron jobs
"""

from tracker import AnjaniTracker
import json
import os
import sys
from datetime import datetime


def get_tracking_ids(state_file='tracking_state.json'):
    """
    Get tracking IDs from state file

    The state file contains all tracking IDs as top-level keys.
    To add a new tracking ID, add it to the state file with an empty object:
    {
      "existing_id": { ... },
      "new_tracking_id": {}
    }
    """
    try:
        with open(state_file, 'r') as f:
            state = json.load(f)
            tracking_ids = list(state.keys())

            if not tracking_ids:
                print("⚠️  No tracking IDs in state file")
                print(f"Add tracking IDs to {state_file}:")
                print('{"1566745519": {}, "1234567890": {}}')
                sys.exit(1)

            return tracking_ids
    except FileNotFoundError:
        print(f"⚠️  State file not found: {state_file}")
        print("Creating initial state file...")
        print("Add your tracking IDs as keys:")
        print('{"1566745519": {}, "1234567890": {}}')

        # Create empty state file
        with open(state_file, 'w') as f:
            json.dump({}, f, indent=2)

        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in {state_file}")
        sys.exit(1)


def main():
    print("="*70)
    print("🔍 Anjani Courier - Automated Package Monitor")
    print(f"🕐 Run started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    # Get webhook URL from environment variable
    webhook_url = os.environ.get('GOOGLE_CHAT_WEBHOOK')

    if not webhook_url:
        print("❌ No webhook URL provided")
        print("Set GOOGLE_CHAT_WEBHOOK environment variable")
        sys.exit(1)

    # Load previous state and get tracking IDs from it
    state_file = 'tracking_state.json'
    previous_state = AnjaniTracker.load_state(state_file)
    tracking_ids = get_tracking_ids(state_file)

    if not tracking_ids:
        print("❌ No tracking IDs provided in config file")
        sys.exit(1)

    print(f"\n📦 Monitoring {len(tracking_ids)} package(s)")
    print(f"💬 Webhook configured: {webhook_url[:50]}...")
    print(f"📂 Loaded previous state: {len(previous_state)} tracked package(s)")

    # Initialize tracker
    tracker = AnjaniTracker(headless=True)

    # Track all packages and detect changes
    new_state = {}
    notifications_sent = 0
    errors = 0

    for tracking_id in tracking_ids:
        print(f"\n{'─'*70}")
        print(f"🔍 Checking: {tracking_id}")

        try:
            # Get current tracking info
            tracking_info = tracker.track(tracking_id)

            if tracking_info.get('error'):
                print(f"❌ Error tracking {tracking_id}: {tracking_info['error']}")
                errors += 1
                # Keep old state if tracking fails
                if tracking_id in previous_state:
                    new_state[tracking_id] = previous_state[tracking_id]
                continue

            # Check for changes
            if tracking_id in previous_state:
                has_changes, change_list = AnjaniTracker.has_changes(
                    previous_state[tracking_id],
                    tracking_info
                )

                if has_changes:
                    print(f"🔔 Changes detected:")
                    for change in change_list:
                        print(f"   • {change}")

                    # Send notification
                    success = tracker.send_to_google_chat(tracking_info, webhook_url)
                    if success:
                        notifications_sent += 1
                else:
                    print(f"✓ No changes detected")
            else:
                # First time tracking this package
                print(f"🆕 First time tracking this package")
                print(f"📊 Status: {tracking_info.get('status', 'Unknown')}")
                print(f"📋 Checkpoints: {len(tracking_info.get('checkpoints', []))}")

                # Send initial notification
                success = tracker.send_to_google_chat(tracking_info, webhook_url)
                if success:
                    notifications_sent += 1

            # Save to new state
            new_state[tracking_id] = tracking_info

        except Exception as e:
            print(f"❌ Unexpected error processing {tracking_id}: {str(e)}")
            errors += 1
            # Keep old state if error occurs
            if tracking_id in previous_state:
                new_state[tracking_id] = previous_state[tracking_id]

    # Save updated state
    AnjaniTracker.save_state(new_state, state_file)
    print(f"\n{'─'*70}")
    print(f"💾 Saved state to: {state_file}")

    # Summary
    print("\n" + "="*70)
    print("📊 Summary:")
    print(f"   • Packages checked: {len(tracking_ids)}")
    print(f"   • Notifications sent: {notifications_sent}")
    print(f"   • Errors: {errors}")
    print(f"   • Run completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    # Exit with error code only if ALL packages failed
    if errors > 0 and notifications_sent == 0 and len(new_state) == 0:
        print("\n❌ All packages failed to track")
        sys.exit(1)
    elif errors > 0:
        print(f"\n⚠️  Some packages had errors, but {notifications_sent} succeeded")
        sys.exit(0)  # Success despite some errors


if __name__ == "__main__":
    main()
