from .strategy import RunStrategy
from processing.multi_transcription_aligner import MultiTranscriptionAligner


class TranscribeOnlyStrategy(RunStrategy):
    def run(self):
        """
        Executes run with user & monitor audio as 2 channels non-diarized. Useful for when granularity is not required and
        things need to happen quick.

        - Records user audio from selected input.
        - Records monitor from selected monitor.

        Each has it's own transcribed timeline, these are then merged intelligently based on start time of each transcript hash.
        """
        # Capture audio files
        user_audio, monitor_audio = self.fetch_audio()
        
        # Transcribe each channel
        user_transcription = self.config.transcriber.transcribe(user_audio)
        monitor_transcription = self.config.transcriber.transcribe(monitor_audio)

        user_transcription_timestamps = user_transcription[1]
        monitor_transcription_timestamps = monitor_transcription[1]

        # Save individual transcriptions
        self.config.save_transcription("mic.json", user_transcription_timestamps)
        self.config.save_transcription("monitor.json", monitor_transcription_timestamps)

        # Align transcriptions by timestamp
        aligned_transcription = MultiTranscriptionAligner.align(
            user_transcription_timestamps, monitor_transcription_timestamps
        )

        # Save final aligned transcription
        self.config.save_final_transcription(aligned_transcription)

        return aligned_transcription
