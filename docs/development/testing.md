# Testing

This guide explains how to test the Rodrunner project.

## Test Structure

The tests are organized into the following directories:

- `test_filesystem`: Tests for the filesystem module
- `test_irods`: Tests for the iRODS client module
- `test_parsers`: Tests for the parsers module
- `test_workflows`: Tests for the Prefect workflows
- `test_api`: Tests for the FastAPI endpoints

## Test Categories

The tests are marked with the following categories:

- `unit`: Unit tests that don't require external services
- `integration`: Integration tests that require iRODS and/or Prefect
- `irods`: Tests that specifically require an iRODS server
- `api`: Tests for the API endpoints

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

## Writing Tests

### Writing Unit Tests

Unit tests should be marked with the `unit` marker and should not depend on external services:

```python
import pytest
from rodrunner.filesystem.find import find_files

@pytest.mark.unit
def test_find_files_basic(temp_dir):
    # Create test files
    # ...
    
    # Test finding all files
    files = list(find_files(temp_dir, file_type='f'))
    assert len(files) == 3
```

### Writing Integration Tests

Integration tests should be marked with the `integration` marker and may depend on external services:

```python
import pytest
from rodrunner.workflows.ingest import ingest_sequencer_runs

@pytest.mark.integration
def test_ingest_sequencer_runs(app_config, sample_sequencer_run, temp_dir):
    # Set up a test directory with a sequencer run
    # ...
    
    # Run the workflow
    results = ingest_sequencer_runs(
        config=app_config,
        sequencer_type="miseq",
        root_dir=miseq_dir
    )
    
    # Verify the results
    assert len(results) == 1
    assert results[0]["success"] is True
```

### Writing iRODS Tests

iRODS tests should be marked with the `irods` marker and depend on an iRODS server:

```python
import pytest
import os
from rodrunner.irods.client import iRODSClient

@pytest.mark.irods
def test_collection_operations(irods_client):
    # Generate a unique collection name for testing
    test_coll_name = f"/tempZone/home/rods/test_collection_{os.getpid()}"
    
    try:
        # Test collection creation
        assert not irods_client.collection_exists(test_coll_name)
        coll = irods_client.create_collection(test_coll_name)
        assert irods_client.collection_exists(test_coll_name)
    
    finally:
        # Clean up
        if irods_client.collection_exists(test_coll_name):
            irods_client.remove_collection(test_coll_name, recursive=True)
```

### Writing API Tests

API tests should be marked with the `api` marker and use the FastAPI test client:

```python
import pytest
from fastapi.testclient import TestClient

@pytest.mark.api
def test_api_root(api_client):
    """Test the API root endpoint."""
    response = api_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Welcome to the iRODS Prefect API"
```

## Test Coverage

The project uses pytest-cov to measure test coverage. You can generate a coverage report with:

```bash
python -m pytest --cov=rodrunner --cov-report=term-missing --cov-report=html
```

This will generate a coverage report in the terminal and an HTML report in the `htmlcov` directory.

## Continuous Integration

The project uses GitHub Actions for continuous integration. The CI pipeline runs the tests on every push and pull request.

The CI pipeline includes:

1. Setting up the environment
2. Installing dependencies
3. Running the tests
4. Generating a coverage report
5. Uploading the coverage report to Codecov

## Best Practices

- **Write tests for all new code**: Aim for high test coverage
- **Use appropriate markers**: Mark tests with the appropriate category
- **Clean up after tests**: Use fixtures and try/finally blocks to clean up resources
- **Use unique names**: Use unique names for test resources to avoid conflicts
- **Keep tests independent**: Tests should not depend on the state from other tests
- **Test edge cases**: Test both normal and error cases
- **Use assertions effectively**: Use specific assertions to check expected behavior
