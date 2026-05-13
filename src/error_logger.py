"""Error Logger — writes errors to log file for later querying."""
import os
from datetime import datetime
from typing import List


class ErrorLogger:
    """Logs errors to a file for silent tracking."""

    def __init__(self, log_path: str = "digest/logs/errors.log"):
        self.log_path = log_path

    def log(self, source: str, error_type: str, message: str) -> None:
        """Append an error entry to the log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"{timestamp} | {source} | {error_type} | {message}\n"

        os.makedirs(os.path.dirname(self.log_path) or ".", exist_ok=True)

        with open(self.log_path, "a") as f:
            f.write(entry)

    def read(self) -> List[dict]:
        """Read all error entries from the log file."""
        if not os.path.exists(self.log_path):
            return []

        errors = []
        with open(self.log_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(" | ", 3)
                if len(parts) >= 4:
                    errors.append({
                        "timestamp": parts[0],
                        "source": parts[1],
                        "error_type": parts[2],
                        "message": parts[3],
                    })
        return errors

    def clear(self) -> None:
        """Clear all error entries."""
        if os.path.exists(self.log_path):
            os.remove(self.log_path)
