# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bili2Text is a powerful video transcription tool for Bilibili videos, built with dual architecture:
- **Web Application**: Modern Flask-based web interface with WebSocket real-time updates
- **CLI Tool**: Command-line interface for batch processing and automation

The project uses OpenAI Whisper for speech recognition and provides comprehensive video downloading and transcription capabilities.

## 🚧 Project Status: Under Refactoring

**Current Status**: The project is undergoing comprehensive refactoring to improve code quality, security, and maintainability.

**Refactoring Goals**:
- ✅ Clean up codebase (216+ MB saved through file cleanup)
- 🔄 Fix critical security vulnerabilities (URL validation, path traversal)
- 🔄 Eliminate code duplication (500+ lines of repeated code)
- 🔄 Improve architecture (decouple modules, implement shared services)
- 🔄 Standardize error handling and configuration management

**Known Issues Being Addressed**:
- TaskManager methods are too long (150+ lines)
- Security vulnerabilities in URL validation and file path handling
- Code duplication between CLI and Web modules
- Reverse dependencies violating layered architecture
- Memory issues with large file transcription

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

# Code quality analysis
pylint src/ cli/ webapp/
mypy src/ cli/ webapp/

# Security scanning
bandit -r src/ cli/ webapp/
safety check

# Clean up development files
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name ".DS_Store" -type f -delete
```

### Refactoring Commands
```bash
# Phase 1: Security fixes (Week 1-2)
# Fix URL validation security
# Fix file path traversal vulnerabilities
# Refactor TaskManager methods

# Phase 2: Architecture improvement (Week 3-4)
# Extract shared transcription service
# Extract shared download service
# Implement event bus pattern

# Phase 3: Standardization (Week 5-6)
# Unify configuration management
# Standardize error handling
# Optimize dependency layers
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
- `cli/get_dynamics.py`: Dynamic content retrieval

#### Shared Libraries
- `src/transcriber/`: Whisper-based transcription engine (🔄 Under refactoring)
- `src/downloader/`: Video/audio download utilities (🔄 Under refactoring) 
- `src/utils/`: Common utility functions (✅ Path management refactored)
- `src/models/`: Data models and schemas (🔄 To be implemented)
- `src/events/`: Event bus for decoupled communication (🔄 To be implemented)
- `src/exceptions/`: Unified exception handling (🔄 To be implemented)

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

## Refactoring Progress Tracker

### Phase 1: Security & Architecture Fixes (🔄 In Progress)
- [ ] **P0-1**: Fix URL validation security vulnerabilities
- [ ] **P0-2**: Fix file path traversal vulnerabilities  
- [ ] **P0-3**: Refactor TaskManager._process_task method (150+ lines → <30 lines)
- [ ] **P1-4**: Implement event bus to resolve reverse dependencies
- [ ] **P1-5**: Extract shared Whisper transcription service
- [ ] **P1-6**: Extract shared Bilibili download service

### Phase 2: Code Quality & Performance (📋 Planned)
- [ ] **P1-7**: Implement streaming transcription for large files
- [ ] **P2-8**: Optimize thread pool configuration
- [ ] **P2-9**: Unify configuration management system
- [ ] **P2-10**: Standardize exception handling across modules

### Phase 3: System Optimization (📋 Planned)
- [ ] **P2-11**: Optimize dependency layers (CLI/Web separation)
- [ ] **P3-12**: Refactor API layer by business domains
- [ ] **P3-13**: Modernize frontend JavaScript architecture

### Success Metrics
- **Code Quality**: Reduce duplication from 15% to <3%
- **Security**: Zero critical vulnerabilities 
- **Performance**: 30% memory optimization for large files
- **Maintainability**: Average method length <25 lines
- **Test Coverage**: Increase from 0% to 80%

## Development Notes
- The project supports both development and production modes
- WebSocket heartbeat and reconnection are handled automatically
- File cleanup and storage management are automated
- System monitoring includes CPU, memory, and disk usage tracking
- Docker deployment includes Nginx reverse proxy and Redis caching
- **🚧 Refactoring in progress**: Follow the phase-based approach for contributions