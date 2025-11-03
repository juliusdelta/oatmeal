from datetime import datetime
from pathlib import Path
import json
import logging

from capturing.audio_file import AudioFile
from capturing.two_channel import TwoChannel
from processing.transcriber import FastWhisperTranscriber, TorchWhisperTranscriber

logger = logging.getLogger(__name__)

BASE_DIR = "~/oatmeal"

class Config:
    def __init__(self, audio_file_path=None, diarize=False, base_output_path=BASE_DIR):
        # Timestamp configuration
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Directory structure: ~/oatmeal/{timestamp}/
        self.base_dir = Path(base_output_path).expanduser()
        self.session_dir = self.base_dir / self.timestamp
        self.audio_dir = self.session_dir / "audio"
        self.transcriptions_dir = self.session_dir / "transcriptions"
        self.final_transcription_path = self.session_dir / "transcription.json"
        self.enhanced_transcription_path = self.session_dir / "enhanced_transcription.json"
        
        # Create directories
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.transcriptions_dir.mkdir(parents=True, exist_ok=True)

        # Runtime configuration
        self.audio_file_path = audio_file_path
        self.diarize = diarize
        self.skip_capture = bool(audio_file_path)
        
        # Track session start time for duration calculation
        self.session_start_time = datetime.now()

        # Capturer and Transcriber configuration
        self.capturer = self.set_capturer(audio_file_path)
        self.transcriber = self.set_transcriber()

    def set_capturer(self, audio_file_path: str | None = None):
        if audio_file_path:
            return AudioFile(audio_file_path)
        else:
            return TwoChannel(self.audio_dir, self.timestamp)

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

    def save_transcription(self, filename: str, data):
        """Save transcription data to the transcriptions directory"""
        file_path = self.transcriptions_dir / filename
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                if isinstance(data, (list, dict)):
                    json.dump(data, file, ensure_ascii=False, indent=4)
                else:
                    file.write(str(data))
            logger.info(f"Transcription saved to {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error saving transcription: {e}")
            raise

    def save_final_transcription(self, data):
        """Save the final aligned transcription"""
        try:
            with open(self.final_transcription_path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            logger.info(f"Final transcription saved to {self.final_transcription_path}")
            return self.final_transcription_path
        except Exception as e:
            logger.error(f"Error saving final transcription: {e}")
            raise

    def save_enhanced_transcription(self, data):
        """Save the enhanced transcription format"""
        try:
            with open(self.enhanced_transcription_path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            logger.info(f"Enhanced transcription saved to {self.enhanced_transcription_path}")
            return self.enhanced_transcription_path
        except Exception as e:
            logger.error(f"Error saving enhanced transcription: {e}")
            raise

    def generate_session_metadata(self) -> dict:
        """Generate session-level metadata for enhanced format"""
        session_end_time = datetime.now()
        duration_seconds = (session_end_time - self.session_start_time).total_seconds()
        
        return {
            "timestamp": self.timestamp,
            "duration_seconds": round(duration_seconds, 2)
        }
