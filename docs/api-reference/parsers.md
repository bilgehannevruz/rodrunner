# Parsers API Reference

This page contains the API reference for the parsers module.

## `BaseParser`

```python
class BaseParser(ABC):
    """
    Base class for parsers.
    
    This class defines the interface for parsers that extract metadata from files.
    """
    
    @abstractmethod
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a file and extract metadata.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            Dictionary of metadata extracted from the file
        """
        pass
    
    @abstractmethod
    def validate(self, metadata: Dict[str, Any]) -> bool:
        """
        Validate metadata.
        
        Args:
            metadata: Metadata to validate
            
        Returns:
            True if the metadata is valid, False otherwise
        """
        pass
```

The `BaseParser` class is an abstract base class for parsers that extract metadata from files.

### Methods

#### `parse`

```python
@abstractmethod
def parse(self, file_path: str) -> Dict[str, Any]:
    """
    Parse a file and extract metadata.
    
    Args:
        file_path: Path to the file to parse
        
    Returns:
        Dictionary of metadata extracted from the file
    """
```

This method parses a file and extracts metadata.

##### Parameters

- `file_path`: Path to the file to parse

##### Returns

Dictionary of metadata extracted from the file.

#### `validate`

```python
@abstractmethod
def validate(self, metadata: Dict[str, Any]) -> bool:
    """
    Validate metadata.
    
    Args:
        metadata: Metadata to validate
        
    Returns:
        True if the metadata is valid, False otherwise
    """
```

This method validates metadata.

##### Parameters

- `metadata`: Metadata to validate

##### Returns

True if the metadata is valid, False otherwise.

## `RunInfoParser`

```python
class RunInfoParser(BaseParser):
    """
    Parser for RunInfo.xml files.
    
    This class extracts metadata from RunInfo.xml files.
    """
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a RunInfo.xml file and extract metadata.
        
        Args:
            file_path: Path to the RunInfo.xml file
            
        Returns:
            Dictionary of metadata extracted from the file
        """
```

The `RunInfoParser` class extracts metadata from RunInfo.xml files.

### Methods

#### `parse`

```python
def parse(self, file_path: str) -> Dict[str, Any]:
    """
    Parse a RunInfo.xml file and extract metadata.
    
    Args:
        file_path: Path to the RunInfo.xml file
        
    Returns:
        Dictionary of metadata extracted from the file
    """
```

This method parses a RunInfo.xml file and extracts metadata.

##### Parameters

- `file_path`: Path to the RunInfo.xml file

##### Returns

Dictionary of metadata extracted from the file.

##### Example

```python
parser = RunInfoParser()
metadata = parser.parse("/path/to/RunInfo.xml")
print(metadata)
```

#### `validate`

```python
def validate(self, metadata: Dict[str, Any]) -> bool:
    """
    Validate RunInfo.xml metadata.
    
    Args:
        metadata: Metadata to validate
        
    Returns:
        True if the metadata is valid, False otherwise
    """
```

This method validates RunInfo.xml metadata.

##### Parameters

- `metadata`: Metadata to validate

##### Returns

True if the metadata is valid, False otherwise.

##### Example

```python
parser = RunInfoParser()
metadata = parser.parse("/path/to/RunInfo.xml")
is_valid = parser.validate(metadata)
```

## `RunParametersParser`

```python
class RunParametersParser(BaseParser):
    """
    Parser for RunParameters.xml files.
    
    This class extracts metadata from RunParameters.xml files.
    """
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a RunParameters.xml file and extract metadata.
        
        Args:
            file_path: Path to the RunParameters.xml file
            
        Returns:
            Dictionary of metadata extracted from the file
        """
```

The `RunParametersParser` class extracts metadata from RunParameters.xml files.

### Methods

#### `parse`

```python
def parse(self, file_path: str) -> Dict[str, Any]:
    """
    Parse a RunParameters.xml file and extract metadata.
    
    Args:
        file_path: Path to the RunParameters.xml file
        
    Returns:
        Dictionary of metadata extracted from the file
    """
```

This method parses a RunParameters.xml file and extracts metadata.

##### Parameters

- `file_path`: Path to the RunParameters.xml file

##### Returns

Dictionary of metadata extracted from the file.

##### Example

```python
parser = RunParametersParser()
metadata = parser.parse("/path/to/RunParameters.xml")
print(metadata)
```

#### `validate`

```python
def validate(self, metadata: Dict[str, Any]) -> bool:
    """
    Validate RunParameters.xml metadata.
    
    Args:
        metadata: Metadata to validate
        
    Returns:
        True if the metadata is valid, False otherwise
    """
```

This method validates RunParameters.xml metadata.

##### Parameters

- `metadata`: Metadata to validate

##### Returns

True if the metadata is valid, False otherwise.

##### Example

```python
parser = RunParametersParser()
metadata = parser.parse("/path/to/RunParameters.xml")
is_valid = parser.validate(metadata)
```

## `SampleSheetParser`

```python
class SampleSheetParser(BaseParser):
    """
    Parser for SampleSheet.csv files.
    
    This class extracts metadata from SampleSheet.csv files.
    """
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a SampleSheet.csv file and extract metadata.
        
        Args:
            file_path: Path to the SampleSheet.csv file
            
        Returns:
            Dictionary of metadata extracted from the file
        """
```

The `SampleSheetParser` class extracts metadata from SampleSheet.csv files.

### Methods

#### `parse`

```python
def parse(self, file_path: str) -> Dict[str, Any]:
    """
    Parse a SampleSheet.csv file and extract metadata.
    
    Args:
        file_path: Path to the SampleSheet.csv file
        
    Returns:
        Dictionary of metadata extracted from the file
    """
```

This method parses a SampleSheet.csv file and extracts metadata.

##### Parameters

- `file_path`: Path to the SampleSheet.csv file

##### Returns

Dictionary of metadata extracted from the file.

##### Example

```python
parser = SampleSheetParser()
metadata = parser.parse("/path/to/SampleSheet.csv")
print(metadata)
```

#### `validate`

```python
def validate(self, metadata: Dict[str, Any]) -> bool:
    """
    Validate SampleSheet.csv metadata.
    
    Args:
        metadata: Metadata to validate
        
    Returns:
        True if the metadata is valid, False otherwise
    """
```

This method validates SampleSheet.csv metadata.

##### Parameters

- `metadata`: Metadata to validate

##### Returns

True if the metadata is valid, False otherwise.

##### Example

```python
parser = SampleSheetParser()
metadata = parser.parse("/path/to/SampleSheet.csv")
is_valid = parser.validate(metadata)
```

## `ParserFactory`

```python
class ParserFactory:
    """
    Factory for creating parsers.
    
    This class creates parsers based on file names.
    """
    
    def get_parser(self, file_path: str) -> BaseParser:
        """
        Get a parser for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Parser for the file
            
        Raises:
            ValueError: If no parser is available for the file
        """
```

The `ParserFactory` class creates parsers based on file names.

### Methods

#### `get_parser`

```python
def get_parser(self, file_path: str) -> BaseParser:
    """
    Get a parser for a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Parser for the file
        
    Raises:
        ValueError: If no parser is available for the file
    """
```

This method gets a parser for a file.

##### Parameters

- `file_path`: Path to the file

##### Returns

Parser for the file.

##### Raises

- `ValueError`: If no parser is available for the file.

##### Example

```python
factory = ParserFactory()
parser = factory.get_parser("/path/to/RunInfo.xml")
```

#### `parse_file`

```python
def parse_file(self, file_path: str) -> Dict[str, Any]:
    """
    Parse a file and extract metadata.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary of metadata extracted from the file
        
    Raises:
        ValueError: If no parser is available for the file
    """
```

This method parses a file and extracts metadata.

##### Parameters

- `file_path`: Path to the file

##### Returns

Dictionary of metadata extracted from the file.

##### Raises

- `ValueError`: If no parser is available for the file.

##### Example

```python
factory = ParserFactory()
metadata = factory.parse_file("/path/to/RunInfo.xml")
print(metadata)
```

#### `parse_directory`

```python
def parse_directory(self, directory_path: str) -> Dict[str, Dict[str, Any]]:
    """
    Parse all supported files in a directory and extract metadata.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        Dictionary mapping file names to metadata
    """
```

This method parses all supported files in a directory and extracts metadata.

##### Parameters

- `directory_path`: Path to the directory

##### Returns

Dictionary mapping file names to metadata.

##### Example

```python
factory = ParserFactory()
metadata = factory.parse_directory("/path/to/sequencer/run")
print(metadata["RunInfo.xml"])
print(metadata["RunParameters.xml"])
print(metadata["SampleSheet.csv"])
```

## Notes

- The `BaseParser` class defines the interface for parsers that extract metadata from files.
- The `RunInfoParser`, `RunParametersParser`, and `SampleSheetParser` classes implement the `BaseParser` interface for specific file types.
- The `ParserFactory` class creates parsers based on file names and provides methods for parsing files and directories.
- The `parse_directory` method parses all supported files in a directory and returns a dictionary mapping file names to metadata.
