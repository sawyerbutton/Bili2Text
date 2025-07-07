# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bili2Text is a collection of Python scripts for transcribing Bilibili videos using OpenAI Whisper. The project focuses on simplicity and functionality, providing proven video downloading and transcription capabilities through a set of well-tested scripts.

## 🧹 Project Status: Clean Architecture with Legacy Support

**Current Status**: The project has been reorganized with clear separation between modern modular code and legacy scripts.

**Project Philosophy**:
- ✅ **Clear separation** between new and legacy code
- ✅ **Modular design** with reusable core components
- ✅ **Backward compatibility** - all legacy scripts remain functional
- ✅ **Professional structure** following Python best practices
- ✅ **Focus on core value**: video transcription with improved maintainability

## 📁 New Project Structure

```
Bili2Text/
├── README.md                      # 📖 Project documentation
├── CLAUDE.md                      # 🤖 Claude Code instructions
├── LICENSE                        # ⚖️ License file
│
├── bili2text_v2/                  # 🚀 Modern modular code (NEW)
│   ├── bili2text.py               #   Main CLI entry point
│   ├── simple_transcribe.py       #   Simple transcription script
│   ├── core/                      #   🔧 Reusable core modules
│   │   ├── __init__.py
│   │   ├── whisper_transcriber.py #     Unified transcription logic
│   │   ├── bilibili_downloader.py #     Unified download logic  
│   │   ├── markdown_generator.py  #     Unified output generation
│   │   └── file_manager.py        #     Unified file operations
│   ├── workflows/                 #   ⚡ High-level workflows
│   │   ├── __init__.py
│   │   ├── batch_transcribe.py    #     Batch processing workflow
│   │   ├── infinity_workflow.py   #     InfinityAcademy specialized workflow
│   │   └── ref_info_workflow.py   #     Reference info series workflow
│   └── tools/                     #   🛠️ Setup and management tools
│       ├── __init__.py
│       ├── setup.py               #     Project setup and dependency installation
│       └── model_downloader.py    #     Whisper model management
│
└── legacy/                        # 📂 Legacy scripts (moved to root)
    ├── README.md                  #   Legacy documentation
    ├── README_InfinityAcademy.md  #   InfinityAcademy specific docs
    ├── main.py                    #   Original main script
    ├── download_videos.py         #   Video download script
    ├── download_infinityacademy_audio.py  # Audio download script
    ├── transcribe_infinityacademy_audio.py # Transcription script
    ├── get_all_dynamics_infinityacademy.py # Dynamics fetcher
    ├── get_ref_from_dynamics.py   #   Reference extractor
    ├── install_dependencies.py    #   Legacy dependency installer
    ├── install_dependencies.sh    #   Shell installer
    └── download_whisper_model.py  #   Legacy model downloader
```

## Development Commands

### Environment Setup
```bash
# Create virtual environment (recommended)
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate  # Windows

# Install dependencies and setup project (RECOMMENDED)
python bili2text_v2/tools/setup.py
# or with specific Whisper model
python bili2text_v2/tools/setup.py --model medium
```

### 🎯 New Modular Architecture Usage (v2)

#### Unified CLI Interface (Recommended)
```bash
# One-command setup
python bili2text_v2/bili2text.py setup

# Simple transcription test
python bili2text_v2/bili2text.py simple

# Batch transcription workflow
python bili2text_v2/bili2text.py batch

# InfinityAcademy complete workflow  
python bili2text_v2/bili2text.py infinity

# Reference info series workflow
python bili2text_v2/bili2text.py ref-info
```

#### Direct Module Access
```bash
# Simple transcription test
python bili2text_v2/simple_transcribe.py

# Batch transcription workflow
python bili2text_v2/workflows/batch_transcribe.py

# InfinityAcademy complete workflow  
python bili2text_v2/workflows/infinity_workflow.py

# Reference info series workflow
python bili2text_v2/workflows/ref_info_workflow.py
```

#### Tools and Management
```bash
# Unified CLI (Recommended)
python bili2text_v2/bili2text.py setup
python bili2text_v2/bili2text.py model --list
python bili2text_v2/bili2text.py model --download medium

# Direct tool access
python bili2text_v2/tools/setup.py
python bili2text_v2/tools/model_downloader.py --download medium
python bili2text_v2/tools/model_downloader.py --list
```

#### Advanced Workflows
```bash
# Batch workflow with custom settings
python bili2text_v2/workflows/batch_transcribe.py

# InfinityAcademy - download only
python bili2text_v2/workflows/infinity_workflow.py --mode download

# InfinityAcademy - transcribe only  
python bili2text_v2/workflows/infinity_workflow.py --mode transcribe

# Reference info - latest video
python bili2text_v2/workflows/ref_info_workflow.py --target latest

# Reference info - specific video
python bili2text_v2/workflows/ref_info_workflow.py --target BV1234567890
```

### 📂 Legacy Scripts (Still Available)
```bash
# Original scripts are still available for compatibility
python legacy/main.py
python legacy/download_videos.py
python legacy/transcribe_infinityacademy_audio.py
python legacy/get_all_dynamics_infinityacademy.py
python legacy/get_ref_from_dynamics.py
python legacy/install_dependencies.py
python legacy/download_whisper_model.py
```

## Architecture Overview

### Modular Design with Clean Separation (v2)
The new version uses a modular architecture with clear separation of concerns:

```
bili2text_v2/
├── core/                           # 🔧 Reusable core modules
│   ├── whisper_transcriber.py      #   Unified transcription logic
│   ├── bilibili_downloader.py      #   Unified download logic  
│   ├── markdown_generator.py       #   Unified output generation
│   └── file_manager.py             #   Unified file operations
├── workflows/                      # ⚡ High-level workflows
│   ├── batch_transcribe.py         #   Batch processing workflow
│   ├── infinity_workflow.py        #   InfinityAcademy specialized workflow
│   └── ref_info_workflow.py        #   Reference info series workflow
├── tools/                          # 🛠️ Setup and management tools
│   ├── setup.py                    #   Project setup and dependency installation
│   └── model_downloader.py         #   Whisper model management
├── bili2text.py                    # 🎯 Main CLI entry point
└── simple_transcribe.py            # 📝 Simple entry script
```

### Core Modules (v2)

#### `core/whisper_transcriber.py`
- **Unified transcription logic** for all Whisper operations
- **Model management** and device selection
- **Batch processing** capabilities
- **Text processing** and standardization

#### `core/bilibili_downloader.py`
- **B站 API integration** for video/audio downloading
- **User content discovery** (videos, dynamics)
- **Concurrent downloads** with rate limiting
- **Error handling** and retry mechanisms

#### `core/markdown_generator.py`
- **Unified output formatting** for all transcription results
- **Video embedding** templates for B站 and YouTube
- **Batch summary** generation
- **Customizable** tags and metadata

#### `core/file_manager.py`
- **Directory management** and setup
- **Status tracking** (downloaded, transcribed, processed)
- **Video information** storage and retrieval
- **File operations** with conflict resolution

### Workflows (v2)

#### `workflows/batch_transcribe.py`
- **General-purpose** batch transcription workflow
- **Configurable** video URL lists
- **Complete pipeline**: download → transcribe → save

#### `workflows/infinity_workflow.py`  
- **InfinityAcademy specialized** workflow
- **User content discovery** and bulk processing
- **Modular execution**: download-only, transcribe-only, or full workflow

#### `workflows/ref_info_workflow.py`
- **Reference info series** specialized processing
- **Latest video** auto-detection
- **Title normalization** and series recognition

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

### 🚀 Quick Start (New Users - Recommended)
1. Clone the repository
2. Set up Python environment (Python 3.9+)
3. **One-command setup**: `python bili2text_v2/tools/setup.py`
4. **Test installation**: `python bili2text_v2/simple_transcribe.py`
5. **Start with workflows**: `python bili2text_v2/workflows/batch_transcribe.py`

### 📚 Usage Guide

#### For New Users (v2 - Recommended)
- **First time**: `python bili2text_v2/tools/setup.py` (installs everything)
- **Quick test**: `python bili2text_v2/simple_transcribe.py` 
- **Batch processing**: `python bili2text_v2/workflows/batch_transcribe.py`

#### For InfinityAcademy Content (v2)
- **Complete workflow**: `python bili2text_v2/workflows/infinity_workflow.py`
- **Download only**: `python bili2text_v2/workflows/infinity_workflow.py --mode download`
- **Transcribe only**: `python bili2text_v2/workflows/infinity_workflow.py --mode transcribe`

#### For Reference Info Series (v2)
- **Latest video**: `python bili2text_v2/workflows/ref_info_workflow.py`
- **Specific video**: `python bili2text_v2/workflows/ref_info_workflow.py --target BV1234567890`

#### Model Management (v2)
- **List available**: `python bili2text_v2/tools/model_downloader.py --list`
- **Download model**: `python bili2text_v2/tools/model_downloader.py --download medium`
- **Check downloaded**: `python bili2text_v2/tools/model_downloader.py --downloaded`

#### Legacy Usage (Still Supported)
- **Legacy main**: `python legacy/main.py`
- **Legacy setup**: `python legacy/install_dependencies.py`
- **Legacy InfinityAcademy**: `python legacy/transcribe_infinityacademy_audio.py`

### 🎯 Benefits of New Architecture
- **Clear separation**: New vs legacy code clearly organized
- **No code duplication**: All functionality shared through core modules
- **Consistent behavior**: Same transcription quality across all workflows
- **Easy maintenance**: Update core logic in one place
- **Extensible**: Easy to add new workflows using existing modules
- **Backward compatible**: All legacy scripts still work
- **Professional structure**: Follows Python project conventions

## Migration Guide

### For Existing Users
- **Legacy scripts continue to work** - no immediate changes needed
- **Gradually migrate** to v2 for better features and maintenance
- **Both versions** can coexist safely

### For New Projects
- **Start with v2**: Use `bili2text_v2/` directory for all new work
- **Use unified CLI**: `python bili2text_v2/bili2text.py` for best experience
- **Reference legacy**: Check `legacy/` for historical implementations

## Important File Paths
- **New code**: All in `bili2text_v2/` directory
- **Legacy code**: All in `legacy/` directory  
- **Working directories**: Created at project root (audio/, video/, result/, temp/)
- **Model cache**: `.cache/whisper/` in project root