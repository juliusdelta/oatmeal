import subprocess
import signal
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class TwoChannel:
    def __init__(self, audio_dir, timestamp) -> None:
        self.timestamp = timestamp
        self.audio_dir = Path(audio_dir)
        self.mic_source = "alsa_input.usb-Blue_Microphones_Yeti_Stereo_Microphone_797_2021_05_05_40752-00.analog-stereo"
        self.monitor_source = "alsa_output.usb-Nuforce_Inc._NuForce_USB_Audio-01.analog-stereo.monitor"

    def capture(self) -> tuple[str, str]:
        """
        Records user and monitor as 2 separate channels with FFMpeg regardless of other configuration
        variables.

        Returns 2 file paths, one for each channel.
        """
        # Ensure audio directory exists
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        
        mic_wav_path = str(self.audio_dir / "mic.wav")
        monitor_wav_path = str(self.audio_dir / "monitor.wav")

        cmd = [
            "ffmpeg",
            "-f", "pulse", "-i", self.mic_source,
            "-f", "pulse", "-i", self.monitor_source,
            "-map", "0:a",
            "-ac", "2", "-ar", "44100", mic_wav_path,
            "-map", "1:a",
            "-ac", "2", "-ar", "44100", monitor_wav_path
        ]
        logging.info(f"Recording to {mic_wav_path} and {monitor_wav_path}... Press Ctrl+C to stop.")
        proc = None
        try:
            proc = subprocess.Popen(cmd)
            proc.wait()
        except KeyboardInterrupt:
            if proc is not None:
                proc.send_signal(signal.SIGINT)
                proc.wait()
        return mic_wav_path, monitor_wav_path
