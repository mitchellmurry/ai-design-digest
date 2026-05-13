"""Queue Manager — reads and writes personal article queue."""
import os
from datetime import datetime
from typing import List


class QueueManager:
    """Manages a queue of URLs to include in the next digest."""

    def __init__(self, queue_path: str = "queue.md"):
        self.queue_path = queue_path

    def add(self, url: str) -> None:
        """Append a URL with timestamp to queue.md."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"- {url} (added {timestamp})\n"

        # Create file with header if missing
        if not os.path.exists(self.queue_path):
            os.makedirs(os.path.dirname(self.queue_path) or ".", exist_ok=True)
            with open(self.queue_path, "w") as f:
                f.write("# Personal Queue\n\n")

        with open(self.queue_path, "a") as f:
            f.write(line)

    def read(self) -> List[str]:
        """Read all URLs from queue.md."""
        if not os.path.exists(self.queue_path):
            return []

        urls = []
        with open(self.queue_path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("- "):
                    # Extract URL (everything before " (added" if present)
                    url = line[2:]
                    if " (added " in url:
                        url = url.split(" (added ")[0]
                    if url.startswith("http"):
                        urls.append(url)
        return urls

    def clear(self) -> None:
        """Clear all URLs from queue."""
        if os.path.exists(self.queue_path):
            with open(self.queue_path, "w") as f:
                f.write("# Personal Queue\n\n")
