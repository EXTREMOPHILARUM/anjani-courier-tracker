#!/usr/bin/env python3
"""
Example usage of the Anjani Courier Tracker
"""

from anjani_tracker_final import AnjaniTracker
import json

def main():
    # Create tracker instance
    print("Creating tracker...")
    tracker = AnjaniTracker(headless=True)

    # Example 1: Track a single package
    print("\n" + "="*70)
    print("Example 1: Track a single package")
    print("="*70)

    tracking_number = "1566745519"
    tracking_info = tracker.track(tracking_number)

    # Print formatted output
    tracker.print_tracking_info(tracking_info)

    # Example 2: Track multiple packages
    print("\n" + "="*70)
    print("Example 2: Track multiple packages")
    print("="*70)

    tracking_numbers = ["1566745519"]  # Add more tracking numbers here
    results = tracker.track_multiple(tracking_numbers)

    for result in results:
        tracker.print_tracking_info(result)

    # Example 3: Access data programmatically
    print("\n" + "="*70)
    print("Example 3: Access data programmatically")
    print("="*70)

    tracking_info = tracker.track("1566745519")

    print(f"Tracking Number: {tracking_info['tracking_number']}")
    print(f"Status: {tracking_info['status']}")
    print(f"Number of checkpoints: {len(tracking_info['checkpoints'])}")

    print("\nCheckpoints:")
    for i, checkpoint in enumerate(tracking_info['checkpoints'], 1):
        print(f"  {i}. {checkpoint['date']} {checkpoint['time']}")
        print(f"     {checkpoint['activity']}")
        if checkpoint['location']:
            print(f"     Location: {checkpoint['location']}")

    # Example 4: Save to JSON
    print("\n" + "="*70)
    print("Example 4: Save tracking data")
    print("="*70)

    # Save to JSON file
    tracker.save_to_json(tracking_info, "my_package_tracking.json")

    # Or work with the data as a dictionary
    json_str = json.dumps(tracking_info, indent=2)
    print("\nJSON data:")
    print(json_str)

    # Example 5: Check for errors
    print("\n" + "="*70)
    print("Example 5: Error handling")
    print("="*70)

    invalid_tracking = tracker.track("0000000000")
    if invalid_tracking.get('error'):
        print(f"Error occurred: {invalid_tracking['error']}")
    elif not invalid_tracking.get('checkpoints'):
        print("No tracking information available for this number")

    # Example 6: Send to Google Chat webhook
    print("\n" + "="*70)
    print("Example 6: Send to Google Chat")
    print("="*70)

    # Replace with your actual Google Chat webhook URL
    webhook_url = "https://chat.googleapis.com/v1/spaces/XXXXX/messages?key=XXXXX&token=XXXXX"

    # Uncomment to send notification
    # tracking_info = tracker.track("1566745519")
    # tracker.send_to_google_chat(tracking_info, webhook_url)
    print("Set your webhook URL and uncomment the code above to send notifications")


if __name__ == "__main__":
    main()
