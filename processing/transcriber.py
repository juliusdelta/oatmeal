import torch
import logging
from typing import Dict, List
from faster_whisper import WhisperModel
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

logger = logging.getLogger(__name__)

class FastWhisperTranscriber:
    def __init__(self, model_name="tiny"):
        self.whisper_model = WhisperModel(model_name, device="cpu", compute_type="int8")

    def transcribe(self, audio_path: str) -> tuple[str, List[Dict]]:
        segments, _ = self.whisper_model.transcribe(audio_path)
        transcription = []
        transcription_with_timestamps = []

        for segment in segments:
            transcription.append(segment.text)
            transcription_with_timestamps.append({ "timestamp": [segment.start, segment.end], "text": segment.text })


        return " ".join(transcription), transcription_with_timestamps

class TorchWhisperTranscriber:
    def __init__(self, model_name="openai/whisper-tiny"):
        if torch.cuda.is_available():
            self.device = "cuda:0"
            self.torch_dtype = torch.float16
        elif torch.backends.mps.is_available():
            self.device = "mps"
            self.torch_dtype = torch.float16
        else:
            self.device = "cpu"
            self.torch_dtype = torch.float32

        logger.info(f"Using device: {self.device} with dtype: {self.torch_dtype}")

        try:
            self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                model_name,
                torch_dtype=self.torch_dtype,
                low_cpu_mem_usage=True,
                use_safetensors=True,
            )
            self.model.to(self.device)

            self.processor = AutoProcessor.from_pretrained(model_name)

            self.pipe = pipeline(
                "automatic-speech-recognition",
                model=self.model,
                tokenizer=self.processor.tokenizer,
                feature_extractor=self.processor.feature_extractor,
                torch_dtype=self.torch_dtype,
                device=self.device,
                model_kwargs={"language": "end", "attn_implementation": "sdpa"},
                return_timestamps=True,
                batch_size=1, # 24 for GPUs maybe?
                generate_kwargs={"max_new_tokens": 400},
                chunk_length_s=5,
                stride_length_s=(1, 1),
            )
            logger.info("Transcription model and pipeline loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading the transcription model: {e}")
            raise

    def transcribe(self, audio_path: str) -> tuple:
        try:
            # Perform transcription with timestamps
            result = self.pipe(audio_path)
            transcription = result['text']
            timestamps = result['chunks']
            logger.info(f"Successfully transcribed: {audio_path}")
            return transcription, timestamps
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            return None, None
