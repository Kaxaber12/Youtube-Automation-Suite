# API Reference - YouTube Automation Suite

Technical documentation for developers and advanced users.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Core Components](#core-components)
- [API Functions](#api-functions)
- [Configuration](#configuration)
- [Error Handling](#error-handling)
- [Extending the Tool](#extending-the-tool)

---

## Architecture Overview

### Project Structure

```
Youtube-Automation-Suite/
├── .github/                          # GitHub templates & workflows
│   ├── ISSUE_TEMPLATE/
│   └── pull_request_template.md
├── docs/                             # Documentation
│   ├── API.md
│   ├── BEST_PRACTICES.md
│   ├── SETUP.md
│   └── USER_GUIDE.md
├── examples/                         # Example input files
│   ├── likes.txt
│   ├── comments.txt
│   ├── channels.txt
│   └── sample_config.json
├── src/                              # Source code
│   ├── youtube_automation_gui.py     # Main GUI application
│   ├── youtube_automation_cli.py     # Main CLI application
│   ├── __init__.py
│   └── processed_state/              # State tracking (auto-generated)
├── Youtube_Automation.py             # CLI launcher (root level)
├── Youtube_Automation_Gui.py         # GUI launcher (root level)
├── START_GUI.bat                     # Windows GUI launcher
├── START_CLI.bat                     # Windows CLI launcher
├── start_gui.sh                      # Unix/Mac GUI launcher
├── start_cli.sh                      # Unix/Mac CLI launcher
├── README.md                         # Main documentation
├── CHANGELOG.md                      # Version history
├── CODE_OF_CONDUCT.md                # Community guidelines
├── CONTRIBUTING.md                   # Contribution guide
├── LICENSE                           # MIT License
├── requirements.txt                  # Python dependencies
├── credentials.json                  # Google API credentials (user-provided)
├── token.json                        # OAuth token (auto-generated)
└── Logs.csv                          # Activity logs (auto-generated)
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **GUI Framework** | CustomTkinter | Modern dark-themed interface |
| **API Client** | Google API Python Client | YouTube API integration |
| **Authentication** | OAuth 2.0 | Secure Google authentication |
| **CLI Colors** | Colorama | Cross-platform terminal colors |
| **Logging** | Python logging + CSV | Activity tracking |

---

## Core Components

### 1. Authentication Module

**Purpose**: Handle OAuth 2.0 authentication with Google

**Key Functions**:

```python
def load_or_create_credentials(credentials_path, token_path, scopes):
    """
    Load existing OAuth credentials or create new ones.
    
    Args:
        credentials_path (str): Path to credentials.json
        token_path (str): Path to token.json
        scopes (list): OAuth scopes required
    
    Returns:
        Credentials: Google OAuth credentials object
    """
```

**Authentication Flow**:
1. Check for existing `token.json`
2. If valid, use existing credentials
3. If expired, attempt refresh
4. If refresh fails or no token exists, initiate OAuth flow
5. Save new token to `token.json`

**Scopes Used**:
```python
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
```

### 2. YouTube Service Builder

**Purpose**: Create authenticated YouTube API service

```python
from googleapiclient.discovery import build

youtube_service = build("youtube", "v3", credentials=creds)
```

**Service Methods Used**:
- `videos().rate()` - Like videos
- `commentThreads().insert()` - Post comments
- `subscriptions().insert()` - Subscribe to channels
- `channels().list()` - Resolve channel information
- `search().list()` - Search for channels

### 3. State Management

**Purpose**: Track processed items to prevent duplicates

**Files**:
- `processed_state/processed_like.json`
- `processed_state/processed_comment.json`
- `processed_state/processed_subscribe.json`

**Functions**:

```python
def save_processed(action, processed_set):
    """
    Save processed items to JSON file.
    
    Args:
        action (str): Action type (like, comment, subscribe)
        processed_set (set): Set of processed item IDs
    """
    
def load_processed(action):
    """
    Load processed items from JSON file.
    
    Args:
        action (str): Action type
    
    Returns:
        set: Set of previously processed item IDs
    """
```

### 4. Retry Logic with Exponential Backoff

**Purpose**: Handle rate limits and transient errors

```python
def with_exponential_backoff(fn, *args, max_retries=4, **kwargs):
    """
    Execute function with exponential backoff retry logic.
    
    Args:
        fn (callable): Function to execute
        max_retries (int): Maximum retry attempts
    
    Returns:
        Result of function call
    
    Raises:
        HttpError: If all retries exhausted
    """
    attempt = 0
    while True:
        try:
            return fn(*args, **kwargs)
        except HttpError as e:
            if should_retry(e) and attempt < max_retries:
                sleep_time = BASE_BACKOFF * (2 ** attempt)
                time.sleep(sleep_time)
                attempt += 1
                continue
            raise
```

**Backoff Schedule**:
- Attempt 1: 1 second
- Attempt 2: 2 seconds
- Attempt 3: 4 seconds
- Attempt 4: 8 seconds

---

## API Functions

### Like Operations

```python
def like_video(youtube, video_id):
    """
    Like a YouTube video.
    
    Args:
        youtube: Authenticated YouTube service
        video_id (str): 11-character video ID
    
    Returns:
        dict: API response
    
    Raises:
        HttpError: API error
    """
    return youtube.videos().rate(
        id=video_id,
        rating="like"
    ).execute()
```

**API Quota Cost**: 50 units per like

**Example Usage**:
```python
youtube = build("youtube", "v3", credentials=creds)
like_video(youtube, "YOUR_VIDEO_ID")
```

### Comment Operations

```python
def post_top_level_comment(youtube, video_id, text):
    """
    Post a top-level comment on a video.
    
    Args:
        youtube: Authenticated YouTube service
        video_id (str): Target video ID
        text (str): Comment text
    
    Returns:
        dict: API response with comment ID
    
    Raises:
        HttpError: API error (e.g., comments disabled)
    """
    body = {
        "snippet": {
            "videoId": video_id,
            "topLevelComment": {
                "snippet": {
                    "textOriginal": text
                }
            }
        }
    }
    return youtube.commentThreads().insert(
        part="snippet",
        body=body
    ).execute()
```

**API Quota Cost**: 50 units per comment

**Response Structure**:
```json
{
  "kind": "youtube#commentThread",
  "id": "COMMENT_THREAD_ID",
  "snippet": {
    "topLevelComment": {
      "id": "COMMENT_ID",
      "snippet": {
        "textDisplay": "Your comment text",
        "authorDisplayName": "Your Name",
        "publishedAt": "2025-01-31T10:30:00Z"
      }
    }
  }
}
```

### Subscribe Operations

```python
def subscribe_channel(youtube, channel_id):
    """
    Subscribe to a YouTube channel.
    
    Args:
        youtube: Authenticated YouTube service
        channel_id (str): Target channel ID (starts with UC)
    
    Returns:
        dict: API response with subscription ID
    
    Raises:
        HttpError: API error
    """
    body = {
        "snippet": {
            "resourceId": {
                "kind": "youtube#channel",
                "channelId": channel_id
            }
        }
    }
    return youtube.subscriptions().insert(
        part="snippet",
        body=body
    ).execute()
```

**API Quota Cost**: 50 units per subscription

### Channel Resolution

```python
def resolve_channel_id(youtube, input_str):
    """
    Resolve various channel identifiers to channel ID.
    
    Supports:
    - Channel URLs: https://www.youtube.com/channel/UC...
    - Custom URLs: https://www.youtube.com/c/CustomName
    - Handles: @username
    - Direct IDs: UC...
    
    Args:
        youtube: Authenticated YouTube service
        input_str (str): Channel identifier
    
    Returns:
        str: Channel ID or None if not found
    """
    # Implementation includes:
    # 1. Regex extraction for direct IDs
    # 2. Handle resolution via channels().list(forHandle=...)
    # 3. Fallback to search().list() for custom URLs
```

### Video ID Extraction

```python
def extract_video_id_from_url(url):
    """
    Extract video ID from various YouTube URL formats.
    
    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - VIDEO_ID (direct)
    - https://www.youtube.com/embed/VIDEO_ID
    
    Args:
        url (str): Video URL or ID
    
    Returns:
        str: 11-character video ID or None
    """
```

---

## Configuration

### Constants

```python
# API Configuration
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
DEFAULT_CREDENTIALS = "credentials.json"
DEFAULT_TOKEN = "token.json"

# File Paths
LOG_CSV = "Logs.csv"
PROCESSED_DIR = "processed_state"

# Timing Configuration
DELAY_SECONDS = 4.0    # Base delay between actions
JITTER = 2.0           # Random jitter (±seconds)
MAX_RETRIES = 4        # Maximum retry attempts
BASE_BACKOFF = 1.0     # Initial backoff time
```

### GUI Configuration

```python
# Appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# Window Size
DEFAULT_WIDTH = 1200
DEFAULT_HEIGHT = 700
MIN_WIDTH = 900
MIN_HEIGHT = 600

# Colors
PRIMARY_COLOR = "#00FF88"
ERROR_COLOR = "#FF4444"
WARNING_COLOR = "#FFAA00"
SUCCESS_COLOR = "#00FF88"
```

---

## Error Handling

### HTTP Error Codes

| Code | Meaning | Handling |
|------|---------|----------|
| **400** | Bad Request | Log error, skip item |
| **401** | Unauthorized | Re-authenticate |
| **403** | Forbidden | Retry with backoff |
| **404** | Not Found | Log error, skip item |
| **429** | Rate Limit | Retry with exponential backoff |
| **500-503** | Server Error | Retry with exponential backoff |

### Error Classes

```python
from googleapiclient.errors import HttpError

try:
    like_video(youtube, video_id)
except HttpError as e:
    status = e.resp.status
    reason = e.reason
    
    if status == 429:
        # Rate limited - wait and retry
        time.sleep(60)
    elif status == 403:
        # Quota exceeded or access denied
        check_quota()
    elif status == 404:
        # Video not found
        log_error(f"Video {video_id} not found")
```

### Logging

**CSV Log Format**:
```csv
timestamp,action,target_id,status,note
2025-01-31 10:30:15,like,VIDEO_ID,success,
2025-01-31 10:30:20,like,INVALID_ID,failed,HTTP 404
2025-01-31 10:30:25,comment,VIDEO_ID,success,COMMENT_ID
```

**Python Logging**:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("Logs.csv"),
        logging.StreamHandler()
    ]
)

logging.info("Operation successful")
logging.warning("Rate limit approaching")
logging.error("API call failed")
```

---

## Extending the Tool

### Adding New Actions

**Step 1**: Define the action function
```python
def dislike_video(youtube, video_id):
    """Dislike a video"""
    return youtube.videos().rate(
        id=video_id,
        rating="dislike"
    ).execute()
```

**Step 2**: Add to action mapping
```python
ACTIONS = {
    "like": like_video,
    "comment": post_top_level_comment,
    "subscribe": subscribe_channel,
    "dislike": dislike_video  # New action
}
```

**Step 3**: Update CLI argument parser
```python
parser.add_argument(
    "--action",
    choices=["like", "comment", "subscribe", "dislike"],
    required=True
)
```

**Step 4**: Add GUI checkbox
```python
self.dislike_var = ctk.BooleanVar()
self.dislike_cb = ctk.CTkCheckBox(
    actions_frame,
    text="👎 Dislike Videos",
    variable=self.dislike_var
)
```

### Custom Processing Logic

```python
def process_with_filter(youtube, items, filter_func, action_func):
    """
    Process items with custom filtering.
    
    Args:
        youtube: YouTube service
        items: List of items to process
        filter_func: Function to filter items
        action_func: Function to execute on each item
    """
    filtered = [item for item in items if filter_func(item)]
    
    for item in filtered:
        try:
            result = action_func(youtube, item)
            logging.info(f"Processed {item}: {result}")
        except Exception as e:
            logging.error(f"Failed to process {item}: {e}")
```

**Example**: Only like videos longer than 10 minutes
```python
def is_long_video(video_id):
    """Check if video is longer than 10 minutes"""
    response = youtube.videos().list(
        part="contentDetails",
        id=video_id
    ).execute()
    
    duration = response["items"][0]["contentDetails"]["duration"]
    # Parse ISO 8601 duration
    return parse_duration(duration) > 600  # 10 minutes

process_with_filter(youtube, video_ids, is_long_video, like_video)
```

### Plugin System (Advanced)

```python
class AutomationPlugin:
    """Base class for automation plugins"""
    
    def __init__(self, youtube_service):
        self.youtube = youtube_service
    
    def execute(self, item):
        """Execute plugin action"""
        raise NotImplementedError
    
    def validate(self, item):
        """Validate item before processing"""
        return True

class SmartCommentPlugin(AutomationPlugin):
    """Plugin to generate contextual comments"""
    
    def execute(self, video_id):
        # Fetch video details
        video_info = self.get_video_info(video_id)
        
        # Generate comment based on video content
        comment = self.generate_comment(video_info)
        
        # Post comment
        return post_top_level_comment(self.youtube, video_id, comment)
```

---

## Performance Optimization

### Batch Operations

```python
def batch_like_videos(youtube, video_ids, batch_size=50):
    """
    Process videos in batches.
    
    Args:
        youtube: YouTube service
        video_ids: List of video IDs
        batch_size: Number of videos per batch
    """
    for i in range(0, len(video_ids), batch_size):
        batch = video_ids[i:i+batch_size]
        
        for video_id in batch:
            like_video(youtube, video_id)
            time.sleep(DELAY_SECONDS + random.uniform(-JITTER, JITTER))
        
        # Pause between batches
        if i + batch_size < len(video_ids):
            logging.info(f"Batch complete. Pausing...")
            time.sleep(60)
```

### Async Operations (Future Enhancement)

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def async_like_video(youtube, video_id):
    """Async wrapper for like operation"""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        return await loop.run_in_executor(pool, like_video, youtube, video_id)

async def process_videos_async(youtube, video_ids):
    """Process multiple videos concurrently"""
    tasks = [async_like_video(youtube, vid) for vid in video_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

---

## Testing

### Unit Tests (Example)

```python
import unittest
from unittest.mock import Mock, patch

class TestVideoOperations(unittest.TestCase):
    
    def setUp(self):
        self.youtube = Mock()
    
    def test_like_video(self):
        """Test video like operation"""
        video_id = "test_video_id"
        like_video(self.youtube, video_id)
        
        self.youtube.videos().rate.assert_called_once_with(
            id=video_id,
            rating="like"
        )
    
    def test_extract_video_id(self):
        """Test video ID extraction"""
        test_cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ]
        
        for url, expected in test_cases:
            result = extract_video_id_from_url(url)
            self.assertEqual(result, expected)

    def test_invalid_video_id(self):
        """Test handling of invalid video IDs"""
        invalid_ids = ["", "invalid", "too_short"]
        for vid_id in invalid_ids:
            with self.assertRaises(Exception):
                like_video(self.youtube, vid_id)
```

---

<div align="center">

**API Reference Complete**

For more information, see the [User Guide](USER_GUIDE.md) and [Setup Guide](SETUP.md)

[⬆ Back to Top](#api-reference---youtube-automation-suite)

</div>
