# Oatmeal

> [!WARNING]
> This is still a work in progress but hopefully this will make it easy to automate transcribing/diarization all completely locally

## Requirements
- uv
- ffmpeg

## Todos
- [ ] Record user input & microphone in parallel for simple "user & other" transcription
- [ ] Skip dairization by default as it's very itensive and allow user to opt in
- [ ] Add configuration file for output file directory settings, adding personal API keys, default parameters and more...
- [ ] Add configurable hooks so a user can add in their own behavior
- [ ] Automatically provide summaries via LLM if API key is provided
  - [ ] ensure prompt is configurable
- [ ] Standardize output json schema so handling diarized vs. transcribe only situations is easier

## Usage
In this early stage you can use `uv run main.py --help` to get a full list of the parameters for basic use

## Advanced Usage

