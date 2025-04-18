"""
Base parser class for metadata extraction.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseParser(ABC):
    """Base class for metadata parsers."""
    
    @abstractmethod
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a file and extract metadata.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            Dictionary of extracted metadata
        """
        pass
    
    @abstractmethod
    def validate(self, metadata: Dict[str, Any]) -> bool:
        """
        Validate the extracted metadata.
        
        Args:
            metadata: Dictionary of metadata to validate
            
        Returns:
            True if the metadata is valid, False otherwise
        """
        pass
    
    def get_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Parse a file and validate the extracted metadata.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            Dictionary of validated metadata, or None if validation fails
        """
        metadata = self.parse(file_path)
        if self.validate(metadata):
            return metadata
        return None
