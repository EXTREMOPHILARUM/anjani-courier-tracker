# Google Chat Integration Guide

This guide explains how to set up and use Google Chat webhooks to receive Anjani Courier tracking notifications.

## What You'll Get

When you track a package, you'll receive formatted notifications in Google Chat with:
- 📦 Tracking number
- 🚛 Current status (IN TRANSIT, DELIVERED, etc.)
- 📅 Latest update date and time
- 📝 Latest activity description
- 📍 Location (if available)
- 🔗 Direct link to full tracking page

## Setup Instructions

### Step 1: Create a Google Chat Webhook

1. **Open Google Chat** (chat.google.com or the mobile app)
2. **Navigate to a space** where you want to receive tracking notifications
   - You can create a new space specifically for package tracking
3. **Click on the space name** at the top of the conversation
4. Select **"Apps & integrations"** from the dropdown
5. Click **"Add webhooks"**
6. Give your webhook a name (e.g., "Anjani Package Tracker")
7. Optionally add an avatar URL or use the default
8. Click **"Save"**
9. **Copy the webhook URL** - it will look like:
   ```
   https://chat.googleapis.com/v1/spaces/XXXXX/messages?key=XXXXX&token=XXXXX
   ```

### Step 2: Use the Webhook

You have three options:

#### Option A: Command Line

```bash
uv run python3 anjani_tracker_final.py 1566745519 --webhook="YOUR_WEBHOOK_URL"
```

#### Option B: Environment Variable

Set the webhook URL as an environment variable:

```bash
export GOOGLE_CHAT_WEBHOOK="YOUR_WEBHOOK_URL"
uv run python3 google_chat_example.py
```

#### Option C: Python Code

```python
from anjani_tracker_final import AnjaniTracker

tracker = AnjaniTracker(headless=True)
tracking_info = tracker.track('1566745519')

webhook_url = "YOUR_WEBHOOK_URL"
tracker.send_to_google_chat(tracking_info, webhook_url)
```

## Usage Examples

### Track Single Package

```bash
uv run python3 anjani_tracker_final.py 1566745519 --webhook="YOUR_WEBHOOK_URL"
```

### Track Multiple Packages

```bash
uv run python3 anjani_tracker_final.py 1566745519 1234567890 --webhook="YOUR_WEBHOOK_URL"
```

### Track and Save to JSON

```bash
uv run python3 anjani_tracker_final.py 1566745519 --webhook="YOUR_WEBHOOK_URL" --save-json
```

### Automated Monitoring Script

Create a script to check packages periodically:

```python
#!/usr/bin/env python3
import time
from anjani_tracker_final import AnjaniTracker

# Your packages to monitor
PACKAGES = ["1566745519", "1234567890"]
WEBHOOK_URL = "YOUR_WEBHOOK_URL"

# Check every 30 minutes
CHECK_INTERVAL = 30 * 60

tracker = AnjaniTracker(headless=True)

while True:
    for tracking_number in PACKAGES:
        tracking_info = tracker.track(tracking_number)
        if not tracking_info.get('error'):
            tracker.send_to_google_chat(tracking_info, WEBHOOK_URL)

    print(f"Waiting {CHECK_INTERVAL/60} minutes before next check...")
    time.sleep(CHECK_INTERVAL)
```

## Message Format

The notification sent to Google Chat will look like:

```
*📦 Package Update - 1566745519*
🚛 *Status:* IN TRANSIT
🚚 *Courier:* Anjani Courier

*Latest Update:*
📅 29-Jan-2026 11:26 AM
📝 IN Anjani Courier
📍 BANDRA-EAST

🔗 View Full Tracking
```

## Troubleshooting

### "Failed to send to Google Chat: 400"
- Check that your webhook URL is correct and complete
- Make sure the webhook hasn't been deleted from Google Chat

### "Failed to send to Google Chat: 404"
- The webhook may have been deleted
- Create a new webhook and update your URL

### "Error sending to Google Chat: Connection timeout"
- Check your internet connection
- Google Chat services might be temporarily unavailable

### No notification received
- Check that you're looking at the correct Google Chat space
- Verify the webhook URL is correct
- Check the command output for error messages

## Security Notes

- **Keep your webhook URL private** - anyone with the URL can send messages to your Google Chat space
- Store webhook URLs in environment variables or secure configuration files
- Don't commit webhook URLs to version control (git)
- Consider using different webhooks for different purposes

## Advanced: Customizing Messages

You can customize the message format by modifying the `send_to_google_chat` method in `anjani_tracker_final.py`:

```python
def send_to_google_chat(self, tracking_info, webhook_url):
    # Customize the message_lines list to change the format
    message_lines = [
        f"Custom message for {tracking_info['tracking_number']}",
        # ... add your custom format
    ]

    payload = {"text": "\n".join(message_lines)}
    # ... rest of the method
```

## Rate Limits

Google Chat webhooks have rate limits:
- 1 message per second per webhook
- If you're tracking many packages, add delays between notifications

## Additional Resources

- [Google Chat Webhook Documentation](https://developers.google.com/chat/how-tos/webhooks)
- [Anjani Courier Tracker README](README.md)
