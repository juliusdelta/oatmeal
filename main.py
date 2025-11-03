import argparse
import logging

from config import Config
from run_strategies.transcribe_only_strategy import TranscribeOnlyStrategy

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        prog="Oatmeal",
        description="Transcribe two-channel audio completely locally!",
        epilog="Records mic and monitor audio, transcribes each separately, then aligns them by timestamp.",
    )

    parser.add_argument(
        "-f", "--audio-file-path", help="Path to existing audio file (skips capture)"
    )
    parser.add_argument(
        "-o", "--output-path", help="Base output directory (default: ~/oatmeal)"
    )

    args = parser.parse_args()

    try:
        # Create configuration
        config = Config(
            audio_file_path=args.audio_file_path,
            base_output_path=args.output_path or "~/oatmeal",
        )

        logger.info(f"Starting transcription session: {config.timestamp}")
        logger.info(f"Session directory: {config.session_dir}")

        # Run the transcription strategy
        strategy = TranscribeOnlyStrategy(config)
        aligned_transcription = strategy.run()

        logger.info("Transcription complete!")
        logger.info(f"Audio files: {config.audio_dir}")
        logger.info(f"Individual transcriptions: {config.transcriptions_dir}")
        logger.info(f"Final aligned transcription: {config.final_transcription_path}")

        return aligned_transcription

    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise


if __name__ == "__main__":
    main()
