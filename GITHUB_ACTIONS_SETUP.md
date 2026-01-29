# GitHub Actions Setup Guide

This guide explains how to set up automated package monitoring using GitHub Actions. The workflow will:
- Run every 30 minutes (or on your custom schedule)
- Track your packages automatically
- Send Google Chat notifications **only when changes are detected**
- Save tracking state to detect future changes

## Prerequisites

- A GitHub repository for this project
- A Google Chat webhook URL
- Package tracking numbers you want to monitor

## Step-by-Step Setup

### 1. Fork or Push This Repository to GitHub

If you haven't already, push this code to a GitHub repository:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 2. Set Up GitHub Secrets

Go to your GitHub repository and add two secrets:

1. Click **Settings** → **Secrets and variables** → **Actions**

**Secret 1: GOOGLE_CHAT_WEBHOOK**
2. Click **New repository secret**
3. Name: `GOOGLE_CHAT_WEBHOOK`
4. Value: Your full Google Chat webhook URL
   ```
   https://chat.googleapis.com/v1/spaces/XXXXX/messages?key=XXXXX&token=XXXXX
   ```
5. Click **Add secret**

**Secret 2: TRACKING_IDS**
6. Click **New repository secret**
7. Name: `TRACKING_IDS`
8. Value: Comma-separated list of tracking numbers
   ```
   1566745519,1234567890,9876543210
   ```
   Or as JSON array:
   ```
   ["1566745519","1234567890","9876543210"]
   ```
9. Click **Add secret**

**That's it!** No config files needed - everything is in secure GitHub Secrets.

### 3. Enable GitHub Actions

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. If prompted, click **"I understand my workflows, go ahead and enable them"**
4. You should see the "Monitor Packages" workflow

### 4. Test the Workflow

You can manually trigger the workflow to test it:

1. Go to **Actions** tab
2. Click **Monitor Packages** workflow
3. Click **Run workflow** dropdown
4. Click the green **Run workflow** button

Watch the workflow run and check for:
- ✅ All steps complete successfully
- 💬 Notifications appear in your Google Chat
- 📂 `tracking_state.json` is updated in your repository

## How It Works

### Workflow Schedule

The workflow runs on the following triggers:

1. **Schedule**: Every 30 minutes (can be customized)
   ```yaml
   schedule:
     - cron: '*/30 * * * *'
   ```

2. **Manual**: You can trigger it manually from the Actions tab

3. **On Push**: Runs when you update config files

### Change Detection

The system only sends notifications when something changes:

- ✅ Status changes (e.g., IN TRANSIT → DELIVERED)
- ✅ New checkpoints added
- ✅ Latest checkpoint details change
- ✅ First time tracking a package

No notifications are sent if nothing has changed since the last check.

### State Persistence

- Current tracking data is saved to `tracking_state.json`
- This file is committed back to the repository after each run
- Future runs compare against this state to detect changes

## Customization

### Change the Schedule

Edit `.github/workflows/monitor-packages.yml`:

```yaml
# Every hour
schedule:
  - cron: '0 * * * *'

# Every 2 hours
schedule:
  - cron: '0 */2 * * *'

# Every day at 9 AM UTC
schedule:
  - cron: '0 9 * * *'

# Every 15 minutes (be careful with rate limits!)
schedule:
  - cron: '*/15 * * * *'
```

**Cron Format:** `minute hour day month weekday`

### Add Multiple Tracking Numbers

Update the `TRACKING_IDS` GitHub Secret:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click on **TRACKING_IDS**
3. Click **Update secret**
4. Update the value:
   ```
   1566745519,1234567890,9876543210,5555555555
   ```
   Or as JSON:
   ```
   ["1566745519","1234567890","9876543210","5555555555"]
   ```
5. Save

The next workflow run will automatically use the updated list.

### Use Multiple Webhooks

For different packages to different Google Chat spaces, modify `monitor_packages.py` to support multiple webhooks, or run separate workflows.

## Monitoring and Logs

### View Workflow Runs

1. Go to **Actions** tab in your repository
2. Click on **Monitor Packages**
3. View recent runs and their status

### Check Logs

1. Click on any workflow run
2. Click on the **monitor** job
3. Expand steps to see detailed logs:
   - Which packages were checked
   - What changes were detected
   - Whether notifications were sent

### Common Log Messages

- `✓ No changes detected` - Package hasn't updated
- `🔔 Changes detected` - Changes found, notification sent
- `🆕 First time tracking` - New package added to monitoring
- `❌ Error tracking` - Problem fetching tracking info

## Troubleshooting

### Workflow Not Running

**Check:**
- Is the repository public or do you have Actions enabled for private repos?
- Go to Settings → Actions → General → ensure workflows are enabled
- Check the Actions tab for any errors

### No Notifications Received

**Check:**
1. Secret is set correctly: Settings → Secrets → `GOOGLE_CHAT_WEBHOOK`
2. Webhook URL is valid and not expired
3. Check workflow logs for error messages
4. Verify there were actual changes to notify about

### "Failed to send to Google Chat: 400"

**Fix:**
- Webhook URL is malformed or incorrect
- Update the `GOOGLE_CHAT_WEBHOOK` secret with the correct URL

### State File Conflicts

If multiple workflows run simultaneously, you might get merge conflicts on `tracking_state.json`.

**Fix:**
- Ensure only one workflow runs at a time
- Don't trigger manual runs while scheduled runs are active

### Rate Limiting

Google Chat webhooks have rate limits (1 message/second).

**Fix:**
- Don't check too many packages too frequently
- Add delays between notifications if needed

## Security Best Practices

### 1. Keep Everything in GitHub Secrets

- ✅ Use GitHub Secrets for `GOOGLE_CHAT_WEBHOOK` and `TRACKING_IDS`
- ✅ No config files means no accidental commits of sensitive data
- ❌ Don't commit `.env` files with sensitive data

### 2. Review Workflow Logs

- Workflow logs are visible to anyone with repository access
- Ensure no sensitive data is printed in logs

### 3. Limit Repository Access

- Only give repository access to trusted users
- Anyone with write access can modify workflows

### 4. Use Dependabot

Enable Dependabot to keep dependencies updated:

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
```

## Advanced: Notifications for Specific Events Only

If you want notifications only for specific events (e.g., delivery only), modify `monitor_packages.py`:

```python
# Only notify on delivery
if tracking_info.get('status') == 'DELIVERED':
    tracker.send_to_google_chat(tracking_info, webhook_url)

# Only notify on new checkpoints, not status changes
has_new_checkpoints = len(new_checkpoints) > len(old_checkpoints)
if has_new_checkpoints:
    tracker.send_to_google_chat(tracking_info, webhook_url)
```

## Cost and Quotas

### GitHub Actions

- Public repositories: **Unlimited free minutes**
- Private repositories: **2,000 free minutes/month** (Pro accounts)

This workflow uses approximately:
- ~2-3 minutes per run
- Running every 30 minutes = 48 runs/day = 96-144 minutes/day
- Approximately 3,000-4,500 minutes/month

For private repos, you may need a paid plan or reduce frequency.

### Google Chat

- Webhook rate limit: **1 message per second**
- No hard quota on total messages
- Best practice: Don't send more than 1 message/second

## Getting Help

If you encounter issues:

1. Check workflow logs in the Actions tab
2. Test the script locally: `python3 monitor_packages.py`
3. Verify your webhook with a manual test:
   ```bash
   curl -X POST -H 'Content-Type: application/json' \
   -d '{"text":"Test message"}' \
   YOUR_WEBHOOK_URL
   ```

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Cron Schedule Examples](https://crontab.guru/)
- [Google Chat Webhooks](https://developers.google.com/chat/how-tos/webhooks)
