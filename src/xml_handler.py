import xml.etree.ElementTree as ET
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)

class XMLHandler:
    def __init__(self, output_dir: str, config: dict):
        self.output_dir = output_dir
        self.xml_config = config['xml']
        
        # Map categories to their file names from config
        self.category_files = {
            'external': self.xml_config['external_file'],
            'internal': self.xml_config['internal_file'],
            'client': self.xml_config['client_file']
        }
        
        self.roots = {
            'external': ET.Element('Root'),
            'internal': ET.Element('Root'),
            'client': ET.Element('Root')
        }
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Output directory: {output_dir}")
        
        # Load existing XML files if they exist
        self._load_existing_files()

    def _load_existing_files(self):
        """Load existing XML files if they exist."""
        for category, filename in self.category_files.items():
            file_path = os.path.join(self.output_dir, filename)
            logger.info(f"Checking for existing file: {file_path}")
            
            if os.path.exists(file_path):
                try:
                    tree = ET.parse(file_path)
                    self.roots[category] = tree.getroot()
                    logger.info(f"Loaded existing {filename} with {len(self.roots[category])} entries")
                except ET.ParseError:
                    logger.warning(f"Could not parse existing {filename}, starting fresh")
            else:
                logger.info(f"No existing file found for {category}, will create new {filename}")

    def _entry_exists(self, category: str, filename: str) -> bool:
        """Check if an entry with the given filename already exists."""
        root = self.roots[category]
        existing_entries = root.findall(".//entry[@filename]")
        return any(entry.get('filename') == filename for entry in existing_entries)

    def add_entry(self, category: str, filename: str, text: str, metadata: Optional[dict] = None):
        """Add a new entry to the specified XML category."""
        if category not in self.roots:
            logger.error(f"Invalid category: {category}")
            raise ValueError(f"Invalid category: {category}")

        # Check if entry already exists
        if self._entry_exists(category, filename):
            logger.debug(f"Entry for {filename} already exists in {category}")
            return

        # Create new entry
        entry = ET.Element('entry')
        entry.set('filename', filename)
        
        # Add metadata if provided
        if metadata:
            for key, value in metadata.items():
                entry.set(key, str(value))
        
        entry.text = text
        self.roots[category].append(entry)
        logger.info(f"Added new entry for {filename} to {category}")

    def save_all(self):
        """Save all XML files."""
        logger.info("Saving all XML files...")
        for category, root in self.roots.items():
            filename = self.category_files[category]
            self._save_xml(category, root, filename)

    def _save_xml(self, category: str, root: ET.Element, filename: str):
        """Save individual XML file."""
        output_path = os.path.join(self.output_dir, filename)
        
        # Add indentation for better readability
        self._indent(root)
        
        # Create ElementTree and save
        tree = ET.ElementTree(root)
        try:
            tree.write(output_path, encoding='utf-8', xml_declaration=True)
            entry_count = len(root.findall('.//entry'))
            logger.info(f"Successfully saved {filename} with {entry_count} entries to {output_path}")
        except Exception as e:
            logger.error(f"Error saving {filename}: {str(e)}")

    def _indent(self, elem, level=0):
        """Add proper indentation to the XML file."""
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for subelem in elem:
                self._indent(subelem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i 