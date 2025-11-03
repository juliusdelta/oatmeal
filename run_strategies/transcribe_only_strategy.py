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

        # Align transcriptions by timestamp (legacy format)
        aligned_transcription = MultiTranscriptionAligner.align(
            user_transcription_timestamps, monitor_transcription_timestamps
        )

        # Save final aligned transcription (legacy format)
        self.config.save_final_transcription(aligned_transcription)

        # Generate enhanced format
        session_metadata = self.config.generate_session_metadata()
        enhanced_transcription = MultiTranscriptionAligner.align_enhanced(
            user_transcription_timestamps,
            monitor_transcription_timestamps,
            session_metadata,
        )

        # Save enhanced transcription
        self.config.save_enhanced_transcription(enhanced_transcription)

        # Log summary statistics
        hints = enhanced_transcription["summary_hints"]
        print("Session Summary:")
        print(f"  Total segments: {hints['total_segments']}")
        print(f"  User talk time: {hints['user_talk_time_seconds']}s")
        print(f"  Others talk time: {hints['others_talk_time_seconds']}s")
        print(f"  Average segment length: {hints['avg_segment_length']}s")
        print(f"  Silence gaps detected: {hints['silence_gaps']}")

        return aligned_transcription
