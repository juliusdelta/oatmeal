from datetime import datetime
from pathlib import Path

from capturing.audio_file import AudioFile
from capturing.two_channel import TwoChannel
from processing.transcriber import FastWhisperTranscriber, TorchWhisperTranscriber

DEFAULT_AUDIO_CAPTURE_DIR = "~/tmp/oatmeal-audio-captures/"
DEFAULT_TRANSCRIPTION_OUTPUT_DIR = "~/tmp/oatmeal-transcriptions/"

class Config:
    def __init__(self, audio_file_path=None, diarize=False, captured_audio_output_path=DEFAULT_AUDIO_CAPTURE_DIR, transcription_output_dir=DEFAULT_TRANSCRIPTION_OUTPUT_DIR):
        # Output configuration
        self.audio_file_path = audio_file_path
        self.captured_audio_output_path = Path(captured_audio_output_path).expanduser()
        self.transcription_output_path = Path(transcription_output_dir).expanduser()

        # Runtime configuration
        self.diarize = diarize
        self.skip_capture = bool(audio_file_path)

        # Timestamp and filename configuration
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.filename = f"{self.timestamp}.json"

        # Capturer and Transcriber configuration
        self.capturer = self.set_capturer(audio_file_path)
        self.transcriber = self.set_transcriber()

    def set_capturer(self, audio_file_path: str | None = None):
        if audio_file_path:
            return AudioFile(audio_file_path)
        else:
            capture_dir = str(Path("~/audiocaptures").expanduser())
            return TwoChannel(capture_dir, self.timestamp)

    def set_transcriber(self):
        """
        Sets transcriber based on configuration.

        - FasterWhisperTranscriber: Fastest but slightly inaccurate default
        - TorchWhisperTranscriber: Slowest but highest accuracy
        """
        if self.diarize:
            return TorchWhisperTranscriber()
        else:
            return FastWhisperTranscriber()
