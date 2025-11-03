# AGENTS.md

## Build/Run Commands
- **Run application**: `uv run main.py --help` (shows all CLI options)
- **Install dependencies**: `uv sync` or `uv install` 
- **Test**: No test framework configured - this project has no unit tests
- **Lint**: No linting configuration found

## Code Style Guidelines
- **Imports**: Standard library first, then third-party, then local imports with blank lines between groups
- **Classes**: PascalCase (e.g., `FastWhisperTranscriber`, `TwoChannel`)
- **Functions/variables**: snake_case (e.g., `fetch_audio`, `audio_file_path`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `OUTPUT_DIR`, `DEFAULT_AUDIO_CAPTURE_DIR`)
- **Type hints**: Use modern union syntax `str | None` instead of `Optional[str]`
- **Error handling**: Use try-except blocks with logging, propagate exceptions when appropriate
- **Logging**: Use module-level logger: `logger = logging.getLogger(__name__)`
- **Docstrings**: Triple quotes for class/method documentation, focus on purpose and behavior
- **File organization**: Group related functionality in modules (capturing/, processing/, run_strategies/)

## Architecture Notes
- **Core Architecture**: Uses modern strategy pattern in `run_strategies/` - legacy `Runner` class removed from `main.py`
- **Session Management**: Timestamp-based directory structure `~/oatmeal/{timestamp}/` for each recording session
- **Configuration**: Centralized in `config.py` with dependency injection and session directory management
- **Two-Channel Audio**: `TwoChannel.capture()` creates separate `audio/mic.wav` and `audio/monitor.wav` files
- **File Handling**: Use Path objects, expand user home with `Path.expanduser()`
- **ML Models**: Initialize lazily with proper device detection (CPU/CUDA/MPS)

## Directory Structure
Each recording session creates:
```
~/oatmeal/{timestamp}/
├── audio/
│   ├── mic.wav          # Microphone input
│   └── monitor.wav      # System audio
├── transcriptions/
│   ├── mic.json         # Individual mic transcription
│   ├── monitor.json     # Individual monitor transcription
│   └── transcription.json  # Current aligned output
└── enhanced_transcription.json  # Future: LLM-optimized format
```

## Current Implementation Status
- ✅ **Core Two-Channel Workflow**: Functional with timestamp-based sessions
- ✅ **Strategy Pattern**: TranscribeOnlyStrategy and DiarizeStrategy operational
- 🚧 **Enhanced LLM Format**: Implementation planned (see `llm-docs/enhanced-transcription-format.md`)
- 🚧 **MultiTranscriptionAligner**: Needs enhanced alignment method for speaker attribution

## Key Classes & Methods
- **Config**: Session directory creation, file path management
- **TwoChannel**: Two-channel audio capture with proper file separation  
- **TranscribeOnlyStrategy**: Individual + aligned transcription generation
- **MultiTranscriptionAligner**: Aligns mic/monitor transcriptions (needs enhancement)