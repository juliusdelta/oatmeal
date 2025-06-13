import os
from pyannote.audio import Pipeline
import torch
import logging

logger = logging.getLogger(__name__)

class Diarizer:
    def __init__(self):
        try:
            hf_token = os.getenv('HF_AUTH_TOKEN')
            if hf_token is None:
                raise ValueError("HF_AUTH_TOKEN environment variable not set")

            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=hf_token
            )
            # Move the pipeline to GPU (if available)
            device = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")
            self.pipeline.to(device)
            logger.info(f"Diarization pipeline loaded and set to use {device}.")
        except Exception as e:
            logger.error(f"Error loading the diarization model: {e}")
            self.pipeline = None

    def diarize(self, audio_path: str):
        if self.pipeline is None:
            logger.warning("Diarization model is not available.")
            return None

        try:
            diarization = self.pipeline(audio_path)
            logger.info(f"Diarization successful for file: {audio_path}")
            return diarization
        except Exception as e:
            logger.error(f"Error during diarization: {e}")
            return None
