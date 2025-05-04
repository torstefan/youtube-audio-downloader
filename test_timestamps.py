#!/usr/bin/env python3

import sys
import os
import re

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

def extract_timestamps_current(description):
    """
    Original timestamp extraction function.
    """
    # Match patterns like "00:00 Track Name" or "00:00:00 Track Name"
    # Also handles variations with - or : separators and timestamps with parentheses
    timestamp_pattern = r'(?:^|\n)(?:\()?(\d{1,2}:(?:\d{1,2}:)?\d{1,2})(?:\))?(?:[ \t]*[-:][ \t]*)?(.+?)(?=\n\d{1,2}:|$)'
    matches = re.findall(timestamp_pattern, description, re.MULTILINE)
    
    if not matches:
        return []
    
    result = []
    for time_str, track_name in matches:
        try:
            time_ms = time_to_ms(time_str)
            result.append((time_ms, track_name.strip()))
        except ValueError:
            continue
    
    return sorted(result, key=lambda x: x[0])

def extract_timestamps_enhanced(description):
    """
    Enhanced timestamp extraction function that also handles "Track Name - 00:00" format.
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

# Test with the example tracklist
example = """Predlude - 0:00
Ichthus - 1:37
The Serpent's Kiss - 6:16
Mountain - 18:13
Theocracy - 23:01
The Healing Hand - 29:02
Sinner - 40:38
New Jerusalem - 46:47
The Victory Dance - 51:57
Twist of Fate - 56:59"""

print("Testing with current extraction function:")
current_results = extract_timestamps_current(example)
if current_results:
    for i, (time_ms, name) in enumerate(current_results):
        seconds = time_ms // 1000
        minutes = seconds // 60
        seconds %= 60
        print(f"{i+1:2d}. {name} - {minutes}:{seconds:02d}")
else:
    print("Current function found no timestamps")

print("\nTesting with enhanced extraction function:")
enhanced_results = extract_timestamps_enhanced(example)
if enhanced_results:
    for i, (time_ms, name) in enumerate(enhanced_results):
        seconds = time_ms // 1000
        minutes = seconds // 60
        seconds %= 60
        print(f"{i+1:2d}. {name} - {minutes}:{seconds:02d}")
else:
    print("Enhanced function found no timestamps")