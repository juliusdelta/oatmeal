from abc import abstractmethod
from typing import Any
from pathlib import Path

from capturing.audio_file import AudioFile
from capturing.two_channel import TwoChannel

from config import Config


class RunStrategy:
    def __init__(self, configuration: Config):
        self.config = configuration

    @abstractmethod
    def run(self) -> Any:
        """
        Primary execution method of the child classes
        """
        pass

    def fetch_audio(self) -> str | tuple[str, str]:
        return self.config.capturer.capture()
