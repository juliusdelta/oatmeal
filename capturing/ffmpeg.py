import subprocess
import signal
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
CAPTURE_DIR = "~/audiocaptures/"

class Ffmpeg:
    def __init__(self) -> None:
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.capture_dir = str(Path("~/audiocaptures").expanduser())
        self.mic_source = "alsa_input.usb-Blue_Microphones_Yeti_Stereo_Microphone_797_2021_05_05_40752-00.analog-stereo"
        self.monitor_source = "alsa_output.usb-Nuforce_Inc._NuForce_USB_Audio-01.analog-stereo.monitor"

    def capture(self, timestamp, separate_files=False):
        mic_wav_path = f"{self.capture_dir}/{timestamp}_mic.wav"
        monitor_wav_path = f"{self.capture_dir}/{timestamp}_monitor.wav"
        mixed_wav_path = f"{self.capture_dir}/{timestamp}.wav"

        if not separate_files:
            cmd = [
                "ffmpeg",
                "-f", "pulse", "-i", self.mic_source,
                "-f", "pulse", "-i", self.monitor_source,
                "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=longest[aout]",
                "-map", "[aout]",
                "-ac", "2", "-ar", "44100",
                str(mixed_wav_path)
            ]
            logging.info(f"Recording to {mixed_wav_path}... Press Ctrl+C to stop.")
            proc = None
            try:
                proc = subprocess.Popen(cmd)
                proc.wait()
            except KeyboardInterrupt:
                if proc is not None:
                    proc.send_signal(signal.SIGINT)
                    proc.wait()
            return mixed_wav_path
        else:
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
