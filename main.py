import argparse
import os
from datetime import datetime
from capturing.ffmpeg import Ffmpeg
from processing.diarizer import Diarizer
from processing.transcriber import FastWhisperTranscriber
from processing.aligner import Aligner

import json
from pathlib import Path

import logging

logger = logging.getLogger(__name__)

OUTPUT_DIR = os.path.expanduser('~/org/transcriptions')

class Persister:
    def __init__(self, output_dir):
        self.file_path = os.path.join(output_dir)
        os.makedirs(self.file_path, exist_ok=True)

    def persist(self, filename, data):
        file_path = os.path.join(self.file_path, filename)

        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                if isinstance(data, (list, dict)):
                    json.dump(data, file, ensure_ascii=False, indent=4)
                else:
                    file.write(str(data))
                    logger.info(f"Data saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving data: {e}")

class OrgPostProcessor:
    def __init__(self, runner):
        self.source_file = runner.config.filename
        self.timestamp = runner.config.timestamp

    def process(self):
        output_dir = os.path.expanduser('~/org/transcriptions')
        transcription_file = os.path.join(output_dir, self.source_file)
        org_output_file = os.path.join(output_dir, f"{self.timestamp}.org")

        with open(transcription_file) as f:
            data = json.load(f)

        lines = [f"* Transcription {self.timestamp}"]

        for entry in data:
            speaker, start, end, text = entry
            lines.append(f"** {speaker} ({start:.2f}s - {end:.2f}s)")
            lines.append(text.strip())
            lines.append("")

        Path(org_output_file).write_text("\n".join(lines))

class Runner:
    def __init__(self, config):
        self.config = config

        self.capturer = Ffmpeg()
        self.transcriber = FastWhisperTranscriber()
        self.diarizer = Diarizer()
        self.aligner = Aligner()
        self.persister = Persister(config.output_path)
        self.hooks = hooks

    def run(self):
        audio = self.fetch_audio()

        transcription, timestamps = self.transcriber.transcribe(audio)
        diarization = self.diarize(audio)
        final_transcription = self.align(transcription, timestamps, diarization)

        self.persister.persist(self.config.filename, final_transcription)
        self.run_hooks()

    def fetch_audio(self):
        def normalize_path(raw_path: str | Path, base_dir: str | Path | None = None) -> Path:
            p = Path(raw_path).expanduser()
            if not p.is_absolute():
                base = Path(base_dir) if base_dir else Path.cwd()
                p = base / p

            return p.resolve(strict=False)

        if self.config.skip_capture:
            return str(normalize_path(self.config.audio_file_path))
        else:
            return self.capturer.capture(self.config.timestamp)

    def diarize(self, audio_file):
        if self.config.skip_diarization:
            return None
        else:
            return self.diarizer.diarize(audio_file)

    def align(self, transcription, timestamps, diarization=None):
        if self.config.skip_diarization:
            return None
        else:
            return self.aligner.align(transcription, timestamps, diarization)

    def run_hooks(self):
        if not self.config.skip_hooks:
            for hook in self.hooks:
                hook(self).process()

class Config:
    def __init__(self, audio_file_path, skip_diarization, output_path, skip_hooks, hooks=[]):
        self.skip_diarization = skip_diarization
        self.skip_capture = bool(audio_file_path)
        self.skip_hooks = skip_hooks
        self.audio_file_path = audio_file_path
        self.output_path = output_path if bool(output_path) else "~/tmp/transcriptions" # OUTPUT_DIR
        self.hooks = hooks

        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.filename = f"{self.timestamp}.json"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Oatmeal',
        description='Transcribe and diarize audio completely locally!',
        epilog='This is still a WIP so expect updates and/or breaking changes.')

    parser.add_argument('-d', '--skip-diarization', action='store_true')
    parser.add_argument('-k', '--skip-hooks', action='store_true')
    parser.add_argument('-f', '--audio-file-path')
    parser.add_argument('-o', '--output-path')

    args = parser.parse_args()
    hooks = [OrgPostProcessor]

    config = Config(args.audio_file_path, args.skip_diarization, args.output_path, args.skip_hooks, hooks)
    runner = Runner(config)
    runner.run()
