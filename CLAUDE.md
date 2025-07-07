# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bili2Text is a collection of Python scripts for transcribing Bilibili videos using OpenAI Whisper. The project focuses on simplicity and functionality, providing proven video downloading and transcription capabilities through a set of well-tested scripts.

## 🧹 Project Status: Simplified and Focused

**Current Status**: The project has been simplified to focus on core functionality through proven scripts.

**Project Philosophy**:
- ✅ Simplicity over complexity
- ✅ Proven functionality over theoretical architecture  
- ✅ Single-purpose scripts that work reliably
- ✅ Focus on core value: video transcription

## Development Commands

### Environment Setup
```bash
# Create virtual environment (recommended)
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate  # Windows

# Install dependencies (check each script for requirements)
pip install openai-whisper yt-dlp requests bilix
```

### Running the Scripts

#### Core Transcription
```bash
# Simple transcription
python Original_Code/simple_transcribe.py

# Main batch transcription  
python Original_Code/main.py

# InfinityAcademy specific transcription
python Original_Code/transcribe_infinityacademy_audio.py
```

#### Video Download
```bash
# Download videos
python Original_Code/download_videos.py

# Download InfinityAcademy videos
python Original_Code/download_infinityacademy_audio.py
```

#### Content Discovery
```bash
# Get dynamics from specific UP
python Original_Code/get_all_dynamics_infinityacademy.py

# Extract references from dynamics
python Original_Code/get_ref_from_dynamics.py
```

#### Setup and Utilities
```bash
# Install dependencies automatically
python Original_Code/install_dependencies.py
# or
bash Original_Code/install_dependencies.sh

# Download Whisper models
python Original_Code/download_whisper_model.py
```

## Architecture Overview

### Simple Script Collection
The project consists of focused, single-purpose scripts in the `Original_Code/` directory:
- **Core Scripts**: Proven transcription and download functionality
- **No Complex Architecture**: Each script is self-contained and focused
- **Direct Approach**: Minimal abstractions, maximum clarity

### Key Scripts

#### Transcription Scripts
- `simple_transcribe.py`: Basic transcription functionality
- `main.py`: Batch processing with file management
- `transcribe_infinityacademy_audio.py`: Specialized for InfinityAcademy content

#### Download Scripts  
- `download_videos.py`: General video downloading
- `download_infinityacademy_audio.py`: Audio extraction and downloading

#### Content Discovery
- `get_all_dynamics_infinityacademy.py`: Extract dynamics from UP主
- `get_ref_from_dynamics.py`: Parse references from dynamic content

#### Utilities
- `install_dependencies.py/sh`: Dependency management
- `download_whisper_model.py`: Model downloading

## Whisper Models Available
- `tiny`: Fastest, lower accuracy (39MB)
- `base`: Balanced performance (74MB)  
- `medium`: Recommended for most use cases (769MB)
- `large-v3`: Highest accuracy (1550MB)

## Storage and Output
Each script manages its own file organization:
- Audio files are typically saved to `audio/` subdirectories
- Results are saved as text files alongside audio files
- Temporary files are cleaned up automatically

## Error Handling
Scripts include basic error handling:
- Network retry mechanisms for downloads
- File existence checks
- Basic logging to console

## Development Notes
- Each script is designed to be run independently
- Configuration is typically done through script modification
- File paths and settings are script-specific
- Scripts have been tested and proven to work reliably
- Focus on practical functionality over theoretical architecture

## Getting Started
1. Clone the repository
2. Set up Python environment (Python 3.9+)
3. Install basic dependencies: `pip install openai-whisper yt-dlp requests bilix`
4. Navigate to `Original_Code/` directory
5. Run the script that matches your needs
6. Check the script's output directory for results

## Script Selection Guide
- **New to the project**: Start with `simple_transcribe.py`
- **Batch processing**: Use `main.py`
- **Video downloading**: Use `download_videos.py`
- **InfinityAcademy content**: Use the specialized `*_infinityacademy_*` scripts
- **Content discovery**: Use `get_all_dynamics_infinityacademy.py`

The beauty of this approach is that each script does one thing well, and you can easily understand and modify them as needed.