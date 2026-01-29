# Quick Start Guide

Get automated package tracking with Google Chat notifications in 5 minutes!

## Option 1: GitHub Actions (Recommended)

Fully automated - runs every 30 minutes, notifies only on changes.

### Step 1: Get Google Chat Webhook

1. Open Google Chat → Create/Select a space
2. Space name → **Apps & integrations** → **Add webhooks**
3. Name it "Package Tracker" and copy the URL

### Step 2: Push to GitHub

```bash
git init
git add .
git commit -m "Setup package tracking"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 3: Add GitHub Secrets

Go to your repo → **Settings** → **Secrets and variables** → **Actions**

**Secret 1: GOOGLE_CHAT_WEBHOOK**
1. Click **New repository secret**
2. Name: `GOOGLE_CHAT_WEBHOOK`
3. Value: Your webhook URL (from Step 1)
4. Click **Add secret**

**Secret 2: TRACKING_IDS**
1. Click **New repository secret**
2. Name: `TRACKING_IDS`
3. Value: Your tracking numbers (comma-separated)
   ```
   1566745519,1234567890,9876543210
   ```
4. Click **Add secret**

### Step 4: Test It!

1. Go to **Actions** tab
2. Click **Monitor Packages**
3. Click **Run workflow** → **Run workflow**

✅ You should receive a notification in Google Chat within 2-3 minutes!

**That's it!** The workflow now runs automatically every 30 minutes.

---

## Option 2: Local Monitoring

Run on your computer or server with cron.

### Step 1: Install Dependencies

```bash
uv pip install -r requirements.txt
uv run playwright install chromium
```

### Step 2: Set Environment Variables

```bash
export GOOGLE_CHAT_WEBHOOK="YOUR_WEBHOOK_URL"
export TRACKING_IDS="1566745519,1234567890,9876543210"
```

Or create a `.env` file:
```bash
echo 'export GOOGLE_CHAT_WEBHOOK="YOUR_WEBHOOK_URL"' > .env
echo 'export TRACKING_IDS="1566745519,1234567890"' >> .env
source .env
```

### Step 3: Run Monitor

```bash
uv run python3 monitor_packages.py
```

### Step 4: Schedule with Cron (Optional)

```bash
crontab -e
```

Add this line to run every 30 minutes:
```
*/30 * * * * cd /path/to/anjani-courier-tracker && source /path/to/.env && /path/to/uv run python3 monitor_packages.py
```

---

## Option 3: One-Time Tracking

Quick package check without automation.

```bash
# Install dependencies
uv pip install -r requirements.txt
uv run playwright install chromium

# Track a package
uv run python3 anjani_tracker_final.py 1566745519

# With Google Chat notification
uv run python3 anjani_tracker_final.py 1566745519 --webhook="YOUR_WEBHOOK_URL"
```

---

## What Happens Next?

### With Automated Monitoring:
- ✅ Checks packages every 30 minutes
- 🔔 Notifies you **only when something changes**:
  - Status updates (e.g., IN TRANSIT → DELIVERED)
  - New tracking checkpoints
  - Location changes
- 💾 Saves state to `tracking_state.json`
- 🔇 No spam - silent if nothing changed

### Notification Example:

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

---

## Customization

### Change Schedule (GitHub Actions)

Edit `.github/workflows/monitor-packages.yml`:

```yaml
schedule:
  - cron: '0 * * * *'  # Every hour
  - cron: '0 */2 * * *'  # Every 2 hours
  - cron: '*/15 * * * *'  # Every 15 minutes
```

### Add More Packages

Update your GitHub Secret:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click on **TRACKING_IDS**
3. Click **Update secret**
4. Update value with new tracking numbers:
   ```
   1566745519,1234567890,9876543210,5555555555
   ```
5. Save

The next scheduled run will pick up the changes automatically!

---

## Troubleshooting

### No notifications received?
1. Check webhook URL is correct
2. Check GitHub Actions logs (Actions tab)
3. Verify packages have actually changed

### Workflow not running?
1. Check Actions are enabled: Settings → Actions → Allow all actions
2. Manually trigger from Actions tab to test

### Need help?
See detailed guides:
- [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) - Complete GitHub Actions guide
- [GOOGLE_CHAT_SETUP.md](GOOGLE_CHAT_SETUP.md) - Google Chat webhook guide

---

## Pro Tips

1. **Use separate Google Chat spaces** for different types of packages
2. **Test with manual trigger** before waiting for scheduled runs
3. **Check logs regularly** for any errors
4. **Add delays** if tracking many packages (avoid rate limits)
5. **Review `tracking_state.json`** to see what's being tracked

Enjoy automated package tracking! 📦✨
