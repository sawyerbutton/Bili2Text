# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bili2Text is a Bilibili video transcription tool with dual architecture:
- **Web Application**: Flask + SocketIO with real-time WebSocket updates
- **CLI Tool**: Command-line interface for batch processing and automation
- **Core Technology**: OpenAI Whisper for speech-to-text transcription

## Essential Commands

### Quick Start
```bash
# Web application (development)
python run.py --debug

# CLI tool (using conda - recommended)
conda activate bili2text-cli
./bili2text.sh audio --url "https://www.bilibili.com/video/BV1234567890"

# GPU batch transcription
conda activate bili2text-gpu
./scripts/transcribe/stable_transcribe.sh
```

### Environment Setup
```bash
# CLI with conda (recommended for isolation)
conda create -n bili2text-cli python=3.11 -y
conda activate bili2text-cli
pip install bilibili-api-python bilix httpx beautifulsoup4 lxml openai-whisper
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# GPU environment (for batch transcription)
conda create -n bili2text-gpu python=3.11 -y
conda activate bili2text-gpu
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install openai-whisper

# Web application (venv)
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements/cli-cpu.txt  # or cli-gpu.txt for GPU
```

### Common Development Tasks
```bash
# Run specific CLI commands
python -m cli.main audio --url "VIDEO_URL" --model medium
python -m cli.main video --url "VIDEO_URL"
python -m cli.main user-videos --uid 3546737620814672
python -m cli.main gpu-transcribe --input video.mp4 --model large-v3

# Batch operations
python scripts/transcribe/batch_transcribe_gpu_improved.py  # Full batch with progress
python scripts/transcribe/resume_transcribe.py              # Resume interrupted batch

# Test GPU availability
python -m cli.test_gpu

# Web app with specific configurations
python run.py --production --host 0.0.0.0 --port 8000

# Docker deployment
docker-compose -f deployment/docker/docker-compose.yml up -d
```

## Architecture Insights

### Dual-Mode Execution Pattern
The project separates Web and CLI modes but shares core functionality:
```
Project Root
├── cli/                    # CLI entry points (main.py handles subcommands)
│   ├── main.py            # Unified CLI with argparse subcommands
│   ├── download_audio.py  # B站音频下载 + 自动转录
│   ├── download_video.py  # B站视频下载
│   └── download_user_videos.py  # UP主批量下载
├── webapp/                 # Web application
│   ├── app.py             # Flask factory + SocketIO setup
│   ├── api/routes.py      # RESTful endpoints
│   └── core/              # Business logic (task_manager, file_manager)
├── src/                    # Shared libraries (both modes use this)
│   ├── transcriber/       # Whisper transcription engine
│   └── downloader/        # Bilibili download utilities
└── scripts/               # Standalone utility scripts
    └── transcribe/        # GPU batch transcription scripts
```

### Key Technical Decisions

1. **Conda vs Venv**: Project uses conda for CLI tools (better isolation, easier GPU setup) and venv for web app
2. **GPU Transcription**: Separate conda environment (`bili2text-gpu`) to avoid dependency conflicts
3. **Batch Processing**: Uses temporary files to handle special characters in Chinese filenames
4. **Resume Capability**: Scripts check `storage/results/gpu_transcripts/` for existing files before processing

### Storage Layout
```
storage/
├── video/                  # Downloaded videos (organized by UP user)
├── audio/                  # Extracted audio files
├── results/
│   ├── gpu_transcripts/   # GPU batch transcription outputs
│   └── result/            # CLI transcription outputs
└── temp/                   # Temporary processing files
```

### Critical Files

- `cli/main.py`: CLI argument parsing and subcommand routing
- `webapp/app.py`: Flask application factory with SocketIO
- `scripts/transcribe/stable_transcribe.sh`: Production-ready batch transcription
- `scripts/transcribe/resume_transcribe.py`: Handles interrupted batch jobs
- `config/models/whisper_models.json`: Model configurations and download URLs

### Whisper Model Selection
- `tiny`: Fast but less accurate (39MB)
- `base`: Good balance for Chinese (74MB) - default for batch
- `medium`: Recommended for quality (769MB)
- `large-v3`: Best accuracy, needs GPU (1550MB)

### Common Issues & Solutions

1. **Special characters in filenames**: Scripts use `safe_filename()` function and temporary files
2. **FP16 GPU errors**: Use `--compute-type float32` instead of default fp16
3. **Conda environment not found**: Run `conda create -n bili2text-gpu python=3.11` first
4. **WebSocket disconnections**: Frontend has automatic reconnection with exponential backoff

## Database & State Management

- SQLite database at `webapp/data/bili2text.db`
- Task states: pending, processing, completed, failed
- WebSocket rooms for real-time updates per task
- System monitoring updates every 5 seconds

## Deployment Notes

- Docker deployment uses Nginx reverse proxy + Gunicorn
- Production mode disables debug and uses threading for SocketIO
- Storage directories are volume-mounted in Docker
- Redis optional for session management in production