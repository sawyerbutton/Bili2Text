# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bili2Text is a dual-mode Bilibili video transcription and optimization system:
- **Web Application**: Flask + SocketIO with real-time WebSocket updates
- **CLI Tool**: Command-line interface for batch processing and automation
- **Document Optimizer**: Gemini 2.5 Flash integration for ASR output enhancement

## Essential Commands

### Transcription Workflow
```bash
# Step 1: Download and transcribe videos (GPU)
conda activate bili2text-gpu
./scripts/transcribe/stable_transcribe.sh

# Step 2: Optimize transcripts with Gemini
export GEMINI_API_KEY="your-api-key"
python batch_optimize_txt_to_markdown.py \
  --input storage/results/gpu_transcripts \
  --output storage/results/professional_markdown
```

### CLI Operations
```bash
# Download audio with transcription
./bili2text.sh audio --url "https://www.bilibili.com/video/BV1234567890" --model medium

# Batch download UP主 videos
./bili2text.sh user-videos --uid 3546737620814672 --audio-only

# GPU batch transcription with resume
python scripts/transcribe/batch_transcribe_gpu_improved.py
python scripts/transcribe/resume_transcribe.py  # If interrupted
```

### Web Application
```bash
# Development
python run.py --debug

# Production
python run.py --production --host 0.0.0.0 --port 8000

# Docker deployment
docker-compose -f deployment/docker/docker-compose.yml up -d
```

## Architecture Patterns

### Dual-Mode Execution with Shared Core
The project maintains strict separation between Web and CLI while sharing core functionality through `src/`:

- **CLI Entry**: `cli/main.py` uses argparse subcommands pattern
- **Web Entry**: `webapp/app.py` uses Flask factory pattern with SocketIO
- **Shared Logic**: Both modes import from `src/transcriber/` and `src/downloader/`
- **Batch Processing**: Standalone scripts in `scripts/transcribe/` use direct Whisper API

### Storage Organization
```
storage/results/
├── gpu_transcripts/              # Raw ASR output (TXT)
├── professional_markdown/        # Gemini-optimized final documents
├── mark_transcripts_professional/# Batch-optimized markdown docs
└── [deprecated folders]/         # Legacy optimization attempts
```

### Environment Strategy
- **bili2text-cli**: CLI tools with CPU-based Whisper
- **bili2text-gpu**: GPU transcription with CUDA support
- **venv**: Web application dependencies
- Rationale: Conda handles GPU dependencies better, venv is lighter for web

## Critical Implementation Details

### Chinese Filename Handling
- Scripts use `safe_filename()` to handle special characters
- Temporary files pattern: `get_temp_filename()` → process → rename
- Essential for Bilibili video titles with emojis/special chars

### Whisper Model Configuration
```python
# Default settings in batch scripts
model = whisper.load_model("base")  # 74MB, good for Chinese
compute_type = "float32"  # Avoid fp16 issues on some GPUs
```

### Gemini Optimization Pipeline
```python
# Core optimizer usage
from scripts.optimize.professional_gemini_optimizer import ProfessionalGeminiOptimizer

# Key configuration
config = ProfessionalOptConfig(
    temperature=0.0,  # Deterministic output
    max_document_size=100000  # 100K chars limit
)
```

### WebSocket Real-time Updates
- Task states: pending → processing → completed/failed
- Frontend auto-reconnects with exponential backoff
- System monitoring broadcasts every 5 seconds

## Production File Locations

### Core Entry Points
- `run.py`: Web application launcher
- `cli/main.py`: CLI unified entry
- `batch_optimize_txt_to_markdown.py`: Primary optimization script
- `batch_optimize_mark_transcripts.py`: Markdown optimization

### Critical Scripts
- `scripts/transcribe/stable_transcribe.sh`: Production GPU transcription
- `scripts/transcribe/batch_transcribe_gpu_improved.py`: Batch with progress
- `scripts/optimize/professional_gemini_optimizer.py`: Core optimizer engine

### Deprecated Code
All experimental and superseded scripts are in `scripts/deprecated/` for reference.

## API Integration Notes

### Gemini 2.5 Flash
- Context window: 100M tokens (~750K Chinese characters)
- Rate limit: 15 RPM (free tier) → 5-second intervals in batch
- Retry strategy: 60s wait on quota errors, 10s on general errors

### Bilibili Download
- Uses `bilix` for video/audio extraction
- `bilibili-api-python` for user video lists
- Proxy support via `--proxy-url` parameter