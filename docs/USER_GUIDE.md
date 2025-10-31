# 📘 User Guide

<div align="center">

**Your Complete Guide to YouTube Automation Suite**

Master both GUI and CLI interfaces with step-by-step instructions!

[🚀 Getting Started](#getting-started) • [🖥️ GUI Guide](#gui-version) • [⌨️ CLI Guide](#cli-version) • [📊 Monitoring](#monitoring--logs)

</div>

---

## Table of Contents

- [Getting Started](#getting-started)
- [GUI Version](#gui-version)
- [CLI Version](#cli-version)
- [Input Files](#input-files)
- [Configuration Options](#configuration-options)
- [Monitoring & Logs](#monitoring--logs)
- [Tips & Tricks](#tips--tricks)

---

## 🚀 Getting Started

### ✅ Pre-flight Checklist

<table>
<tr>
<td width="5%" align="center">1️⃣</td>
<td width="25%"><b>📖 Setup Complete</b></td>
<td>Follow the <a href="SETUP.md">Setup Guide</a> first</td>
</tr>
<tr>
<td width="5%" align="center">2️⃣</td>
<td width="25%"><b>🔑 Credentials Ready</b></td>
<td><code>credentials.json</code> in project root folder</td>
</tr>
<tr>
<td width="5%" align="center">3️⃣</td>
<td width="25%"><b>🔓 Authenticated</b></td>
<td>Run once to generate <code>token.json</code></td>
</tr>
<tr>
<td width="5%" align="center">4️⃣</td>
<td width="25%"><b>📁 Input Files</b></td>
<td>Prepare your files (check <code>examples/</code> folder)</td>
</tr>
</table>

---

---

## 🖥️ GUI Version

### 🚀 Launching the GUI

```bash
python src/youtube_automation_gui.py
```

### 🎨 Interface Overview

<table>
<tr>
<td width="50%" align="center">
<h4>📋 Left Sidebar</h4>
Actions, files, credentials & controls
</td>
<td width="50%" align="center">
<h4>📊 Main Panel</h4>
Stats, progress & activity logs
</td>
</tr>
</table>

#### 📋 Left Sidebar Components:

#### 1. Sidebar (Left)
- **Branding**: Application title and tagline
- **Actions**: Checkboxes for Like, Comment, Subscribe
- **Input Files**: File selection buttons
- **Credentials**: Credentials file selector
- **Controls**: Start/Stop buttons
- **Settings**: Configuration panel access

#### 2. Main Area (Right)
- **Progress Bar**: Shows current automation progress
- **Statistics**: Real-time counters for likes, comments, subscriptions
- **Current Action**: Displays what's currently being processed
- **Activity Log**: Detailed color-coded logs

#### 3. Status Bar (Bottom)
- **Application Status**: Current state
- **Connection Status**: API connection indicator

### Basic Workflow

1. **Select Actions**
   - Check the boxes for desired actions (Like, Comment, Subscribe)
   - You can select multiple actions to run in sequence

2. **Load Input Files**
   - Click "📁 Likes.txt" to select your video URLs file
   - Click "📁 Comments.txt" to select your comments file
   - Click "📁 Channels.txt" to select your channels file
   - For comments: Enter target video URL in the text field

3. **Configure Settings** (Optional)
   - Click "⚙️ Settings" to adjust:
     - Base Delay (seconds between actions)
     - Jitter (random variation)
   - Click "Save Settings"

4. **Start Automation**
   - Click "🚀 Start Automation"
   - Watch real-time progress in the logs
   - View statistics updating live

5. **Stop if Needed**
   - Click "⏹️ Stop" to pause automation
   - Progress is saved - you can resume later

### GUI Features

#### Real-Time Statistics
- **Likes**: Count of videos liked
- **Comments**: Count of comments posted
- **Subscriptions**: Count of channels subscribed
- **Errors**: Any failed operations

#### Activity Log
- **Color-coded messages**:
  - 🟢 Green: Success messages
  - 🔴 Red: Error messages
  - 🟡 Yellow: Warning messages
  - ⚪ White: Info messages
- Timestamps for all actions
- Detailed operation information

#### Settings Panel
- **Base Delay**: Time between each action (default: 4.0 seconds)
- **Jitter**: Random variation (default: 2.0 seconds)
- **Clear Processed State**: Reset tracking to start fresh
- **View Log File**: Open the CSV log file

---

---

## ⌨️ CLI Version

### Basic Usage

```bash
python src/youtube_automation_cli.py [OPTIONS]
```

### Common Commands

#### Like Videos
```bash
# Basic like operation
python src/youtube_automation_cli.py --action like --file likes.txt

# With custom delay
python src/youtube_automation_cli.py --action like --file likes.txt --delay 5.0

# Limit number of actions
python src/youtube_automation_cli.py --action like --file likes.txt --limit 10
```

#### Post Comments
```bash
# Comment on a specific video
python src/youtube_automation_cli.py --action comment --file comments.txt --video VIDEO_ID

# Using video URL
python src/youtube_automation_cli.py --action comment --file comments.txt --video "https://www.youtube.com/watch?v=VIDEO_ID"
```

#### Subscribe to Channels
```bash
# Subscribe to channels from file
python src/youtube_automation_cli.py --action subscribe --file channels.txt
```

### Advanced Options

```bash
python src/youtube_automation_cli.py \
  --action like \
  --file likes.txt \
  --credentials custom_creds.json \
  --token custom_token.json \
  --delay 6.0 \
  --jitter 2.5 \
  --limit 50 \
  --log-level DEBUG
```

### CLI Options Reference

| Option | Description | Default |
|--------|-------------|---------|
| `--action` | Action to perform: like, comment, subscribe | Required |
| `--file` | Input file path | Required |
| `--video` | Target video ID/URL (for comments) | Required for comments |
| `--credentials` | Path to credentials.json | `credentials.json` |
| `--token` | Path to token.json | `token.json` |
| `--delay` | Base delay between actions (seconds) | `4.0` |
| `--jitter` | Random jitter (seconds) | `2.0` |
| `--limit` | Maximum actions to perform | Unlimited |
| `--log-level` | Logging level: DEBUG, INFO, WARNING, ERROR | `INFO` |

---

## Input Files

### Likes File Format

**File: `likes.txt`**

```text
# YouTube video URLs or IDs (one per line)
# Lines starting with # are comments

https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://youtu.be/9bZkp7q19f0
VIDEO_ID_ONLY
https://www.youtube.com/watch?v=JGwWNGJdvx8

# All these formats are supported:
# - Full URL: https://www.youtube.com/watch?v=VIDEO_ID
# - Short URL: https://youtu.be/VIDEO_ID
# - Video ID only: VIDEO_ID
```

### Comments File Format

**File: `comments.txt`**

```text
Great video! Really enjoyed the content.
Very informative, thank you for sharing.
This tutorial helped me a lot!
Amazing work, keep it up!
Looking forward to more content like this.

# Tips:
# - Keep comments relevant and genuine
# - Vary your comments to appear natural
# - Avoid spammy or repetitive messages
# - Each line is a separate comment
```

### Channels File Format

**File: `channels.txt`**

```text
# Channel URLs, IDs, or handles (one per line)

https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw
@YouTubeHandle
UC_CHANNEL_ID
https://www.youtube.com/c/CustomChannelName

# Supported formats:
# - Full channel URL: https://www.youtube.com/channel/UC_ID
# - Custom URL: https://www.youtube.com/c/CustomName
# - Handle: @Username
# - Channel ID: UC_CHANNEL_ID
```

### Best Practices for Input Files

1. **One Item Per Line**: Each URL, ID, or comment on a new line
2. **Comments Are Optional**: Lines starting with `#` are ignored
3. **Empty Lines Ignored**: Blank lines are automatically skipped
4. **UTF-8 Encoding**: Save files in UTF-8 to support special characters
5. **No Trailing Spaces**: Trim whitespace for cleaner processing

---

## Configuration Options

### Delay Settings

**Base Delay**: Time between each action
- **Recommended**: 4-6 seconds
- **Minimum**: 2 seconds (risky)
- **Safe Range**: 4-10 seconds

**Jitter**: Random variation added to delay
- **Purpose**: Makes automation appear more human
- **Recommended**: 1-3 seconds
- **Formula**: Actual delay = Base Delay ± Random(0 to Jitter)

**Example:**
```
Base Delay: 5.0 seconds
Jitter: 2.0 seconds
Actual delays: 3.0s, 6.5s, 4.2s, 7.0s, etc.
```

### Retry Configuration

The tool automatically handles errors with exponential backoff:

- **Max Retries**: 4 attempts (configurable in code)
- **Backoff Strategy**: Exponential (1s, 2s, 4s, 8s)
- **Handled Errors**:
  - HTTP 429 (Too Many Requests)
  - HTTP 403 (Forbidden)
  - HTTP 5xx (Server Errors)

---

## Monitoring & Logs

### Activity Logs

**Real-time Monitoring** (GUI):
- Watch the Activity Log panel
- Color-coded messages
- Timestamps for all events
- Scroll automatically follows latest entries

**CSV Log File**: `Logs.csv`
```csv
timestamp,action,target_id,status,note
2025-01-31 10:30:15,like,VIDEO_ID,success,
2025-01-31 10:30:20,comment,VIDEO_ID,success,COMMENT_ID
2025-01-31 10:30:25,subscribe,CHANNEL_ID,success,SUB_ID
```

### Processed State Tracking

**Location**: `processed_state/` directory

Files:
- `processed_like.json`: Tracks liked videos
- `processed_comment.json`: Tracks posted comments
- `processed_subscribe.json`: Tracks subscribed channels

**Purpose**: Prevents duplicate actions when resuming

**To Reset**:
```bash
# Delete processed state
# macOS/Linux:
rm -rf processed_state/

# Windows (Command Prompt):
rmdir /s /q processed_state

# Windows (PowerShell):
Remove-Item -Recurse -Force processed_state

# Or use GUI Settings > Clear Processed State
```

---

## Tips & Tricks

### Efficiency Tips

1. **Start Small**: Test with 5-10 items first
2. **Use Appropriate Delays**: Faster isn't better - avoid rate limits
3. **Monitor Quotas**: Check Google Cloud Console regularly
4. **Save Progress**: Use processed state to resume safely
5. **Batch Processing**: Split large jobs into smaller batches

### Safety Tips

1. **Respect Rate Limits**: Don't exceed YouTube API quotas
2. **Natural Behavior**: Use jitter to randomize timing
3. **Quality Over Quantity**: Post genuine, relevant comments
4. **Own Accounts Only**: Only automate accounts you control
5. **Monitor Results**: Check YouTube Studio to verify actions

### Optimization Tips

1. **Parallel Sessions**: Run multiple accounts separately (different credentials)
2. **Off-Peak Hours**: Lower API usage during off-peak times
3. **Regular Backups**: Save your configuration and processed state
4. **Clean Input Files**: Remove invalid URLs before processing
5. **Log Analysis**: Review logs to identify patterns or issues

### Troubleshooting Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| Authentication Error | Delete `token.json` and re-authenticate |
| Duplicate Actions | Don't delete `processed_state/` folder |
| API Quota Exceeded | Wait 24 hours or request increase |
| GUI Not Responding | Use CLI version instead |
| Slow Performance | Increase delay, decrease jitter |

---

## Examples

### Example 1: Like 50 Videos Safely

```bash
python src/youtube_automation_cli.py \
  --action like \
  --file my_likes.txt \
  --delay 6.0 \
  --jitter 2.0 \
  --limit 50
```

### Example 2: Post Comments on Tutorial Video

```bash
python src/youtube_automation_cli.py \
  --action comment \
  --file tutorial_comments.txt \
  --video "https://www.youtube.com/watch?v=TUTORIAL_ID" \
  --delay 8.0
```

### Example 3: Subscribe to Educational Channels

```bash
python src/youtube_automation_cli.py \
  --action subscribe \
  --file edu_channels.txt \
  --delay 5.0 \
  --jitter 1.5
```

---

## FAQ

**Q: How many actions can I perform per day?**
A: YouTube API has quotas (default ~10,000 units/day). Each action uses units:
- Like: 50 units
- Comment: 50 units
- Subscribe: 50 units

**Q: Will this get my account banned?**
A: If used responsibly on your own accounts, no. Misuse or spam may violate YouTube TOS.

**Q: Can I run this 24/7?**
A: Not recommended. Use reasonable intervals and respect API quotas.

**Q: How do I stop a running automation?**
A: Click "Stop" button (GUI) or press Ctrl+C (CLI)

**Q: Can I undo actions?**
A: No. The tool performs real YouTube actions that cannot be automatically reversed.

---

<div align="center">

**Need More Help?**

[Setup Guide](SETUP.md) • [API Reference](API.md) • [Best Practices](BEST_PRACTICES.md)

**Contact**: haseebkaloya@gmail.com

[⬆ Back to Top](#user-guide---youtube-automation-suite)

</div>
