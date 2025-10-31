#!/usr/bin/env python3
"""
Professional GUI Version - YouTube Automation Tool
A modern automation suite for YouTube channel management

Author: Haseeb Kaloya
Email: haseebkaloya@gmail.com
Contact: +92 3294163702
"""
import os
import sys
import time
import json
import csv
import random
import threading
import logging
import re
import shutil
import itertools
from pathlib import Path
from typing import List, Optional, Set
import webbrowser

import customtkinter as ctk
from tkinter import filedialog, messagebox, scrolledtext

# Google API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# Constants
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
DEFAULT_CREDENTIALS = "credentials.json"
DEFAULT_TOKEN = "token.json"
LOG_CSV = "Logs.csv"
PROCESSED_DIR = "processed_state"
DELAY_SECONDS = 4.0
JITTER = 2.0
MAX_RETRIES = 4
BASE_BACKOFF = 1.0

class YouTubeAutomationGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("🔰 YouTube Automation Suite - Professional Tool")
        
        # Get screen dimensions and set appropriate window size
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Set window to 80% of screen size with reasonable limits
        window_width = min(1200, int(screen_width * 0.8))
        window_height = min(700, int(screen_height * 0.75))
        
        # Calculate position to center the window
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        
        self.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.minsize(900, 600)
        
        # Initialize state variables
        self.is_running = False
        self.current_action = None
        self.youtube_service = None
        self.credentials_path = DEFAULT_CREDENTIALS
        self.token_path = DEFAULT_TOKEN
        
        # File paths and direct content
        self.likes_file = ""
        self.comments_file = ""
        self.channels_file = ""
        self.target_video = ""
        
        # Processed sets
        self.processed_like = set()
        self.processed_subscribe = set()
        self.processed_comment = set()
        
        # Statistics
        self.stats = {"likes": 0, "comments": 0, "subscriptions": 0, "errors": 0}
        
        # Setup UI first
        self.setup_ui()
        
        # Configure logging to GUI
        self.setup_logging()
        
        # Load processed state
        self.load_processed_state()
    
    def setup_logging(self):
        """Configure logging to display in GUI"""
        self.log_handler = GUILogHandler(self)
        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger().setLevel(logging.INFO)
    
    def setup_ui(self):
        """Create the main user interface"""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
        # Create status bar
        self.create_status_bar()
    
    def create_sidebar(self):
        """Create the enhanced sidebar"""
        sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color="#111111")
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(8, weight=1)
        
        # Branding with hacker style
        brand_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        brand_label = ctk.CTkLabel(
            brand_frame, 
            text="🔰 YT Automation",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#00FF88"
        )
        brand_label.pack()
        
        tagline_label = ctk.CTkLabel(
            brand_frame,
            text="Think Secure. Act Smart.",
            font=ctk.CTkFont(size=12),
            text_color="#0088FF"
        )
        tagline_label.pack(pady=(5, 0))
        
        # Action selection
        actions_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        actions_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(
            actions_frame, 
            text="ACTIONS",
            font=ctk.CTkFont(weight="bold", size=14),
            text_color="#00FF88"
        ).pack(anchor="w", pady=(0, 10))
        
        self.like_var = ctk.BooleanVar()
        self.comment_var = ctk.BooleanVar()
        self.subscribe_var = ctk.BooleanVar()
        
        self.like_cb = ctk.CTkCheckBox(
            actions_frame, 
            text="💖 Like Videos", 
            variable=self.like_var
        )
        self.like_cb.pack(anchor="w", pady=5)
        
        self.comment_cb = ctk.CTkCheckBox(
            actions_frame, 
            text="💬 Post Comments", 
            variable=self.comment_var
        )
        self.comment_cb.pack(anchor="w", pady=5)
        
        self.subscribe_cb = ctk.CTkCheckBox(
            actions_frame, 
            text="📢 Subscribe", 
            variable=self.subscribe_var
        )
        self.subscribe_cb.pack(anchor="w", pady=5)
        
        # File inputs section
        files_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        files_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(
            files_frame, 
            text="INPUT FILES",
            font=ctk.CTkFont(weight="bold", size=14),
            text_color="#00FF88"
        ).pack(anchor="w", pady=(0, 10))
        
        # Likes file
        self.likes_button = ctk.CTkButton(
            files_frame,
            text="📁 Likes.txt",
            command=self.select_likes_file,
            width=200
        )
        self.likes_button.pack(fill="x", pady=5)
        self.likes_label = ctk.CTkLabel(files_frame, text="No file selected", text_color="#888888", font=ctk.CTkFont(size=10))
        self.likes_label.pack()
        
        # Comments file
        self.comments_button = ctk.CTkButton(
            files_frame,
            text="📁 Comments.txt",
            command=self.select_comments_file,
            width=200
        )
        self.comments_button.pack(fill="x", pady=5)
        self.comments_label = ctk.CTkLabel(files_frame, text="No file selected", text_color="#888888", font=ctk.CTkFont(size=10))
        self.comments_label.pack()
        
        # Channels file
        self.channels_button = ctk.CTkButton(
            files_frame,
            text="📁 Channels.txt",
            command=self.select_channels_file,
            width=200
        )
        self.channels_button.pack(fill="x", pady=5)
        self.channels_label = ctk.CTkLabel(files_frame, text="No file selected", text_color="#888888", font=ctk.CTkFont(size=10))
        self.channels_label.pack()
        
        # Target video for comments
        ctk.CTkLabel(files_frame, text="Target Video:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        self.target_video_entry = ctk.CTkEntry(
            files_frame,
            placeholder_text="Video URL or ID for comments",
            width=200
        )
        self.target_video_entry.pack(fill="x", pady=5)
        
        # Credentials file
        self.creds_button = ctk.CTkButton(
            files_frame,
            text="🔑 credentials.json",
            command=self.select_credentials,
            width=200
        )
        self.creds_button.pack(fill="x", pady=10)
        self.creds_label = ctk.CTkLabel(files_frame, text="No file selected", text_color="#888888", font=ctk.CTkFont(size=10))
        self.creds_label.pack()
        
        # Control buttons
        controls_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        controls_frame.grid(row=9, column=0, padx=20, pady=20, sticky="ew")
        
        self.run_button = ctk.CTkButton(
            controls_frame,
            text="🚀 Start Automation",
            command=self.start_automation,
            fg_color="#00AA55",
            hover_color="#008844",
            font=ctk.CTkFont(weight="bold"),
            height=40
        )
        self.run_button.pack(fill="x", pady=(0, 10))
        
        self.stop_button = ctk.CTkButton(
            controls_frame,
            text="⏹️ Stop",
            command=self.stop_automation,
            fg_color="#FF4444",
            hover_color="#CC3333",
            state="disabled",
            height=35
        )
        self.stop_button.pack(fill="x", pady=(0, 10))
        
        # Quick actions
        quick_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        quick_frame.grid(row=10, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkButton(
            quick_frame,
            text="⚙️ Settings",
            command=self.open_settings,
            fg_color="#444444",
            hover_color="#666666"
        ).pack(fill="x", pady=2)
    
    def create_main_content(self):
        """Create the main content area"""
        main_frame = ctk.CTkFrame(self, fg_color="#1A1A1A")
        main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Progress section
        progress_frame = ctk.CTkFrame(main_frame, fg_color="#222222")
        progress_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ctk.CTkLabel(progress_frame, text="Automation Progress", 
                    font=ctk.CTkFont(weight="bold", size=16)).pack(anchor="w", padx=20, pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame, height=20, progress_color="#00FF88")
        self.progress_bar.pack(fill="x", padx=20, pady=10)
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(progress_frame, text="Ready to start automation", 
                                          font=ctk.CTkFont(size=12))
        self.progress_label.pack(pady=(0, 10))
        
        # Statistics
        stats_frame = ctk.CTkFrame(main_frame, fg_color="#222222")
        stats_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        ctk.CTkLabel(stats_frame, text="Live Statistics", 
                    font=ctk.CTkFont(weight="bold", size=14)).pack(anchor="w", padx=20, pady=10)
        
        stats_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_grid.pack(fill="x", padx=20, pady=10)
        stats_grid.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.likes_stats = ctk.CTkLabel(stats_grid, text="💖 Likes: 0", font=ctk.CTkFont(size=12, weight="bold"))
        self.likes_stats.grid(row=0, column=0, padx=10, pady=5)
        
        self.comments_stats = ctk.CTkLabel(stats_grid, text="💬 Comments: 0", font=ctk.CTkFont(size=12, weight="bold"))
        self.comments_stats.grid(row=0, column=1, padx=10, pady=5)
        
        self.subs_stats = ctk.CTkLabel(stats_grid, text="📢 Subscriptions: 0", font=ctk.CTkFont(size=12, weight="bold"))
        self.subs_stats.grid(row=0, column=2, padx=10, pady=5)
        
        # Current action
        action_frame = ctk.CTkFrame(main_frame, fg_color="#222222")
        action_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        
        ctk.CTkLabel(action_frame, text="Current Action", 
                    font=ctk.CTkFont(weight="bold", size=14)).pack(anchor="w", padx=20, pady=10)
        
        self.action_display = ctk.CTkLabel(action_frame, text="No active action", 
                                         font=ctk.CTkFont(size=16, weight="bold"),
                                         text_color="#00FF88")
        self.action_display.pack(pady=10)
        
        # Log output
        log_frame = ctk.CTkFrame(main_frame)
        log_frame.grid(row=3, column=0, sticky="nsew")
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(0, weight=1)
        
        ctk.CTkLabel(log_frame, text="Activity Log", 
                    font=ctk.CTkFont(weight="bold", size=14)).pack(anchor="w", padx=15, pady=10)
        
        self.log_text = ctk.CTkTextbox(
            log_frame,
            wrap="word",
            font=ctk.CTkFont(family="Consolas", size=11)
        )
        self.log_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Clear log button
        self.clear_log_button = ctk.CTkButton(
            log_frame, 
            text="Clear Log", 
            command=self.clear_log,
            width=100
        )
        self.clear_log_button.pack(anchor="e", padx=15, pady=(0, 15))
    
    def create_status_bar(self):
        """Create enhanced status bar"""
        status_frame = ctk.CTkFrame(self, height=30, fg_color="#111111", corner_radius=0)
        status_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            status_frame, 
            text="🔰 YouTube Automation Suite - Ready"
        )
        self.status_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.connection_status = ctk.CTkLabel(
            status_frame, 
            text="🔴 Disconnected",
            text_color="#FF4444"
        )
        self.connection_status.grid(row=0, column=1, padx=10, pady=5, sticky="e")
    
    def select_credentials(self):
        """Select credentials.json file"""
        filename = filedialog.askopenfilename(
            title="Select credentials.json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.credentials_path = filename
            self.creds_label.configure(text=os.path.basename(filename))
            self.update_status("Credentials file loaded")
    
    def select_likes_file(self):
        """Select Likes.txt file"""
        filename = filedialog.askopenfilename(
            title="Select Likes.txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.likes_file = filename
            self.likes_label.configure(text=os.path.basename(filename))
            self.update_status("Likes file loaded")
    
    def select_comments_file(self):
        """Select Comments.txt file"""
        filename = filedialog.askopenfilename(
            title="Select Comments.txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.comments_file = filename
            self.comments_label.configure(text=os.path.basename(filename))
            self.update_status("Comments file loaded")
    
    def select_channels_file(self):
        """Select Channels.txt file"""
        filename = filedialog.askopenfilename(
            title="Select Channels.txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.channels_file = filename
            self.channels_label.configure(text=os.path.basename(filename))
            self.update_status("Channels file loaded")
    
    def open_settings(self):
        """Open settings dialog - FIXED METHOD"""
        try:
            settings = SettingsDialog(self)
            self.wait_window(settings)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open settings: {e}")
    
    def update_progress(self, value, text=None):
        """Update progress bar and label"""
        self.progress_bar.set(value)
        if text:
            self.progress_label.configure(text=text)
    
    def update_status(self, message):
        """Update status bar"""
        self.status_label.configure(text=f"🔰 YouTube Automation - {message}")
        self.log_message(f"STATUS: {message}")
    
    def update_action(self, action):
        """Update current action display"""
        self.current_action = action
        if action:
            self.action_display.configure(text=f"🔄 {action}", text_color="#00FF88")
            self.connection_status.configure(text="🟢 Connected", text_color="#00FF88")
        else:
            self.action_display.configure(text="No active action", text_color="#888888")
            self.connection_status.configure(text="🔴 Disconnected", text_color="#FF4444")
    
    def update_stats(self):
        """Update statistics display"""
        self.likes_stats.configure(text=f"💖 Likes: {self.stats['likes']}")
        self.comments_stats.configure(text=f"💬 Comments: {self.stats['comments']}")
        self.subs_stats.configure(text=f"📢 Subscriptions: {self.stats['subscriptions']}")
    
    def log_message(self, message, level="info"):
        """Add message to log with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        color_map = {
            "info": "#FFFFFF",
            "warning": "#FFAA00",
            "error": "#FF4444",
            "success": "#00FF88",
        }
        
        tag = level.upper()
        log_entry = f"[{timestamp}] [{tag}] {message}\n"
        
        self.log_text.insert("end", log_entry)
        self.log_text.see("end")
    
    def clear_log(self):
        """Clear the log display"""
        self.log_text.delete("1.0", "end")
    
    def load_processed_state(self):
        """Load processed state from files"""
        self.processed_like = self.load_processed("like")
        self.processed_subscribe = self.load_processed("subscribe")
        self.processed_comment = self.load_processed("comment")
    
    def load_processed(self, action):
        """Load processed items for an action"""
        ensure_dir(PROCESSED_DIR)
        p = os.path.join(PROCESSED_DIR, f"processed_{action}.json")
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return set(json.load(f))
            except Exception as e:
                self.log_message(f"Error loading processed {action}: {e}", "warning")
                return set()
        return set()
    
    def save_processed(self, action, processed_set):
        """Save processed items for an action"""
        ensure_dir(PROCESSED_DIR)
        with open(os.path.join(PROCESSED_DIR, f"processed_{action}.json"), "w", encoding="utf-8") as f:
            json.dump(list(processed_set), f, indent=2)
    
    def start_automation(self):
        """Start the automation process"""
        if not hasattr(self, 'credentials_path') or not os.path.exists(self.credentials_path):
            messagebox.showerror("Error", "❌ Please select a valid credentials.json file")
            return
        
        # Validate actions and inputs
        actions = []
        missing_inputs = []
        
        if self.like_var.get():
            if not self.likes_file or not os.path.exists(self.likes_file):
                missing_inputs.append("Likes.txt file")
            else:
                actions.append("like")
        
        if self.comment_var.get():
            if not self.comments_file or not os.path.exists(self.comments_file):
                missing_inputs.append("Comments.txt file")
            elif not self.target_video_entry.get().strip():
                missing_inputs.append("target video URL")
            else:
                actions.append("comment")
        
        if self.subscribe_var.get():
            if not self.channels_file or not os.path.exists(self.channels_file):
                missing_inputs.append("Channels.txt file")
            else:
                actions.append("subscribe")
        
        if not actions:
            messagebox.showerror("Error", "❌ Please select at least one action and provide the required files")
            return
        
        if missing_inputs:
            messagebox.showerror("Error", f"❌ Missing: {', '.join(missing_inputs)}")
            return
        
        # Store target video
        self.target_video = self.target_video_entry.get().strip()
        
        # Disable controls
        self.disable_controls()
        self.is_running = True
        
        # Reset statistics
        self.stats = {"likes": 0, "comments": 0, "subscriptions": 0, "errors": 0}
        self.update_stats()
        
        # Start automation
        thread = threading.Thread(target=self.run_automation, args=(actions,))
        thread.daemon = True
        thread.start()
    
    def disable_controls(self):
        """Disable all controls during automation"""
        self.run_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        for cb in [self.like_cb, self.comment_cb, self.subscribe_cb]:
            cb.configure(state="disabled")
        for btn in [self.creds_button, self.likes_button, self.comments_button, self.channels_button]:
            btn.configure(state="disabled")
    
    def enable_controls(self):
        """Enable all controls after automation"""
        self.run_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        for cb in [self.like_cb, self.comment_cb, self.subscribe_cb]:
            cb.configure(state="normal")
        for btn in [self.creds_button, self.likes_button, self.comments_button, self.channels_button]:
            btn.configure(state="normal")
    
    def stop_automation(self):
        """Stop the automation process"""
        self.is_running = False
        self.update_status("Stopping automation...")
        self.log_message("Automation stopped by user", "warning")
        self.enable_controls()
        self.update_action(None)
    
    def run_automation(self, actions):
        """Run automation in background thread"""
        try:
            # Authenticate
            self.update_status("Authenticating with YouTube API...")
            self.log_message("Starting authentication process", "info")
            
            creds = self.load_or_create_credentials()
            self.youtube_service = build("youtube", "v3", credentials=creds)
            
            self.log_message("Authentication successful", "success")
            
            # Execute actions
            for action in actions:
                if not self.is_running:
                    break
                    
                self.update_action(action.capitalize())
                self.log_message(f"Starting {action} automation", "info")
                
                if action == "like":
                    success_count = self.run_likes_gui()
                    self.stats["likes"] += success_count
                elif action == "comment":
                    success_count = self.run_comments_gui()
                    self.stats["comments"] += success_count
                elif action == "subscribe":
                    success_count = self.run_subscribes_gui()
                    self.stats["subscriptions"] += success_count
                
                self.update_stats()
                
                if self.is_running:
                    self.log_message(f"Completed {action} - {success_count} successful", "success")
            
            if self.is_running:
                total_success = sum([self.stats['likes'], self.stats['comments'], self.stats['subscriptions']])
                self.update_progress(1.0, "All actions completed")
                self.update_status(f"Completed - {total_success} total actions")
                self.log_message(f"Automation completed - {total_success} successful actions", "success")
                self.after(0, lambda: messagebox.showinfo("Complete", f"✅ Automation completed!\n\n💖 Likes: {self.stats['likes']}\n💬 Comments: {self.stats['comments']}\n📢 Subscriptions: {self.stats['subscriptions']}"))
            
        except Exception as e:
            self.stats["errors"] += 1
            self.update_stats()
            self.log_message(f"Automation failed: {str(e)}", "error")
            self.after(0, lambda: messagebox.showerror("Error", f"❌ Automation failed:\n{str(e)}"))
        
        finally:
            self.after(0, self.enable_controls)
            self.update_action(None)
    
    # ORIGINAL SCRIPT LOGIC METHODS
    def load_or_create_credentials(self):
        """Load or create OAuth2 credentials"""
        creds = None
        if os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
            except Exception as e:
                self.log_message(f"Token load failed: {e}", "warning")
                creds = None

        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                with open(self.token_path, "w", encoding="utf-8") as token:
                    token.write(creds.to_json())
            except Exception as e:
                self.log_message(f"Token refresh failed: {e}", "warning")
                creds = None

        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
            with open(self.token_path, "w", encoding="utf-8") as token:
                token.write(creds.to_json())
            
            self.log_message("New authentication completed", "success")
        
        return creds
    
    def with_exponential_backoff(self, fn, *args, max_retries=MAX_RETRIES, **kwargs):
        """Exponential backoff wrapper"""
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
                if status in (429, 403) or (status and 500 <= status < 600):
                    attempt += 1
                    if attempt > max_retries:
                        raise
                    sleep_time = BASE_BACKOFF * (2 ** (attempt - 1)) + random.random()
                    self.log_message(f"HTTP {status} - backing off {sleep_time:.1f}s (attempt {attempt}/{max_retries})", "warning")
                    time.sleep(sleep_time)
                    continue
                else:
                    raise
            except Exception as e:
                attempt += 1
                if attempt > max_retries:
                    raise
                sleep_time = BASE_BACKOFF * (2 ** (attempt - 1)) + random.random()
                self.log_message(f"Error: {e} - retrying in {sleep_time:.1f}s (attempt {attempt}/{max_retries})", "warning")
                time.sleep(sleep_time)
    
    def like_video(self, video_id: str):
        """Like a video"""
        def _call():
            return self.youtube_service.videos().rate(id=video_id, rating="like").execute()
        self.with_exponential_backoff(_call)
        return True
    
    def subscribe_channel(self, channel_id: str):
        """Subscribe to a channel"""
        body = {"snippet": {"resourceId": {"kind": "youtube#channel", "channelId": channel_id}}}
        def _call():
            return self.youtube_service.subscriptions().insert(part="snippet", body=body).execute()
        resp = self.with_exponential_backoff(_call)
        return resp
    
    def post_top_level_comment(self, video_id: str, text: str):
        """Post a comment"""
        body = {
            "snippet": {
                "videoId": video_id,
                "topLevelComment": {"snippet": {"textOriginal": text}}
            }
        }
        def _call():
            return self.youtube_service.commentThreads().insert(part="snippet", body=body).execute()
        resp = self.with_exponential_backoff(_call)
        return resp
    
    def extract_video_id_from_url(self, s: str) -> Optional[str]:
        """Extract video ID from URL"""
        if not s:
            return None
        s = s.strip()
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
    
    def extract_channel_id_from_url(self, s: str) -> Optional[str]:
        """Extract channel ID from URL"""
        if not s:
            return None
        s = s.strip()
        m = re.search(r"youtube\.com/(?:channel/)(UC[0-9A-Za-z_-]+)", s)
        if m:
            return m.group(1)
        if s.startswith("UC") and len(s) > 10:
            return s
        return None
    
    def resolve_channel_id(self, input_str: str) -> Optional[str]:
        """Resolve channel ID from various formats"""
        if not input_str:
            return None
        s = input_str.strip()

        # Direct channel ID
        m = re.search(r"(UC[A-Za-z0-9_-]{16,})", s)
        if m:
            return m.group(1)

        # Handle @username
        m = re.search(r"@([A-Za-z0-9_\.]+)", s)
        if m:
            handle = m.group(1)
            try:
                resp = self.youtube_service.channels().list(part="id", forHandle=handle).execute()
                items = resp.get("items", [])
                if items:
                    return items[0].get("id")
            except HttpError:
                pass
            except Exception as e:
                self.log_message(f"resolve_channel_id: forHandle failed for {handle}: {e}", "warning")

            # fallback to search
            try:
                resp = self.youtube_service.search().list(part="snippet", q=handle, type="channel", maxResults=1).execute()
                items = resp.get("items", [])
                if items:
                    return items[0]["snippet"].get("channelId")
            except Exception as e:
                self.log_message(f"resolve_channel_id: search fallback failed for {handle}: {e}", "warning")
            return None

        # Generic search
        try:
            resp = self.youtube_service.search().list(part="snippet", q=s, type="channel", maxResults=1).execute()
            items = resp.get("items", [])
            if items:
                return items[0]["snippet"].get("channelId")
        except Exception as e:
            self.log_message(f"resolve_channel_id: generic search failed for {s}: {e}", "warning")

        return None
    
    def read_video_ids_from_file(self, path: str) -> List[str]:
        """Read video IDs from file"""
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(path)
        vids = []
        with p.open("r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s:
                    continue
                vid = self.extract_video_id_from_url(s)
                if vid:
                    vids.append(vid)
                else:
                    self.log_message(f"Skipping invalid video entry: {s}", "warning")
        # dedupe preserve order
        seen = set()
        out = []
        for v in vids:
            if v not in seen:
                seen.add(v)
                out.append(v)
        return out
    
    def read_comments_from_file(self, path: str, max_comments=1000) -> List[str]:
        """Read comments from file"""
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
    
    def read_channel_ids_from_file(self, path: str) -> List[str]:
        """Read channel IDs from file"""
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
                cid = self.extract_channel_id_from_url(s)

                # If not found, try resolving with API
                if not cid:
                    cid = self.resolve_channel_id(s)

                if cid:
                    chs.append(cid)
                    self.log_message(f"Resolved {s} → {cid}")
                else:
                    self.log_message(f"Skipping unrecognized or invalid channel entry: {s}", "warning")

        # dedupe preserve order
        seen = set()
        out = []
        for c in chs:
            if c not in seen:
                seen.add(c)
                out.append(c)
        return out
    
    def write_log(self, action, target_id, status, note=""):
        """Write to log file"""
        header_needed = not os.path.exists(LOG_CSV) or os.path.getsize(LOG_CSV) == 0
        with open(LOG_CSV, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if header_needed:
                w.writerow(["timestamp", "action", "target_id", "status", "note"])
            w.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), action, target_id, status, note])
    
    def run_likes_gui(self):
        """Run likes automation with GUI updates"""
        self.log_message("Starting like automation...")
        video_ids = self.read_video_ids_from_file(self.likes_file)
        self.log_message(f"Found {len(video_ids)} unique videos to like")
        
        success_count = 0
        for idx, vid in enumerate(video_ids, start=1):
            if not self.is_running:
                break
                
            if vid in self.processed_like:
                self.log_message(f"[{idx}/{len(video_ids)}] Skipping already-processed like: {vid}")
                continue
                
            progress = idx / len(video_ids)
            self.update_progress(progress, f"Liking {idx}/{len(video_ids)}")
            self.log_message(f"[{idx}/{len(video_ids)}] Liking video: {vid}")
            
            try:
                self.like_video(vid)
                self.write_log("like", vid, "success", "")
                self.processed_like.add(vid)
                self.save_processed("like", self.processed_like)
                self.log_message(f"Liked: {vid}", "success")
                success_count += 1
            except HttpError as e:
                code = getattr(e.resp, "status", "N/A")
                self.log_message(f"HTTP error liking {vid}: {code}", "error")
                self.write_log("like", vid, "failed", f"HTTP {code}")
            except Exception as e:
                self.log_message(f"Error liking {vid}: {e}", "error")
                self.write_log("like", vid, "failed", str(e))
            
            # polite delay
            if idx < len(video_ids) and self.is_running:
                time.sleep(max(0, DELAY_SECONDS + random.uniform(-JITTER, JITTER)))
        
        return success_count
    
    def run_comments_gui(self):
        """Run comments automation with GUI updates"""
        self.log_message("Starting comment automation...")
        comments = self.read_comments_from_file(self.comments_file)
        self.log_message(f"Loaded {len(comments)} comments")
        
        vid = self.extract_video_id_from_url(self.target_video)
        if not vid:
            self.log_message("Could not extract video id from provided target.", "error")
            raise ValueError("Invalid target video")
            
        self.log_message(f"Posting comments to video id: {vid}")
        
        success_count = 0
        for idx, c in enumerate(comments, start=1):
            if not self.is_running:
                break
                
            key = f"{vid}::{hash(c)}"
            if key in self.processed_comment:
                self.log_message(f"[{idx}/{len(comments)}] Skipping already-posted comment: {c[:60]}...")
                continue
                
            progress = idx / len(comments)
            self.update_progress(progress, f"Commenting {idx}/{len(comments)}")
            self.log_message(f"[{idx}/{len(comments)}] Posting comment: {c[:80]}...")
            
            try:
                resp = self.post_top_level_comment(vid, c)
                comment_id = resp.get("id") if isinstance(resp, dict) else ""
                self.write_log("comment", vid, "success", comment_id)
                self.processed_comment.add(key)
                self.save_processed("comment", self.processed_comment)
                self.log_message(f"Posted comment id: {comment_id}", "success")
                success_count += 1
            except HttpError as e:
                code = getattr(e.resp, "status", "N/A")
                self.log_message(f"HTTP error posting comment: {code}", "error")
                self.write_log("comment", vid, "failed", f"HTTP {code}")
            except Exception as e:
                self.log_message(f"Error posting comment: {e}", "error")
                self.write_log("comment", vid, "failed", str(e))
            
            # polite delay
            if idx < len(comments) and self.is_running:
                time.sleep(max(0, DELAY_SECONDS + random.uniform(-JITTER, JITTER)))
        
        return success_count
    
    def run_subscribes_gui(self):
        """Run subscribe automation with GUI updates"""
        self.log_message("Starting subscribe automation...")
        ch_ids = self.read_channel_ids_from_file(self.channels_file)
        self.log_message(f"Found {len(ch_ids)} unique channels to subscribe")
        
        success_count = 0
        for idx, cid in enumerate(ch_ids, start=1):
            if not self.is_running:
                break
                
            if cid in self.processed_subscribe:
                self.log_message(f"[{idx}/{len(ch_ids)}] Skipping already-processed subscribe: {cid}")
                continue
                
            progress = idx / len(ch_ids)
            self.update_progress(progress, f"Subscribing {idx}/{len(ch_ids)}")
            self.log_message(f"[{idx}/{len(ch_ids)}] Subscribing to channel: {cid}")
            
            try:
                resp = self.subscribe_channel(cid)
                sub_id = resp.get("id") if isinstance(resp, dict) else ""
                self.write_log("subscribe", cid, "success", str(sub_id))
                self.processed_subscribe.add(cid)
                self.save_processed("subscribe", self.processed_subscribe)
                self.log_message(f"Subscribed: {cid}", "success")
                success_count += 1
            except HttpError as e:
                status = getattr(e.resp, "status", "N/A")
                self.log_message(f"HTTP error subscribing {cid}: {status}", "error")
                self.write_log("subscribe", cid, "failed", f"HTTP {status}")
            except Exception as e:
                self.log_message(f"Error subscribing {cid}: {e}", "error")
                self.write_log("subscribe", cid, "failed", str(e))
            
            # polite delay
            if idx < len(ch_ids) and self.is_running:
                time.sleep(max(0, DELAY_SECONDS + random.uniform(-JITTER, JITTER)))
        
        return success_count

class GUILogHandler(logging.Handler):
    """Custom log handler to display logs in GUI"""
    def __init__(self, gui_app):
        super().__init__()
        self.gui_app = gui_app
    
    def emit(self, record):
        log_entry = self.format(record)
        level = "info"
        if record.levelno >= logging.ERROR:
            level = "error"
        elif record.levelno >= logging.WARNING:
            level = "warning"
        self.gui_app.after(0, self.gui_app.log_message, log_entry, level)

class SettingsDialog(ctk.CTkToplevel):
    """Settings dialog for configuration"""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("⚙️ Settings - YouTube Automation")
        self.geometry("400x400")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.setup_ui()
    
    def setup_ui(self):
        """Create settings UI"""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(main_frame, text="⚙️ Settings", 
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        # Delay settings
        delay_frame = ctk.CTkFrame(main_frame)
        delay_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(delay_frame, text="Base Delay (seconds):").pack(anchor="w", pady=5)
        self.delay_entry = ctk.CTkEntry(delay_frame)
        self.delay_entry.insert(0, str(DELAY_SECONDS))
        self.delay_entry.pack(fill="x", pady=5)
        
        ctk.CTkLabel(delay_frame, text="Jitter (seconds):").pack(anchor="w", pady=5)
        self.jitter_entry = ctk.CTkEntry(delay_frame)
        self.jitter_entry.insert(0, str(JITTER))
        self.jitter_entry.pack(fill="x", pady=5)
        
        # File management
        file_frame = ctk.CTkFrame(main_frame)
        file_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(file_frame, text="Clear Processed State", 
                     command=self.clear_processed_state).pack(pady=5)
        
        ctk.CTkButton(file_frame, text="View Log File", 
                     command=self.view_log_file).pack(pady=5)
        
        # Save button
        ctk.CTkButton(main_frame, text="Save Settings", 
                     command=self.save_settings).pack(pady=20)
    
    def clear_processed_state(self):
        """Clear the processed state directory"""
        try:
            if os.path.exists(PROCESSED_DIR):
                for file in os.listdir(PROCESSED_DIR):
                    os.remove(os.path.join(PROCESSED_DIR, file))
                messagebox.showinfo("Success", "Processed state cleared")
            else:
                messagebox.showinfo("Info", "No processed state found")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear state: {e}")
    
    def view_log_file(self):
        """Open log file location"""
        try:
            if os.path.exists(LOG_CSV):
                if os.name == 'nt':
                    os.startfile(LOG_CSV)
                else:
                    messagebox.showinfo("Log File", f"Log file: {os.path.abspath(LOG_CSV)}")
            else:
                messagebox.showinfo("Info", "No log file found yet")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open log file: {e}")
    
    def save_settings(self):
        """Save settings"""
        try:
            global DELAY_SECONDS, JITTER
            DELAY_SECONDS = float(self.delay_entry.get())
            JITTER = float(self.jitter_entry.get())
            messagebox.showinfo("Success", "Settings saved")
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for delay and jitter")

def ensure_dir(path):
    """Ensure directory exists"""
    os.makedirs(path, exist_ok=True)

def main():
    """Main application entry point"""
    try:
        app = YouTubeAutomationGUI()
        app.log_message("🔰 YouTube Automation Suite Started", "success")
        app.log_message("💡 Professional YouTube Management Tool", "info")
        app.log_message("⚠️  IMPORTANT: Use responsibly - only operate on accounts you control", "warning")
        app.log_message("📝 Select your input files and actions to begin", "info")
        app.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Failed to start application: {e}")

if __name__ == "__main__":
    main()
