#!/usr/bin/env python3
import os
import sys
import subprocess

# Print environment variables
print("YTDLP_BIN:", os.environ.get("YTDLP_BIN", "Not set"))

# Try to find yt-dlp directly
try:
    result = subprocess.run(["which", "yt-dlp"], check=True, capture_output=True, text=True)
    print("yt-dlp path from which:", result.stdout.strip())
except subprocess.CalledProcessError:
    print("yt-dlp not found in PATH")

# Try to find it in the virtual environment
venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ytd", "venv")
yt_dlp_path = os.path.join(venv_path, "bin", "yt-dlp")
print("Expected yt-dlp path:", yt_dlp_path)
print("Exists:", os.path.exists(yt_dlp_path))

# Print current directory and script directory
print("Current directory:", os.getcwd())
print("Script directory:", os.path.dirname(os.path.abspath(__file__)))