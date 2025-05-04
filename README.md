# YouTube Audio Downloader

A powerful tool to download high-quality audio from YouTube videos and split tracks by timestamps.

## Features

- Downloads the highest quality audio from YouTube videos
- Converts audio to MP3 format
- Extracts timestamps from video descriptions
- Splits audio files into individual tracks based on timestamps
- Automatic dependency installation
- Built-in test program to verify requirements
- Simple command-line interface

## Prerequisites

- Python 3.6 or higher
- ffmpeg (will be installed automatically if missing)
- Internet connection

## Installation

The tool automatically sets up all required dependencies on first run. Simply run the script, and it will:

1. Check if required system packages (ffmpeg, Python venv) are installed
2. Create a Python virtual environment if needed
3. Install required Python packages (yt-dlp, pydub, regex)

You can also explicitly set up dependencies without downloading any videos:

```
./ytd_audio --setup
```

## Usage

```
./ytd_audio [OPTIONS] <youtube-url> [output-directory]
```

### Options

- `--help`: Show help message
- `--no-split`: Download audio only without extracting timestamps or splitting into tracks
- `--setup`: Just install dependencies and exit
- `--bitrate VALUE`: Set audio quality (128k, 192k, 256k, 320k). Default: 320k

### Examples

Download audio to the current directory:
```
./ytd_audio https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

Download audio to a specific directory:
```
./ytd_audio https://www.youtube.com/watch?v=dQw4w9WgXcQ ~/Music
```

Download audio without splitting into tracks (just download the full file):
```
./ytd_audio --no-split https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

Download audio at a specific quality:
```
./ytd_audio --bitrate 192k https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

## Testing

The tool includes a comprehensive test program that verifies all requirements and functionality:

```
./ytd_test
```

The test program checks:

1. **System Requirements**
   - Python 3 installation
   - FFmpeg installation
   - Python venv module availability

2. **Virtual Environment**
   - Virtual environment existence
   - Python and pip in the virtual environment

3. **Python Dependencies**
   - Installation of all required packages (yt-dlp, pydub, regex)

4. **Script Tests**
   - Main script existence and permissions
   - Wrapper script permissions

5. **Python Module Tests**
   - Import tests for required modules

6. **Function Tests**
   - Timestamp extraction function
   - Audio processing functionality
   - yt-dlp executable test

Run this test program if you encounter any issues to diagnose the problem.

## How It Works

This tool uses yt-dlp (a YouTube-DL fork) to:
1. Extract the highest quality audio from YouTube videos
2. Convert the audio to MP3 format
3. Save the file with the video's title as the filename

When using the `--split` option:
1. The tool extracts timestamps from the video description
2. It then creates a subfolder named after the video title
3. The audio is split into individual tracks at the timestamp points
4. Each track is saved as an MP3 file with track number and name

### Supported Timestamp Formats

The tool can recognize various timestamp formats in video descriptions:

#### Format 1: Timestamp First
- `00:00 Track Name`
- `00:00:00 Track Name`
- `00:00 - Track Name`
- `(00:00) Track Name`

Example:
```
00:00 Introduction
02:15 First Movement
08:30 Second Movement
15:45 Final Movement
```

#### Format 2: Track Name First
- `Track Name - 00:00`
- `Track Name - 00:00:00`
- `Track Name: 00:00`

Example:
```
Prelude - 0:00
Ichthus - 1:37
The Serpent's Kiss - 6:16
Mountain - 18:13
```

## Auto-dependency Management

The tool includes an intelligent dependency management system that:

- Checks for required Python packages and installs them if missing
- Verifies system dependencies like ffmpeg are available
- Attempts to install missing system packages (requires sudo on some systems)
- Creates and maintains a Python virtual environment to avoid conflicts

Supported package managers:
- apt (Debian/Ubuntu)
- yum (RHEL/CentOS/Fedora)
- Homebrew (macOS)

## Troubleshooting

If you encounter any issues:

1. Run the test program to diagnose the problem: `./ytd_test`
2. Run the setup to reinstall dependencies: `./ytd_audio --setup`
3. Make sure you have a working internet connection
4. Verify that the YouTube URL is valid
5. Check that you have write permissions to the output directory
6. If no tracks are split, check if the video description contains timestamps
7. If you encounter permission errors during installation, run `./ytd_audio --setup` with sudo

## License

This project is open source and available under the MIT License.