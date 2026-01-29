# Anjani Courier Package Tracker

A Python script to track Anjani Courier packages from https://trackcourier.io/anjani-courier-tracking

## Features

- ✅ Track single or multiple packages
- 📊 Get real-time tracking status (IN TRANSIT, DELIVERED, etc.)
- 📋 View complete tracking history with timestamps and locations
- 💾 Save tracking data to JSON files
- 🚀 Fast and automated using Playwright
- 💬 Google Chat webhook notifications
- 🤖 **Automated monitoring with GitHub Actions**
- 🔔 **Smart notifications - only on changes**

## Installation

### 1. Install Dependencies

```bash
# Install required Python packages
uv pip install playwright requests beautifulsoup4 lxml

# Install Chromium browser for Playwright
uv run playwright install chromium
```

### 2. Make Script Executable (Optional)

```bash
chmod +x anjani_tracker_final.py
```

## Usage

### Basic Usage

Track a single package:

```bash
uv run python3 anjani_tracker_final.py 1566745519
```

### Track Multiple Packages

```bash
uv run python3 anjani_tracker_final.py 1566745519 1234567890 9876543210
```

### Save Results to JSON

```bash
uv run python3 anjani_tracker_final.py 1566745519 --save-json
```

This will create a file like `tracking_1566745519_20260129_135324.json` with all tracking data.

### Show Browser Window (for debugging)

```bash
uv run python3 anjani_tracker_final.py 1566745519 --show-browser
```

### Send to Google Chat Webhook

```bash
uv run python3 anjani_tracker_final.py 1566745519 --webhook="https://chat.googleapis.com/v1/spaces/XXXXX/messages?key=XXXXX&token=XXXXX"
```

### Combined Options

```bash
uv run python3 anjani_tracker_final.py 1566745519 --save-json --show-browser --webhook="<your_webhook_url>"
```

## Output Example

```
🔍 Tracking 1 package(s)...

======================================================================
📦 Tracking Number: 1566745519
🚚 Courier: Anjani Courier
🚛 Status: IN TRANSIT
🔗 URL: https://trackcourier.io/track-and-trace/anjani-courier/1566745519
🕐 Fetched: 2026-01-29T13:52:45.753331

📋 Tracking History (2 events):
----------------------------------------------------------------------

[1] 29-Jan-2026
    📝 Activity: ON WAY [IN TRANSIT] Anjani Courier

[2] 29-Jan-2026 at 11:26 AM
    📝 Activity: IN Anjani Courier
    📍 Location: BANDRA-EAST
======================================================================
```

## JSON Output Format

When using `--save-json`, the output file contains:

```json
{
  "tracking_number": "1566745519",
  "courier": "Anjani Courier",
  "status": "IN TRANSIT",
  "url": "https://trackcourier.io/track-and-trace/anjani-courier/1566745519",
  "fetched_at": "2026-01-29T13:52:45.753331",
  "checkpoints": [
    {
      "date": "29-Jan-2026",
      "time": "",
      "activity": "ON WAY [IN TRANSIT] Anjani Courier",
      "location": ""
    },
    {
      "date": "29-Jan-2026",
      "time": "11:26 AM",
      "activity": "IN Anjani Courier",
      "location": "BANDRA-EAST"
    }
  ],
  "error": null
}
```

## 🤖 Automated Monitoring with GitHub Actions

Set up automated package tracking that runs on a schedule and sends notifications **only when changes are detected**!

### Quick Start

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Setup automated monitoring"
   git push
   ```

2. **Add GitHub Secrets:**
   Go to Settings → Secrets → Actions → New secret

   **Secret 1:** `GOOGLE_CHAT_WEBHOOK`
   - Value: Your webhook URL

   **Secret 2:** `TRACKING_IDS`
   - Value: `1566745519,1234567890` (comma-separated)

3. **Done!** The workflow runs every 30 minutes and notifies you of changes.

### How It Works

- 📂 Saves tracking state to `tracking_state.json`
- 🔍 Checks packages on a schedule (default: every 30 minutes)
- 🔔 Sends Google Chat notifications **only when something changes**:
  - Status changes (e.g., IN TRANSIT → DELIVERED)
  - New checkpoints added
  - First time tracking a package
- ⏭️ No spam - skips notification if nothing changed

### Manual Monitoring

You can also run the monitoring script locally:

```bash
# Set environment variables
export GOOGLE_CHAT_WEBHOOK="your_webhook_url"
export TRACKING_IDS="1566745519,1234567890"

# Run monitor
uv run python3 monitor_packages.py
```

**[📖 See GITHUB_ACTIONS_SETUP.md for complete setup guide](GITHUB_ACTIONS_SETUP.md)**

## Google Chat Integration

Send tracking notifications directly to Google Chat! 💬

Quick example:
```bash
uv run python3 anjani_tracker_final.py 1566745519 --webhook="<your_webhook_url>"
```

**[📖 See GOOGLE_CHAT_SETUP.md for complete setup instructions](GOOGLE_CHAT_SETUP.md)**

The notification includes:
- 📦 Tracking number
- 🚛 Current status with emoji
- 📝 Latest tracking activity
- 📍 Location (if available)
- 🔗 Direct link to full tracking

## Using as a Python Module

You can also import and use the tracker in your own Python scripts:

```python
from anjani_tracker_final import AnjaniTracker

# Create tracker instance
tracker = AnjaniTracker(headless=True)

# Track a package
tracking_info = tracker.track('1566745519')

# Print formatted output
tracker.print_tracking_info(tracking_info)

# Save to JSON
tracker.save_to_json(tracking_info)

# Send to Google Chat
webhook_url = "https://chat.googleapis.com/v1/spaces/XXXXX/messages?key=XXXXX&token=XXXXX"
tracker.send_to_google_chat(tracking_info, webhook_url)

# Track multiple packages
results = tracker.track_multiple(['1566745519', '1234567890'])
for result in results:
    tracker.print_tracking_info(result)
```

## Configuration

### Wait Time

The script waits 15 seconds for the page to load dynamic content. This is set in the code as:

```python
page.wait_for_timeout(15000)  # 15 seconds
```

If the site is loading slower, you can increase this value by editing the script.

### Headless Mode

By default, the browser runs in headless mode (no window). To see the browser:

```bash
uv run python3 anjani_tracker_final.py 1566745519 --show-browser
```

Or in code:

```python
tracker = AnjaniTracker(headless=False)
```

## Troubleshooting

### "No tracking checkpoints found"

- The site may need more time to load. Try increasing the wait time in the script.
- Check if the tracking number is valid by visiting the URL manually.
- Use `--show-browser` to see what the browser is displaying.

### "Timeout loading tracking page"

- Your internet connection may be slow.
- The trackcourier.io site may be down or slow.
- Try increasing the timeout value in the code.

### Playwright not installed

```bash
uv run playwright install chromium
```

## Notes

- The site uses dynamic JavaScript to load tracking data, so the script waits 15 seconds for content to appear.
- The script respects the site's loading times and doesn't make excessive requests.
- Tracking data is fetched in real-time from the website.

## Files

### Core Scripts
- `anjani_tracker_final.py` - Main tracker with Google Chat & state tracking (recommended)
- `monitor_packages.py` - Automated monitoring script for scheduled runs
- `anjani_tracker_playwright.py` - Alternative version
- `anjani_tracker.py` - Basic version using requests (may not work due to dynamic content)

### Examples & State
- `example_usage.py` - Example Python usage
- `google_chat_example.py` - Example Google Chat integration
- `tracking_state.json` - State file for change detection (auto-generated)

### Documentation
- `README.md` - This file
- `GOOGLE_CHAT_SETUP.md` - Detailed Google Chat setup guide
- `GITHUB_ACTIONS_SETUP.md` - Complete GitHub Actions setup guide

### GitHub Actions
- `.github/workflows/monitor-packages.yml` - Automated monitoring workflow

### Dependencies
- `requirements.txt` - Python dependencies

## License

Free to use for personal package tracking purposes.
