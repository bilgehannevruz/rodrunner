# Rodrunner

A comprehensive solution for managing sequencer data using iRODS and Prefect v3.

## Overview

The Rodrunner project is designed to automate the ingestion, metadata extraction, and management of sequencing data from various sequencer types (MiSeq, NextSeq, NovaSeq, PacBio, Nanopore, NovaSeqXPlus) into an iRODS data management system. It uses Prefect v3 for workflow orchestration and provides a FastAPI-based REST API for interacting with the workflows and querying metadata.

## Features

- **Filesystem Operations**: Generator-based file finding utilities similar to the Unix find command
- **iRODS Client**: A comprehensive wrapper for the python-irodsclient library
- **Metadata Parsers**: Parsers for extracting metadata from sequencer-specific files (RunInfo.xml, RunParameters.xml, SampleSheet.csv)
- **Prefect Workflows**: Workflows for data ingestion and metadata management
- **FastAPI REST API**: API for querying metadata and triggering workflows
- **Docker Integration**: Docker-based deployment for easy setup and testing

## Installation

### Using uv (recommended)

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -e .
```

### Using pip

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Quick Start

### Using the API

The API is available at http://localhost:8000. You can use the API to:

- List available workflows
- Run workflows
- Check workflow status
- Query metadata

```bash
# Start the API server
uvicorn rodrunner.api.main:app --reload

# List available workflows
curl http://localhost:8000/workflows/list

# Run a workflow
curl -X POST http://localhost:8000/workflows/run \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_name": "Ingest Sequencer Runs",
    "parameters": {
      "sequencer_type": "miseq",
      "root_dir": "/path/to/sequencer/miseq"
    }
  }'

# Check workflow status
curl http://localhost:8000/workflows/status/{flow_run_id}

# Search for metadata
curl "http://localhost:8000/metadata/search?key=run_id&value=220101_M00001_0001_000000000-A1B2C"
```

### Using Python

You can also use the Python API directly:

```python
from rodrunner.config import get_config
from rodrunner.workflows.ingest import ingest_sequencer_runs

# Load the configuration
config = get_config()

# Run the ingest workflow
results = ingest_sequencer_runs(
    config=config,
    sequencer_type="miseq",
    root_dir="/path/to/sequencer/miseq"
)

# Print the results
for result in results:
    print(f"Run: {result['run_dir']}, Success: {result['success']}")
```

### Running with Docker

```bash
# Start the Docker containers
docker-compose up -d

# Access the API at http://localhost:8000
```

### Testing with iRODS

We provide several scripts for testing the application with iRODS:

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/test_filesystem
pytest tests/test_irods
pytest tests/test_parsers
pytest tests/test_workflows
pytest tests/test_api
```

## Documentation

Comprehensive documentation is available in the `docs` directory and is also hosted on Read the Docs.

### Online Documentation

The documentation is hosted on Read the Docs at [https://rodrunner.readthedocs.io/](https://rodrunner.readthedocs.io/).

### Local Documentation

You can also build and view the documentation locally using MkDocs:

```bash
# Install MkDocs and dependencies
pip install mkdocs mkdocs-material mkdocstrings

# Build the documentation
mkdocs build

# Serve the documentation
mkdocs serve
```

The documentation includes:

- Getting Started guides
- User guides for each module
- API reference
- Development guides

## Development

### Installing development dependencies

```bash
uv pip install -e ".[dev]"
```

### Running tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=rodrunner

# Run specific tests
pytest tests/test_filesystem
```

### Code formatting and linting

```bash
# Format code
black .

# Sort imports
isort .

# Type checking
mypy rodrunner

# Linting
flake8 .

# Run all checks
pre-commit run --all-files
```

## Contributing

Contributions are welcome! Please see the [Contributing Guide](docs/development/contributing.md) for more information.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
