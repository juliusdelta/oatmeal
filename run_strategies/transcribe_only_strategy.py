from strategy import RunStrategy
from processing import MultiTranscriptionAligner

class TranscribeOnlyStrategy(RunStrategy):
    def run(self):
        """
        Executes run with user & monitor audio as 2 channels non-diarized. Useful for when granularity is not required and
        things neeed to happen quick.

        - Records user audio from selected input.
        - Records monitor from selected monitor.

        Each has it's own transcribed timeline, these are then merged intelligently based on start time of each transcript hash.
        """
        user_audio, monitor_audio = self.fetch_audio()
        user_transcription = self.config.transcriber.transcribe(user_audio)
        monitor_transcription = self.config.transcriber.transcribe(monitor_audio)

        user_transcription_timestamps = user_transcription[1]
        monitor_transcription_timestamps = monitor_transcription[1]

        return MultiTranscriptionAligner.align(user_transcription_timestamps, monitor_transcription_timestamps)
