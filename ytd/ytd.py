#!/usr/bin/env python3
"""
YTD - YouTube Downloader
A tool to download high-quality audio from YouTube videos and split by timestamps.
"""

import os
import sys
import json
import subprocess
import re
from pathlib import Path

# Check for required modules
try:
    from pydub import AudioSegment
except ImportError:
    print("Error: Required Python module 'pydub' is not installed.")
    print("Please run './ytd_audio --setup' first to install all dependencies.")
    sys.exit(1)

# Get the path to yt-dlp from environment variable 
# This should be set by the wrapper script
YTDLP_PATH = os.environ.get("YTDLP_BIN")
if not YTDLP_PATH or not Path(YTDLP_PATH).exists():
    print(f"Error: yt-dlp not found at {YTDLP_PATH}")
    print("Please run './ytd_audio --setup' to ensure all dependencies are installed.")
    sys.exit(1)

def time_to_ms(time_str):
    """
    Convert a timestamp string to milliseconds.
    
    Args:
        time_str (str): Timestamp in format "HH:MM:SS" or "MM:SS"
    
    Returns:
        int: Time in milliseconds
    """
    parts = time_str.strip().split(':')
    if len(parts) == 2:  # MM:SS format
        return int(parts[0]) * 60 * 1000 + int(parts[1]) * 1000
    elif len(parts) == 3:  # HH:MM:SS format
        return int(parts[0]) * 3600 * 1000 + int(parts[1]) * 60 * 1000 + int(parts[2]) * 1000
    else:
        raise ValueError(f"Invalid timestamp format: {time_str}")

def sanitize_filename(filename):
    """
    Remove invalid characters from a filename.
    
    Args:
        filename (str): Original filename
    
    Returns:
        str: Sanitized filename
    """
    # Replace invalid characters with underscores
    return re.sub(r'[\\/*?:"<>|]', '_', filename)

def extract_timestamps(description):
    """
    Extract timestamps and track names from a YouTube video description.
    
    Args:
        description (str): Video description
    
    Returns:
        list: List of (time_ms, track_name) tuples
    """
    # First pattern: traditional format "00:00 Track Name" or variations
    pattern1 = r'(?:^|\n)(?:\()?(\d{1,2}:(?:\d{1,2}:)?\d{1,2})(?:\))?(?:[ \t]*[-:][ \t]*)?(.+?)(?=\n|$)'
    
    # Second pattern: reverse format "Track Name - 00:00"
    pattern2 = r'(?:^|\n)(.+?)(?:[ \t]*[-:][ \t]*)(\d{1,2}:(?:\d{1,2}:)?\d{1,2})(?=\n|$)'
    
    # Try both patterns
    matches1 = re.findall(pattern1, description, re.MULTILINE)
    matches2 = re.findall(pattern2, description, re.MULTILINE)
    
    result = []
    
    # Process standard format matches
    for time_str, track_name in matches1:
        try:
            time_ms = time_to_ms(time_str)
            result.append((time_ms, track_name.strip()))
        except ValueError:
            continue
    
    # Process reverse format matches
    for track_name, time_str in matches2:
        try:
            time_ms = time_to_ms(time_str)
            result.append((time_ms, track_name.strip()))
        except ValueError:
            continue
    
    # Remove duplicates and sort by timestamp
    unique_results = []
    seen_times = set()
    
    for time_ms, track_name in sorted(result, key=lambda x: x[0]):
        if time_ms not in seen_times:
            unique_results.append((time_ms, track_name))
            seen_times.add(time_ms)
    
    return unique_results

def get_best_audio_format(url):
    """
    Get the best audio format ID for a YouTube video
    
    Args:
        url (str): YouTube video URL
    
    Returns:
        tuple: (format_id, format_details) or (None, None) if failed
    """
    format_cmd = [
        YTDLP_PATH,
        "-F",
        "--no-playlist",
        url
    ]
    
    try:
        print("Analyzing available audio formats...")
        result = subprocess.run(format_cmd, check=True, capture_output=True, text=True)
        lines = result.stdout.splitlines()
        
        # Look for audio-only formats
        audio_formats = []
        for line in lines:
            if "audio only" in line:
                parts = line.split()
                if len(parts) >= 1:
                    format_id = parts[0]
                    format_ext = parts[1] if len(parts) > 1 else "unknown"
                    bitrate = None
                    codec = "unknown"
                    
                    # Try to find bitrate information
                    for i, part in enumerate(parts):
                        if part.endswith('k') and i+1 < len(parts) and (parts[i+1] == 'https' or parts[i+1] == 'm3u8'):
                            try:
                                bitrate = int(part.rstrip('k'))
                                break
                            except ValueError:
                                pass
                    
                    # Try to find codec information
                    for i, part in enumerate(parts):
                        if part == "audio" and i-1 >= 0 and parts[i-1] == "only" and i+1 < len(parts):
                            codec = parts[i+1]
                            break
                    
                    format_details = f"{format_id} - {format_ext} - {codec} - {bitrate}k"
                    audio_formats.append((format_id, bitrate, format_details))
                    print(f"Found audio format: {format_details}")
        
        # Sort by bitrate (highest first) and return the best format ID
        if audio_formats:
            audio_formats.sort(key=lambda x: x[1] if x[1] is not None else 0, reverse=True)
            best_format = audio_formats[0]
            print(f"\nSelected highest quality format: {best_format[2]}")
            return best_format[0], best_format[2]
        
        print("No audio formats found.")
        return None, None
    
    except subprocess.CalledProcessError as e:
        print(f"Error analyzing formats: {e}")
        return None, None

def download_audio_with_info(url, output_dir=None, bitrate="320k"):
    """
    Download the highest quality audio from a YouTube video and get video info.
    
    Args:
        url (str): YouTube video URL
        output_dir (str, optional): Directory to save the file. Defaults to current directory.
        bitrate (str, optional): Target MP3 bitrate. Defaults to "320k".
    
    Returns:
        tuple: (audio_file_path, video_title, description) or (None, None, None) if failed
    """
    if not output_dir:
        output_dir = os.getcwd()
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # First, get video info
    info_command = [
        YTDLP_PATH,
        "--dump-json",
        "--no-playlist",
        url
    ]
    
    try:
        info_result = subprocess.run(info_command, check=True, capture_output=True, text=True)
        video_info = json.loads(info_result.stdout)
        video_title = video_info.get('title', 'Unknown Title')
        description = video_info.get('description', '')
        
        # Try to get the best audio format
        best_format_id, best_format_details = get_best_audio_format(url)
        
        # Format: extract audio only, best quality, convert to mp3
        audio_filename = f"{sanitize_filename(video_title)}.mp3"
        audio_file_path = output_dir / audio_filename
        
        download_command = [
            YTDLP_PATH,
        ]
        
        # If we found a specific best format, use it
        if best_format_id:
            download_command.extend(["-f", best_format_id])
            print(f"Using format: {best_format_details}")
        
        download_command.extend([
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", bitrate,
            "--output", str(audio_file_path),
            "--no-playlist",
            url
        ])
        
        print(f"Downloading audio from: {url}")
        print(f"Target quality: MP3 {bitrate}")
        print(f"Output file: {audio_file_path}")
        
        subprocess.run(download_command, check=True)
        
        # Get the actual bitrate of the downloaded file
        try:
            ffprobe_cmd = [
                "ffprobe", 
                "-v", "error", 
                "-select_streams", "a:0", 
                "-show_entries", "stream=bit_rate", 
                "-of", "default=noprint_wrappers=1:nokey=1", 
                str(audio_file_path)
            ]
            result = subprocess.run(ffprobe_cmd, check=True, capture_output=True, text=True)
            actual_bitrate = int(result.stdout.strip()) // 1000
            print(f"\nActual bitrate of MP3 file: {actual_bitrate}k")
        except (subprocess.CalledProcessError, ValueError) as e:
            print(f"Could not determine actual bitrate: {e}")
            
        return str(audio_file_path), video_title, description
    
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Error downloading audio or getting video info: {e}", file=sys.stderr)
        return None, None, None

def split_audio_by_timestamps(audio_file, timestamps, output_dir, bitrate="320k"):
    """
    Split audio file according to timestamps.
    
    Args:
        audio_file (str): Path to the audio file
        timestamps (list): List of (time_ms, track_name) tuples
        output_dir (str): Directory to save the split files
        bitrate (str, optional): Target MP3 bitrate for the split files. Defaults to "320k".
    
    Returns:
        list: List of created files
    """
    if not timestamps:
        return []
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load audio file
    try:
        audio = AudioSegment.from_file(audio_file, format="mp3")
    except Exception as e:
        print(f"Error loading audio file: {e}", file=sys.stderr)
        return []
    
    # Add end timestamp
    timestamps.append((len(audio), "End"))
    
    created_files = []
    
    # Split audio by timestamps
    for i in range(len(timestamps) - 1):
        start_time = timestamps[i][0]
        end_time = timestamps[i+1][0]
        track_name = timestamps[i][1]
        
        # Extract the segment
        segment = audio[start_time:end_time]
        
        # Sanitize track name for filename
        safe_track_name = sanitize_filename(track_name)
        
        # Include track number in filename
        track_number = f"{i+1:02d}"
        output_file = output_dir / f"{track_number} - {safe_track_name}.mp3"
        
        # Export segment to file with the specified bitrate
        segment.export(str(output_file), format="mp3", bitrate=bitrate)
        created_files.append(str(output_file))
        
        print(f"Created: {output_file}")
    
    return created_files

def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: ytd.py <youtube-url> [output-directory] [--no-split] [--bitrate BITRATE]", file=sys.stderr)
        print("Options:", file=sys.stderr)
        print("  --no-split        Don't extract timestamps or split audio (download only)", file=sys.stderr)
        print("  --bitrate BITRATE Target MP3 bitrate (default: 320k)", file=sys.stderr)
        sys.exit(1)
    
    # Find the URL in the arguments (should be the first non-option argument)
    url = None
    output_dir = None
    split_tracks = True  # Default to splitting
    bitrate = "320k"  # Default to high quality
    
    # Process arguments
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--no-split':
            split_tracks = False
            i += 1
        elif arg == '--bitrate' and i + 1 < len(sys.argv):
            bitrate = sys.argv[i + 1]
            i += 2
        elif not arg.startswith('--'):
            if url is None:
                url = arg
                i += 1
            elif output_dir is None:
                output_dir = arg
                i += 1
            else:
                i += 1
        else:
            i += 1
    
    if url is None:
        print("Error: No YouTube URL provided.", file=sys.stderr)
        print("Usage: ytd.py <youtube-url> [output-directory] [--no-split] [--bitrate BITRATE]", file=sys.stderr)
        sys.exit(1)
    
    # Download audio and get video info
    audio_file, video_title, description = download_audio_with_info(url, output_dir, bitrate)
    
    if not audio_file:
        sys.exit(1)
    
    # If splitting tracks is requested
    if split_tracks and description:
        # Create a subdirectory for the split tracks using the video title
        if output_dir:
            tracks_dir = Path(output_dir) / sanitize_filename(video_title)
        else:
            tracks_dir = Path(os.getcwd()) / sanitize_filename(video_title)
        
        # Extract timestamps from the description
        timestamps = extract_timestamps(description)
        
        if timestamps:
            print(f"Found {len(timestamps)} timestamps in the video description.")
            # Pass the same bitrate used for downloading to the splitting function
            print(f"Splitting tracks with bitrate: {bitrate}")
            split_files = split_audio_by_timestamps(audio_file, timestamps, tracks_dir, bitrate)
            
            if split_files:
                print(f"Successfully split audio into {len(split_files)} tracks in: {tracks_dir}")
            else:
                print("Failed to split audio file.")
        else:
            print("No timestamps found in the video description.")
    
    sys.exit(0)

if __name__ == "__main__":
    main()