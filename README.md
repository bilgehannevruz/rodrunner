# iRODS Prefect Workflows

Prefect v3 workflows for iRODS interactions with python-irodsclient.

## Features

- Filesystem interaction functions similar to the Unix find command
- Comprehensive iRODS client wrapper for data operations
- Parsers for sequencer metadata files (RunInfo.xml, RunParameters.xml, SampleSheet.csv)
- Prefect v3 workflows for multiple sequencer types
- FastAPI integration for querying iRODS based on metadata
- Docker deployment with iRODS server for testing

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

## Usage

### Running the API

```bash
uvicorn rodrunner.api.main:app --reload
```

### Running with Docker

```bash
cd docker
docker-compose up -d
```

### Testing with iRODS

We provide several scripts for testing the application with iRODS:

```bash
# Start the iRODS server
cd docker
./start-irods.sh

# Run all tests
./run-tests.sh

# Or run individual tests
cd ..
PYTHONPATH=. python3 test_parsers.py
PYTHONPATH=. python3 test_filesystem.py
PYTHONPATH=. python3 test_irods_client.py
PYTHONPATH=. python3 test_complete_workflow.py
```

## Development

### Installing development dependencies

```bash
uv pip install -e ".[dev]"
```

### Running tests

```bash
# Run unit tests with pytest
pytest

# Run integration tests with iRODS
cd docker
./run-tests.sh
```

### Code formatting

```bash
black .
isort .
```

### Type checking

```bash
mypy rodrunner
```

## License

MIT
