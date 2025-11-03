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
- Modern strategy pattern in `run_strategies/` (preferred) vs legacy `Runner` class in `main.py`
- Configuration centralized in `config.py` with dependency injection
- Use Path objects for file paths, expand user home with `Path.expanduser()`
- ML models initialized lazily with proper device detection (CPU/CUDA/MPS)