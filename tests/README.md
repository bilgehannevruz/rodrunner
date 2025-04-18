# Tests for Rodrunner

This directory contains tests for the Rodrunner project.

## Test Structure

The tests are organized into the following directories:

- `test_filesystem`: Tests for the filesystem module
- `test_irods`: Tests for the iRODS client module
- `test_parsers`: Tests for the parsers module
- `test_workflows`: Tests for the Prefect workflows
- `test_api`: Tests for the FastAPI endpoints

## Running Tests

The tests are designed to be run inside the Docker container environment, which includes an iRODS server and Prefect server.

### Running All Tests

```bash
cd /home/bcn/repos/irods/augment-imp
python -m pytest
```

### Running Tests with Coverage

```bash
cd /home/bcn/repos/irods/augment-imp
python -m pytest --cov=rodrunner
```

### Running Specific Test Categories

The tests are marked with the following categories:

- `unit`: Unit tests that don't require external services
- `integration`: Integration tests that require iRODS and/or Prefect
- `irods`: Tests that specifically require an iRODS server
- `api`: Tests for the API endpoints

To run tests from a specific category:

```bash
# Run only unit tests
python -m pytest -m unit

# Run only integration tests
python -m pytest -m integration

# Run only iRODS tests
python -m pytest -m irods

# Run only API tests
python -m pytest -m api
```

### Running Tests from a Specific Module

```bash
# Run tests for the filesystem module
python -m pytest tests/test_filesystem

# Run tests for a specific test file
python -m pytest tests/test_filesystem/test_find.py

# Run a specific test function
python -m pytest tests/test_filesystem/test_find.py::test_find_files_basic
```

## Test Configuration

The tests use the application configuration from environment variables or config files. Make sure the following environment variables are set or a `.env` file is present:

```
IRODS_HOST=localhost
IRODS_PORT=1247
IRODS_USER=rods
IRODS_PASSWORD=rods
IRODS_ZONE=tempZone
IRODS_RESOURCE=demoResc
```

## Test Fixtures

Common test fixtures are defined in `conftest.py`. These include:

- `temp_dir`: A temporary directory that is cleaned up after the test
- `app_config`: The application configuration
- `irods_client`: An iRODS client instance
- `api_client`: A FastAPI test client
- `sample_run_info_xml`, `sample_run_parameters_xml`, `sample_samplesheet_csv`: Sample file contents for testing
- `sample_sequencer_run`: A sample sequencer run directory with all required files
