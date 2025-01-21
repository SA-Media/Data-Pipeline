import json
import os
from typing import Dict
from datetime import datetime
import logging

class FileTracker:
    def __init__(self, tracker_file: str = "file_tracker.json"):
        self.tracker_file = tracker_file
        self.tracked_files: Dict[str, float] = self._load_tracker()

    def _load_tracker(self) -> Dict[str, float]:
        """Load the tracker file if it exists."""
        if os.path.exists(self.tracker_file):
            with open(self.tracker_file, 'r') as f:
                data = json.load(f)
                logging.info(f"Loaded {len(data)} entries from tracker file")
                return data
        logging.info("No existing tracker file found, starting fresh")
        return {}

    def _save_tracker(self):
        """Save the current state of tracked files."""
        with open(self.tracker_file, 'w') as f:
            json.dump(self.tracked_files, f, indent=2)

    def needs_update(self, file_path: str) -> bool:
        """Check if a file needs to be processed."""
        if not os.path.exists(file_path):
            return False

        current_mtime = os.path.getmtime(file_path)
        last_processed = self.tracked_files.get(file_path, 0)
        
        # Add debug logging
        logging.debug(f"File: {file_path}")
        logging.debug(f"Current mtime: {current_mtime}")
        logging.debug(f"Last processed: {last_processed}")
        
        return current_mtime > last_processed

    def update_file_timestamp(self, file_path: str):
        """Update the last processed timestamp for a file."""
        self.tracked_files[file_path] = os.path.getmtime(file_path)
        self._save_tracker()

    def remove_file(self, file_path: str):
        """Remove a file from tracking."""
        if file_path in self.tracked_files:
            del self.tracked_files[file_path]
            self._save_tracker() 