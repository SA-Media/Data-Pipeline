import os
import yaml
from typing import Set
from datetime import datetime
from document_processor import DocumentProcessor
from xml_handler import XMLHandler
from file_tracker import FileTracker
import logging
from pathlib import Path

class DocumentProcessingPipeline:
    def __init__(self, config_path: str = "config.yaml"):
        # Set up logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Load config
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Error loading config file: {str(e)}")
            raise

        # Initialize components
        self.doc_processor = DocumentProcessor()
        self.xml_handler = XMLHandler(self.config['paths']['output_folder'], self.config)
        self.file_tracker = FileTracker()
        
        self.document_extensions = set(self.config['file_types']['documents'])
        self.ignore_extensions = set(self.config['file_types']['ignore'])
        
        self.logger.info("Pipeline initialized successfully")

    def process_directory(self):
        """Process all documents in the configured directory."""
        root_path = self.config['paths']['root_folder']
        self.logger.info(f"Starting to process directory: {root_path}")
        
        files_processed = 0
        files_skipped = 0
        files_errored = 0
        
        for subdir, _, files in os.walk(root_path):
            for filename in files:
                file_path = os.path.join(subdir, filename)
                try:
                    result = self._process_file(file_path, subdir)
                    if result == "processed":
                        files_processed += 1
                    elif result == "skipped":
                        files_skipped += 1
                    else:
                        files_errored += 1
                except Exception as e:
                    self.logger.error(f"Error processing {file_path}: {str(e)}")
                    files_errored += 1
        
        # Save all XML files
        self.xml_handler.save_all()
        
        self.logger.info(f"Processing complete. "
                        f"Processed: {files_processed}, "
                        f"Skipped: {files_skipped}, "
                        f"Errors: {files_errored}")

    def _process_file(self, file_path: str, subdir: str) -> str:
        """Process individual file. Returns 'processed', 'skipped', or 'error'"""
        extension = os.path.splitext(file_path)[1].lower()
        
        # Skip if file should be ignored
        if extension in self.ignore_extensions:
            self.logger.debug(f"Skipped {file_path}: ignored extension {extension}")
            return "skipped"
        
        # Skip if file type is not supported
        if extension not in self.document_extensions:
            self.logger.debug(f"Skipped {file_path}: unsupported extension {extension}")
            return "skipped"
        
        # Skip if file hasn't been modified
        if not self.file_tracker.needs_update(file_path):
            self.logger.debug(f"Skipped {file_path}: already processed")
            return "skipped"

        # Determine category based on folder
        category = self._determine_category(subdir)
        if not category:
            self.logger.debug(f"Skipped {file_path}: no matching category for {subdir}")
            return "skipped"

        try:
            # Extract text from document
            self.logger.info(f"Processing file: {file_path}")
            text = self.doc_processor.extract_text(file_path)
            
            if not text.strip():
                self.logger.warning(f"No text extracted from {file_path}")
                return "error"
            
            # Add entry to appropriate XML
            self.xml_handler.add_entry(
                category=category,
                filename=os.path.basename(file_path),
                text=text,
                metadata={'processed_date': str(datetime.now())}
            )
            
            # Update file tracker
            self.file_tracker.update_file_timestamp(file_path)
            return "processed"
                
        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {str(e)}")
            return "error"

    def _determine_category(self, subdir: str) -> str:
        """Determine the category based on the subdirectory."""
        subdir = subdir.replace('\\', '/').lower()  # Normalize path separators and case
        
        # Get folder names from config and convert to lower case
        external = self.config['folders']['external'].lower()
        internal = self.config['folders']['internal'].lower()
        client = self.config['folders']['client'].lower()
        
        # Log the path and what we're looking for
        self.logger.debug(f"Checking category for path: {subdir}")
        self.logger.debug(f"Looking for folders: {external}, {internal}, {client}")
        
        # Check each category
        if external in subdir:
            self.logger.info(f"Categorized as external: {subdir}")
            return 'external'
        elif internal in subdir:
            self.logger.info(f"Categorized as internal: {subdir}")
            return 'internal'
        elif client in subdir:
            self.logger.info(f"Categorized as client: {subdir}")
            return 'client'
            
        self.logger.debug(f"No category match found for: {subdir}")
        return None

def main():
    pipeline = DocumentProcessingPipeline()
    pipeline.process_directory()

if __name__ == "__main__":
    main() 