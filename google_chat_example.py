#!/usr/bin/env python3
"""
Example: Sending Anjani Courier tracking updates to Google Chat
"""

from anjani_tracker_final import AnjaniTracker
import os

def main():
    # Get webhook URL from environment variable or replace with your actual webhook URL
    webhook_url = os.environ.get('GOOGLE_CHAT_WEBHOOK')

    if not webhook_url:
        print("❌ Please set GOOGLE_CHAT_WEBHOOK environment variable or edit this script")
        print("\nTo get your webhook URL:")
        print("1. Open Google Chat and go to your space")
        print("2. Click space name → Apps & integrations → Add webhooks")
        print("3. Name it 'Package Tracker' and copy the URL")
        print("\nThen run:")
        print("export GOOGLE_CHAT_WEBHOOK='your-webhook-url-here'")
        return

    # Create tracker
    tracker = AnjaniTracker(headless=True)

    # Example 1: Track single package and send to Google Chat
    print("="*70)
    print("Tracking package and sending to Google Chat...")
    print("="*70)

    tracking_number = "1566745519"
    tracking_info = tracker.track(tracking_number)

    # Display locally
    tracker.print_tracking_info(tracking_info)

    # Send to Google Chat
    if not tracking_info.get('error'):
        success = tracker.send_to_google_chat(tracking_info, webhook_url)
        if success:
            print("✅ Notification sent successfully!")
        else:
            print("❌ Failed to send notification")
    else:
        print(f"❌ Tracking error: {tracking_info['error']}")

    # Example 2: Monitor multiple packages
    print("\n" + "="*70)
    print("Tracking multiple packages...")
    print("="*70)

    tracking_numbers = ["1566745519"]  # Add more tracking numbers here

    for tracking_number in tracking_numbers:
        tracking_info = tracker.track(tracking_number)

        # Only send notification if tracking was successful
        if not tracking_info.get('error') and tracking_info.get('checkpoints'):
            tracker.send_to_google_chat(tracking_info, webhook_url)

    print("\n✅ All notifications sent!")


if __name__ == "__main__":
    main()
