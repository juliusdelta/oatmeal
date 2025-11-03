from .strategy import RunStrategy

class Diarize(RunStrategy):
    def run(self):
        """
        Executes run with user & monitor audio as 2 channels and diarizes the monitor channel. This process is slow and takes a lot of time
        but is useful when accuracy is required.

        - Records user audio from selected input.
        - Records monitor from selected monitor.

        Both channel captures are transcribed, however, only the monitor is diarized. Once the diarization is complete, it is then merged with the transcription of the user channel.
        This helps to optimize performance as much as possible, so if for instance the user speaks the most during the meeting, since their transcript is already attributable to
        them, we don't rediarize their channel.
        """
        print("Diarized run!")
