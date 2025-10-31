#!/usr/bin/env python3
"""
Complete YouTube automation: Like, Comment, Subscribe.
A professional CLI tool for YouTube channel management.

Author: Haseeb Kaloya
Email: haseebkaloya@gmail.com
Contact: +92 3294163702

Requirements:
  pip install google-auth google-auth-oauthlib google-api-python-client colorama

Security / Ethics: Use only for accounts you control. Respect YouTube Terms of Service and quotas.
"""
import os
import sys
import time
import json
import csv
import random
import shutil
import logging
import itertools
from pathlib import Path
from typing import List, Optional

# Google libs
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from colorama import Fore, Style
# UI
from colorama import init as colorama_init, Fore, Style

# ---------- CONFIG DEFAULTS ----------
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
DEFAULT_CREDENTIALS = "credentials.json"
DEFAULT_TOKEN = "token.json"
LOG_CSV = "Logs.csv"
PROCESSED_DIR = "processed_state"
DELAY_SECONDS = 4.0    # base delay between actions
JITTER = 2.0           # +/- random jitter in seconds
MAX_RETRIES = 6
BASE_BACKOFF = 1.0
BOX_MAX_WIDTH = 78
# -------------------------------------

colorama_init(autoreset=True)

# Improved logging: file + console
log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler = logging.FileHandler(LOG_CSV, mode="a", encoding="utf-8")
file_handler.setFormatter(log_formatter)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])

# ---------------- Utilities ----------------


def clear():
    try:
        os.system("cls" if os.name == "nt" else "clear")
    except Exception:
        pass

def prompt(msg: str, default: Optional[str] = None) -> str:
    try:
        if default:
            val = input(f"{msg} [{default}]: ").strip()
            return val if val != "" else default
        return input(f"{msg}: ").strip()
    except EOFError:
        return default if default is not None else ""

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S")

def write_log(action, target_id, status, note=""):
    header_needed = not os.path.exists(LOG_CSV) or os.path.getsize(LOG_CSV) == 0
    with open(LOG_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if header_needed:
            w.writerow(["timestamp", "action", "target_id", "status", "note"])
        w.writerow([timestamp(), action, target_id, status, note])

def save_processed(action, processed_set):
    ensure_dir(PROCESSED_DIR)
    with open(os.path.join(PROCESSED_DIR, f"processed_{action}.json"), "w", encoding="utf-8") as f:
        json.dump(list(processed_set), f, indent=2)

def load_processed(action):
    ensure_dir(PROCESSED_DIR)
    p = os.path.join(PROCESSED_DIR, f"processed_{action}.json")
    if os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

# ---------- Channel resolver ----------
def resolve_channel_id(youtube, input_str: str) -> Optional[str]:
    """
    Accepts channel URL, handle (@username), or UC ID and returns the actual channelId.
    Returns None if not found.
    """
    import re

    if not input_str:
        return None
    s = input_str.strip()

    # Direct channel ID (very tolerant)
    m = re.search(r"(UC[A-Za-z0-9_-]{16,})", s)
    if m:
        return m.group(1)

    # Try to extract handle like @handle
    m = re.search(r"@([A-Za-z0-9_\.]+)", s)
    if m:
        handle = m.group(1)
        # preferred: channels().list(forHandle=handle) (supported by API)
        try:
            resp = youtube.channels().list(part="id", forHandle=handle).execute()
            items = resp.get("items", [])
            if items:
                return items[0].get("id")
        except HttpError:
            # fallback to search if forHandle fails
            pass
        except Exception as e:
            logging.warning("resolve_channel_id: forHandle failed for %s: %s", handle, e)

        # fallback to search
        try:
            resp = youtube.search().list(part="snippet", q=handle, type="channel", maxResults=1).execute()
            items = resp.get("items", [])
            if items:
                return items[0]["snippet"].get("channelId")
        except Exception as e:
            logging.warning("resolve_channel_id: search fallback failed for %s: %s", handle, e)
        return None

    # Generic search for other patterns (custom URLs, /user/, /c/, or plain names)
    try:
        resp = youtube.search().list(part="snippet", q=s, type="channel", maxResults=1).execute()
        items = resp.get("items", [])
        if items:
            return items[0]["snippet"].get("channelId")
    except Exception as e:
        logging.warning("resolve_channel_id: generic search failed for %s: %s", s, e)

    return None

# ---------- Video / Channel extractors ----------
def extract_video_id_from_url(s: str) -> Optional[str]:
    if not s:
        return None
    s = s.strip()
    import re
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", s):
        return s
    m = re.search(r"(?:v=|/v/|youtu\.be/|/embed/)([A-Za-z0-9_-]{11})", s)
    if m:
        return m.group(1)
    if s.startswith("http"):
        parts = s.rstrip("/").split("/")
        candidate = parts[-1]
        if re.fullmatch(r"[A-Za-z0-9_-]{11}", candidate):
            return candidate
    return None

def extract_channel_id_from_url(s: str) -> Optional[str]:
    if not s:
        return None
    s = s.strip()
    import re
    m = re.search(r"youtube\.com/(?:channel/)(UC[0-9A-Za-z_-]+)", s)
    if m:
        return m.group(1)
    # Accept plain UC id
    if s.startswith("UC") and len(s) > 10:
        return s
    return None

# ---------- Google Auth helpers ----------
def load_or_create_credentials(credentials_path: str, token_path: str, scopes=SCOPES):
    creds = None
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, scopes)
        except Exception as e:
            logging.warning("Failed to load token file (%s): %s", token_path, e)
            creds = None

    # refresh if possible
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            # save refreshed token
            with open(token_path, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
        except Exception as e:
            logging.warning("Refresh failed: %s", e)
            creds = None

    if not creds or not creds.valid:
        if not os.path.exists(credentials_path):
            logging.error("Missing credentials.json file at %s", credentials_path)
            raise FileNotFoundError(f"Missing {credentials_path}")
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes)
        creds = flow.run_local_server(port=0, prompt="consent", authorization_prompt_message="")
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
        logging.info("Saved new token to %s", token_path)

    return creds

def build_youtube_service(creds):
    return build("youtube", "v3", credentials=creds, cache_discovery=False)

# ---------- Backoff wrapper ----------
def with_exponential_backoff(fn, *args, max_retries=MAX_RETRIES, **kwargs):
    attempt = 0
    while True:
        try:
            return fn(*args, **kwargs)
        except HttpError as e:
            status = None
            try:
                status = int(e.resp.status)
            except Exception:
                pass
            # retry for 5xx, 429, 403 (quota/rate) - conservative
            if status in (429, 403) or (status and 500 <= status < 600):
                attempt += 1
                if attempt > max_retries:
                    raise
                sleep_time = BASE_BACKOFF * (2 ** (attempt - 1)) + random.random()
                logging.warning("HTTP %s — backing off %.1fs (attempt %d/%d)", status, sleep_time, attempt, max_retries)
                time.sleep(sleep_time)
                continue
            else:
                # non-retryable
                raise
        except Exception as e:
            attempt += 1
            if attempt > max_retries:
                raise
            sleep_time = BASE_BACKOFF * (2 ** (attempt - 1)) + random.random()
            logging.warning("Error: %s — retrying in %.1fs (attempt %d/%d)", e, sleep_time, attempt, max_retries)
            time.sleep(sleep_time)

# ---------- Core actions ----------
def like_video(youtube, video_id: str):
    def _call():
        return youtube.videos().rate(id=video_id, rating="like").execute()
    with_exponential_backoff(_call)
    return True

def subscribe_channel(youtube, channel_id: str):
    body = {"snippet": {"resourceId": {"kind": "youtube#channel", "channelId": channel_id}}}
    def _call():
        return youtube.subscriptions().insert(part="snippet", body=body).execute()
    resp = with_exponential_backoff(_call)
    return resp

def post_top_level_comment(youtube, video_id: str, text: str):
    body = {
        "snippet": {
            "videoId": video_id,
            "topLevelComment": {"snippet": {"textOriginal": text}}
        }
    }
    def _call():
        return youtube.commentThreads().insert(part="snippet", body=body).execute()
    resp = with_exponential_backoff(_call)
    return resp

# ---------- Input parsers ----------
def read_video_ids_from_file(path: str) -> List[str]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    vids = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            vid = extract_video_id_from_url(s)
            if vid:
                vids.append(vid)
            else:
                logging.warning("Skipping invalid video entry: %s", s)
    # dedupe preserve order
    seen = set()
    out = []
    for v in vids:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out

def read_comments_from_file(path: str, max_comments=1000) -> List[str]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    comments = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            t = line.strip()
            if t:
                comments.append(t)
            if len(comments) >= max_comments:
                break
    return comments

def read_channel_ids_from_file(path: str, youtube) -> List[str]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    chs = []
    with p.open("r", encoding="utf-8") as f:
        for raw_line in f:
            s = raw_line.strip()
            if not s:
                continue

            # Try direct extraction from URL (fast)
            cid = extract_channel_id_from_url(s)

            # If not found, try resolving with API
            if not cid:
                cid = resolve_channel_id(youtube, s)

            if cid:
                chs.append(cid)
                logging.info("Resolved %s → %s", s, cid)
            else:
                logging.warning("Skipping unrecognized or invalid channel entry: %s", s)

    # dedupe preserve order
    seen = set()
    out = []
    for c in chs:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out

# ---------- Runner flows ----------
def run_likes(youtube, path, processed):
    video_ids = read_video_ids_from_file(path)
    logging.info("Found %d unique videos to like", len(video_ids))
    for idx, vid in enumerate(video_ids, start=1):
        if vid in processed:
            logging.info("[%d/%d] Skipping already-processed like: %s", idx, len(video_ids), vid)
            continue
        logging.info("[%d/%d] Liking video: %s", idx, len(video_ids), vid)
        try:
            like_video(youtube, vid)
            write_log("like", vid, "success", "")
            processed.add(vid)
            save_processed("like", processed)
            logging.info("Liked: %s", vid)
        except HttpError as e:
            code = getattr(e.resp, "status", "N/A")
            logging.error("HTTP error liking %s: %s", vid, code)
            write_log("like", vid, "failed", f"HTTP {code}")
        except Exception as e:
            logging.exception("Error liking %s: %s", vid, e)
            write_log("like", vid, "failed", str(e))
        # polite delay
        time.sleep(max(0, DELAY_SECONDS + random.uniform(-JITTER, JITTER)))

def run_subscribes(youtube, path, processed):
    ch_ids = read_channel_ids_from_file(path, youtube)
    logging.info("Found %d unique channels to subscribe", len(ch_ids))
    for idx, cid in enumerate(ch_ids, start=1):
        if cid in processed:
            logging.info("[%d/%d] Skipping already-processed subscribe: %s", idx, len(ch_ids), cid)
            continue
        logging.info("[%d/%d] Subscribing to channel: %s", idx, len(ch_ids), cid)
        try:
            resp = subscribe_channel(youtube, cid)
            sub_id = resp.get("id") if isinstance(resp, dict) else ""
            write_log("subscribe", cid, "success", str(sub_id))
            processed.add(cid)
            save_processed("subscribe", processed)
            logging.info("Subscribed: %s", cid)
        except HttpError as e:
            status = getattr(e.resp, "status", "N/A")
            # Specific handling for abuse/quota could be added here
            logging.error("HTTP error subscribing %s: %s", cid, status)
            write_log("subscribe", cid, "failed", f"HTTP {status}")
        except Exception as e:
            logging.exception("Error subscribing %s: %s", cid, e)
            write_log("subscribe", cid, "failed", str(e))
        time.sleep(max(0, DELAY_SECONDS + random.uniform(-JITTER, JITTER)))

def run_comments(youtube, path, processed, max_comments_per_run=None):
    comments = read_comments_from_file(path)
    if max_comments_per_run:
        comments = comments[:max_comments_per_run]
    logging.info("Loaded %d comments", len(comments))
    target_video = prompt("Enter target video URL or ID to post comments to")
    vid = extract_video_id_from_url(target_video)
    if not vid:
        logging.error("Could not extract video id from provided target.")
        raise ValueError("Invalid target video")
    logging.info("Posting comments to video id: %s", vid)
    for idx, c in enumerate(comments, start=1):
        key = f"{vid}::{hash(c)}"
        if key in processed:
            logging.info("[%d/%d] Skipping already-posted comment (dedup): %.60s", idx, len(comments), c)
            continue
        logging.info("[%d/%d] Posting comment: %.80s", idx, len(comments), c)
        try:
            resp = post_top_level_comment(youtube, vid, c)
            comment_id = resp.get("id") if isinstance(resp, dict) else ""
            write_log("comment", vid, "success", comment_id)
            processed.add(key)
            save_processed("comment", processed)
            logging.info("Posted comment id: %s", comment_id)
        except HttpError as e:
            code = getattr(e.resp, "status", "N/A")
            logging.error("HTTP error posting comment: %s", code)
            write_log("comment", vid, "failed", f"HTTP {code}")
        except Exception as e:
            logging.exception("Error posting comment: %s", e)
            write_log("comment", vid, "failed", str(e))
        time.sleep(max(0, DELAY_SECONDS + random.uniform(-JITTER, JITTER)))


#	------------------------------>Welcome Screen<--------------------------------------------


try:
    from colorama import init, Fore, Style
except Exception as e:
    print("Missing dependency: colorama. Install with: pip install colorama")
    raise

try:
    import pyfiglet
    PYFIGLET_AVAILABLE = True
except Exception:
    PYFIGLET_AVAILABLE = False

# Initialize colorama
init(autoreset=True)

# ------------------ Configuration ------------------
BRAND = "YouTube Automation Suite"
AUTHOR = "Community Project"
TAGLINE = "Professional YouTube Management Tool"
TELEGRAM_LINK = "#"      # Optional: Add your contact link
WHATSAPP_LINK = "#"       # Optional: Add your contact link
ANIMATION_SPEED = 0.0018   # lower -> faster; raise if your CPU jumps
BOX_MAX_WIDTH = 78         # maximum width for the info box
# ---------------------------------------------------

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def get_terminal_width(fallback=80):
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return fallback

def center_text(text, width):
    lines = text.splitlines() or [text]
    return "\n".join(line.center(width) for line in lines)

def rainbow_cycle_iter():
    """Return an infinite iterator cycling through chosen colors."""
    colors = [Fore.GREEN + Style.BRIGHT, Fore.CYAN + Style.BRIGHT, Fore.MAGENTA + Style.BRIGHT, Fore.WHITE + Style.BRIGHT]
    return itertools.cycle(colors)

def animate_print(text, delay=ANIMATION_SPEED):
    """Print text character-by-character using an infinite color cycle."""
    color_iter = rainbow_cycle_iter()
    try:
        for ch in text:
            color = next(color_iter)
            # Avoid coloring newline characters to keep layout predictable
            if ch == "\n":
                sys.stdout.write(ch)
            else:
                sys.stdout.write(color + ch)
            sys.stdout.flush()
            time.sleep(delay)
    except KeyboardInterrupt:
        # Allow user to abort animation gracefully
        print(Style.RESET_ALL + "\n[Animation interrupted]")
        raise
    finally:
        # Reset styles after animation
        print(Style.RESET_ALL, end="")

def boxed_info(lines, box_width=None):
    """Return a string with lines enclosed in a Unicode box."""
    if not lines:
        return ""
    content_width = max(len(l) for l in lines)
    if box_width is None:
        box_width = min(max(content_width + 4, 20), BOX_MAX_WIDTH)
    # Ensure box_width is wide enough for content
    inner_width = box_width - 4
    top = "╔" + "═" * (box_width - 2) + "╗"
    bot = "╚" + "═" * (box_width - 2) + "╝"
    body_lines = []
    for l in lines:
        # truncate if too long
        display = l if len(l) <= inner_width else l[:inner_width - 3] + "..."
        body_lines.append("║ " + display.ljust(inner_width) + " ║")
    return "\n".join([top] + body_lines + [bot])

def load_logo_text(brand, font="slant"):
    """Generate ASCII art logo; fallback to plain text if pyfiglet not available."""
    if PYFIGLET_AVAILABLE:
        try:
            return pyfiglet.figlet_format(brand, font=font)
        except Exception:
            # Font might not exist on some systems
            return pyfiglet.figlet_format(brand)
    else:
        # Simple stylized fallback
        return f"=== {brand} ===\n"

def scanning_bar(width, length=40, speed=0.01):
    """Simple scanning bar animation centered."""
    length = min(length, max(10, width - 20))
    for i in range(length + 1):
        left = "[" + "=" * i + " " * (length - i) + "]"
        sys.stdout.write(Fore.GREEN + left.center(width) + "\r")
        sys.stdout.flush()
        time.sleep(speed)
    print()  # newline after bar
#theme functions end


def main():
#theme main function start
    try:
        clear()
        width = get_terminal_width()

        # small safeguard: ensure width not too small
        if width < 40:
            width = 40

        # Scanning prelude
        scanning_bar(width, length=min(60, width - 20), speed=0.008)

        # Load & center logo
        logo_text = load_logo_text(BRAND)
        centered_logo = center_text(logo_text, width)

        # Animated logo print
        animate_print(centered_logo, delay=ANIMATION_SPEED)

        # Tagline
        print(Fore.CYAN + Style.BRIGHT + TAGLINE.center(width) + Style.RESET_ALL)
        print()

        # Info box
        info_lines = [
            f"Author  : {AUTHOR}",
            f"Brand   : {BRAND}",
            f"Telegram: {TELEGRAM_LINK}",
            f"WhatsApp: {WHATSAPP_LINK}",
        ]
        # Choose box width relative to terminal width
        desired_box_width = min(BOX_MAX_WIDTH, max(len(max(info_lines, key=len)) + 6, 40), width - 4)
        box_str = boxed_info(info_lines, box_width=desired_box_width)
        # Color the box green and center it
        box_lines = box_str.splitlines()
        for line in box_lines:
            print(Fore.GREEN + line.center(width))

        print()

        # Ready animation
        ready_msg = "INITIALIZING MODULES"
        for dots in range(4):
            sys.stdout.write(Fore.YELLOW + Style.BRIGHT + (ready_msg + "." * dots).center(width) + "\r")
            sys.stdout.flush()
            time.sleep(0.5)
        print()
        print(Fore.GREEN + Style.BRIGHT + ("✅  READY — " + BRAND).center(width))
        print()

    except KeyboardInterrupt:
        print("\n" + Fore.RED + "Interrupted by user." + Style.RESET_ALL)
        sys.exit(1)
#theme main function end
    print(Fore.YELLOW + Style.BRIGHT + "⚠️  IMPORTANT — USE RESPONSIBLY  ⚠️")
    print(Fore.MAGENTA + "Only operate on accounts you control. Unauthorized or abusive automation can violate YouTube's policies.")
    actions_raw = prompt("✨ What would you like the bot to do today? ✨"
  "\n🎯 Choose your action:\n"
    "   💖  like       →  Auto-like videos\n"
    "   💬  comment    →  Post smart comments\n"
    "   📢  subscribe  →  Subscribe to target channels\n"
    "   🌟  all        →  Perform every action\n\n"
    "✏️  Enter your choice [like] , [comment] , [subscribe] , [all] -->"
).strip().lower()
    if actions_raw == "all":
        chosen = ["like", "comment", "subscribe"]
    else:
        chosen = [a.strip() for a in actions_raw.split(",") if a.strip() in ("like", "comment", "subscribe")]
    if not chosen:
        print(Fore.RED + "No valid actions chosen. Exiting.")
        return

    # Credentials/token paths
    credentials_path = prompt("Path to credentials.json", DEFAULT_CREDENTIALS)
    token_path = prompt("Path to token.json (will be created if missing)", DEFAULT_TOKEN)

    # Gather file paths for selected actions
    likes_path = comments_path = subs_path = None
    if "like" in chosen:
        likes_path = prompt("Path to Likes.txt (video ids or URLs)")
    if "comment" in chosen:
        comments_path = prompt("Path to Comments.txt (one comment per line)")
    if "subscribe" in chosen:
        subs_path = prompt("Path to Channels.txt (channel ids or URLs)")

    # Ask for pacing — FIXED global variable section
    global DELAY_SECONDS, JITTER
    nonlocal_delay = prompt("Base delay in seconds between actions (float)", str(DELAY_SECONDS))
    nonlocal_jitter = prompt("Jitter in seconds (+/-) (float)", str(JITTER))
    try:
        DELAY_SECONDS = float(nonlocal_delay)
        JITTER = float(nonlocal_jitter)
    except Exception:
        print("Invalid delay/jitter values — using defaults.")

    # Authenticate
    try:
        creds = load_or_create_credentials(credentials_path, token_path)
    except Exception as e:
        print(Fore.RED + f"Authentication failed: {e}")
        return

    youtube = build_youtube_service(creds)
    print(Fore.CYAN + "Authenticated. Running actions: " + ", ".join(chosen))

    # Load processed sets
    processed_like = load_processed("like")
    processed_subscribe = load_processed("subscribe")
    processed_comment = load_processed("comment")

    # Execute in chosen order
    try:
        if "like" in chosen:
            if not likes_path:
                logging.warning("No likes path provided — skipping likes.")
            else:
                run_likes(youtube, likes_path, processed_like)
        if "subscribe" in chosen:
            if not subs_path:
                logging.warning("No subscribe path provided — skipping subscribes.")
            else:
                run_subscribes(youtube, subs_path, processed_subscribe)
        if "comment" in chosen:
            if not comments_path:
                logging.warning("No comments path provided — skipping comments.")
            else:
                run_comments(youtube, comments_path, processed_comment)
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\nInterrupted by user. Saving state...")
    except Exception as e:
        logging.exception("Unexpected error: %s", e)
    finally:
        save_processed("like", processed_like)
        save_processed("subscribe", processed_subscribe)
        save_processed("comment", processed_comment)
        print(Fore.GREEN + "\nAll done. Log file: " + LOG_CSV)
        print("Processed state saved in: " + PROCESSED_DIR)

if __name__ == "__main__":
    main()
