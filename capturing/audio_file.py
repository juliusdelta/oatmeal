from pathlib import Path

class AudioFile:
    def __init__(self, file_path: str | Path, base_dir: str | Path | None = None):
        self.file_path = file_path
        self.base_dir = base_dir

    def capture(self) -> str:
        """
        Find and resolve the audio file path regardless if absolute or relative path is provided.

        Returns a string that represents the `Path` to the audio file.
        """
        normalized_file_path =  self.normalize_path(self.file_path, self.base_dir)
        return str(normalized_file_path)

    def normalize_path(self, raw_path: str | Path, base_dir: str | Path | None = None) -> Path:
        p = Path(raw_path).expanduser()
        if not p.is_absolute():
            base = Path(base_dir) if base_dir else Path.cwd()
            p = base / p

        return p.resolve(strict=False)
