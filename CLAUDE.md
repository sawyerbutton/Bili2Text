# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bili2Text is a powerful video transcription tool for Bilibili videos, built with dual architecture:
- **Web Application**: Modern Flask-based web interface with WebSocket real-time updates
- **CLI Tool**: Command-line interface for batch processing and automation

The project uses OpenAI Whisper for speech recognition and provides comprehensive video downloading and transcription capabilities.

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements/web.txt    # For web app
pip install -r requirements/cli.txt    # For CLI only
pip install -r requirements/dev.txt    # For development
```

### Running the Application

#### Web Application
```bash
# Development mode
python run.py --debug

# Production mode
python run.py --production --host 0.0.0.0 --port 8000

# Quick application test
python test_app.py
```

#### CLI Tool
```bash
# Audio transcription
python -m cli.main audio --url "https://www.bilibili.com/video/BV1234567890" --model medium

# Video download only
python -m cli.main video --url "https://www.bilibili.com/video/BV1234567890"

# Batch download all videos from a UP user (New)
python -m cli.main user-videos --uid 3546737620814672  # By UID
python -m cli.main user-videos --user "UP主名称" --audio-only  # By username

# Batch processing
python -m cli.main batch --input-dir ./videos --output-dir ./results --type audio
```

### Docker Deployment
```bash
# Quick deployment (Linux/macOS)
chmod +x deploy.sh && ./deploy.sh deploy

# Quick deployment (Windows)
.\deploy.ps1 deploy

# Manual Docker commands
docker-compose up -d
docker-compose logs -f bili2text-web
```

### Development Tools
```bash
# Code formatting
black src/ cli/ webapp/
isort src/ cli/ webapp/

# Run tests
pytest tests/

# Install pre-commit hooks
pre-commit install
```

## Architecture Overview

### Dual-Mode Design
The project implements a shared-core architecture where both web and CLI applications use common libraries from `src/`:
- **CLI Mode** (`cli/`): Command-line tools for automation and batch processing
- **Web Mode** (`webapp/`): Full-featured web application with real-time updates
- **Shared Core** (`src/`): Common transcription, downloading, and utility functions

### Key Components

#### Web Application Structure
- `webapp/app.py`: Flask application factory with SocketIO integration
- `webapp/api/routes.py`: RESTful API endpoints for task management
- `webapp/core/`: Core business logic (task management, file handling, system monitoring)
- `webapp/static/`: Frontend assets (HTML templates, CSS, JavaScript)

#### CLI Tool Structure
- `cli/main.py`: Unified CLI entry point with subcommands
- `cli/download_audio.py`: Audio transcription functionality
- `cli/download_video.py`: Video download functionality
- `cli/download_user_videos.py`: Batch download all videos from UP users
- `cli/get_dynamics.py`: Dynamic content retrieval

#### Shared Libraries
- `src/transcriber/`: Whisper-based transcription engine
- `src/downloader/`: Video/audio download utilities
- `src/utils/`: Common utility functions
- `src/models/`: Data models and schemas

### Configuration System
- `config/app/`: Environment-specific configurations
- `config/models/`: Whisper model configurations
- Multiple requirement files for different deployment scenarios

### Real-time Communication
- WebSocket integration for live progress updates
- Task status broadcasting to connected clients
- System monitoring with real-time performance metrics

## Whisper Models Available
- `tiny`: Fastest, lower accuracy (39MB)
- `base`: Balanced performance (74MB)
- `medium`: Recommended for most use cases (769MB)
- `large-v3`: Highest accuracy (1550MB)

## Storage Structure
```
storage/
├── audio/     # Downloaded audio files
├── video/     # Downloaded video files
├── results/   # Transcription results
└── temp/      # Temporary processing files
```

## Database Schema
- SQLite database with Task, SystemStatus, and TaskStatistics models
- Automatic database initialization on first run
- Migration support through SQLAlchemy

## Error Handling
The project implements comprehensive error handling:
- Frontend: Global error handler with retry mechanisms and user-friendly messages
- Backend: Unified exception middleware with structured error responses
- Test page available at `/error-test` for error handling verification

## Development Notes
- The project supports both development and production modes
- WebSocket heartbeat and reconnection are handled automatically
- File cleanup and storage management are automated
- System monitoring includes CPU, memory, and disk usage tracking
- Docker deployment includes Nginx reverse proxy and Redis caching