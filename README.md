# Anjani Courier Package Tracker

Automated package tracking with Google Chat notifications. Runs on GitHub Actions every 30 minutes and notifies you **only when something changes**.

## Features

- 🤖 **Automated monitoring** via GitHub Actions
- 🔔 **Smart notifications** - only on status changes, new checkpoints, or updates
- 💬 **Google Chat integration**
- 📊 **State tracking** - no duplicate notifications
- ⚙️ **Simple configuration** - just one secret, tracking IDs in JSON file

## Quick Setup

### 1. Get Google Chat Webhook

1. Open Google Chat → Go to a space
2. Click space name → **Apps & integrations** → **Add webhooks**
3. Name it "Package Tracker" and copy the webhook URL

### 2. Fork/Clone and Push to GitHub

```bash
git clone https://github.com/EXTREMOPHILARUM/anjani-courier-tracker.git
cd anjani-courier-tracker

# Push to your own repository
git remote set-url origin https://github.com/YOUR_USERNAME/anjani-courier-tracker.git
git push
```

### 3. Add GitHub Secret

1. Go to your repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `GOOGLE_CHAT_WEBHOOK`
4. Value: Your webhook URL from step 1
5. Click **Add secret**

### 4. Add Your Tracking Numbers

Edit `tracking_state.json` and add your tracking IDs as keys:

```json
{
  "1566745519": {},
  "1234567890": {},
  "YOUR_TRACKING_ID": {}
}
```

Commit and push:

```bash
git add tracking_state.json
git commit -m "Add my tracking numbers"
git push
```

### 5. Done! ✨

The workflow runs automatically every 30 minutes. You'll get notifications in Google Chat when packages update.

## How It Works

### Automated Monitoring

- ⏰ **Runs every 30 minutes** via GitHub Actions
- 📦 **Tracks all packages** in `tracking_state.json`
- 🔍 **Compares with previous state** to detect changes
- 🔔 **Sends notifications** only when:
  - Status changes (e.g., IN TRANSIT → DELIVERED)
  - New tracking checkpoints appear
  - Location updates
  - First time tracking a package
- 💾 **Saves new state** automatically

### State File

The `tracking_state.json` file serves two purposes:

1. **Configuration** - Lists which packages to track (as keys)
2. **State storage** - Stores last known state to detect changes

**To add a new package:**
```json
{
  "existing_package": { ... existing data ... },
  "NEW_TRACKING_ID": {}
}
```

**To remove a package:**
Simply delete its key from the JSON file.

## Manual Run

Test anytime from the Actions tab:

1. Go to your repo → **Actions**
2. Click **Monitor Packages**
3. Click **Run workflow** → **Run workflow**

## Local Testing

```bash
# Install dependencies
uv pip install -r requirements.txt
uv run playwright install chromium

# Set webhook
export GOOGLE_CHAT_WEBHOOK="your_webhook_url"

# Run monitor
uv run python3 monitor.py
```

## One-Time Tracking (No Automation)

Track a package once without setting up automation:

```bash
uv pip install -r requirements.txt
uv run playwright install chromium

# Basic tracking
uv run python3 tracker.py 1566745519

# With Google Chat notification
uv run python3 tracker.py 1566745519 --webhook="YOUR_WEBHOOK_URL"

# Save to JSON file
uv run python3 tracker.py 1566745519 --save-json

# Show browser (for debugging)
uv run python3 tracker.py 1566745519 --show-browser
```

## Customization

### Change Schedule

Edit `.github/workflows/monitor-packages.yml`:

```yaml
schedule:
  - cron: '0 * * * *'  # Every hour
  - cron: '0 */2 * * *'  # Every 2 hours
  - cron: '*/15 * * * *'  # Every 15 minutes
```

### Modify Notification Format

Edit the `send_to_google_chat()` method in `tracker.py` to customize message formatting.

## File Structure

```
anjani-courier-tracker/
├── .github/workflows/
│   └── monitor-packages.yml    # GitHub Actions workflow
├── tracker.py                   # Core package tracker
├── monitor.py                   # Automated monitoring script
├── tracking_state.json          # Configuration + state
├── requirements.txt             # Python dependencies
├── .gitignore
└── README.md                    # This file
```

## Notification Example

```
📦 Package Update - 1566745519
✅ Status: DELIVERED
🚚 Courier: Anjani Courier

Latest Update:
📅 29-Jan-2026 2:30 PM
📝 Package delivered successfully
📍 BANDRA-EAST

🔗 View Full Tracking
```

## Troubleshooting

### No notifications received?
- Check the webhook URL is correct in GitHub Secrets
- Verify packages have actually changed since last check
- Check workflow logs in Actions tab

### Workflow failing?
- Go to Actions → Click failed run → View logs
- Common issue: Page timeout (will auto-retry next run)
- Check `tracking_state.json` is valid JSON

### Want to track new package?
- Edit `tracking_state.json`
- Add new tracking ID as a key with empty object `{}`
- Commit and push

## Requirements

- Python 3.12+
- Playwright (for browser automation)
- GitHub Actions (free for public repos)
- Google Chat space with webhook

## License

Free to use for personal package tracking.

## Support

For issues: https://github.com/EXTREMOPHILARUM/anjani-courier-tracker/issues
