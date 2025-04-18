# API

The API module provides a FastAPI-based REST API for interacting with the workflows and querying metadata. It includes endpoints for running workflows, checking workflow status, and querying metadata.

## Key Features

- **FastAPI-based REST API** for easy integration
- **Workflow endpoints** for running and monitoring workflows
- **Metadata endpoints** for querying and updating metadata
- **Pydantic models** for request and response validation
- **OpenAPI documentation** for easy exploration

## API Endpoints

### Root Endpoints

- `GET /`: Welcome message
- `GET /health`: Health check endpoint

### Workflow Endpoints

- `GET /workflows/list`: List available workflows
- `POST /workflows/run`: Run a workflow
- `GET /workflows/status/{flow_run_id}`: Get workflow status

### Metadata Endpoints

- `GET /metadata/search`: Search for metadata by key and value
- `GET /metadata/object`: Get metadata for a specific object
- `POST /metadata/update`: Update metadata for an object

## Basic Usage

### Starting the API Server

```bash
# Using uvicorn directly
uvicorn rodrunner.api.main:app --host 0.0.0.0 --port 8000 --reload

# Using the main module
python -m rodrunner.api.main
```

### Accessing the API Documentation

The API documentation is available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Using the API

#### List Available Workflows

```bash
curl http://localhost:8000/workflows/list
```

Response:
```json
[
  {
    "name": "Ingest Sequencer Runs",
    "description": "Ingest all completed sequencer runs of a specific type.",
    "parameters": {
      "sequencer_type": "string",
      "root_dir": "string (optional)",
      "completion_indicator": "string (optional)"
    }
  },
  {
    "name": "Ingest All Sequencer Runs",
    "description": "Ingest all completed sequencer runs of all supported types.",
    "parameters": {
      "root_dir": "string (optional)",
      "completion_indicator": "string (optional)"
    }
  },
  {
    "name": "Update Run Metadata",
    "description": "Update metadata for a sequencer run in iRODS.",
    "parameters": {
      "irods_path": "string",
      "sequencer_type": "string"
    }
  }
]
```

#### Run a Workflow

```bash
curl -X POST http://localhost:8000/workflows/run \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_name": "Ingest Sequencer Runs",
    "parameters": {
      "sequencer_type": "miseq",
      "root_dir": "/path/to/sequencer/miseq"
    }
  }'
```

Response:
```json
{
  "flow_run_id": "12345678-1234-5678-1234-567812345678",
  "status": "RUNNING",
  "start_time": "2023-04-18T12:34:56.789Z"
}
```

#### Check Workflow Status

```bash
curl http://localhost:8000/workflows/status/12345678-1234-5678-1234-567812345678
```

Response:
```json
{
  "flow_run_id": "12345678-1234-5678-1234-567812345678",
  "status": "COMPLETED",
  "start_time": "2023-04-18T12:34:56.789Z",
  "end_time": "2023-04-18T12:45:12.345Z",
  "result": {
    "success": true,
    "message": "Workflow completed successfully",
    "details": [
      {
        "run_dir": "/path/to/sequencer/miseq/220101_M00001_0001_000000000-A1B2C",
        "success": true,
        "irods_path": "/tempZone/home/rods/sequencer/miseq/220101_M00001_0001_000000000-A1B2C"
      }
    ]
  }
}
```

#### Search for Metadata

```bash
curl "http://localhost:8000/metadata/search?key=run_id&value=220101_M00001_0001_000000000-A1B2C"
```

Response:
```json
[
  {
    "path": "/tempZone/home/rods/sequencer/miseq/220101_M00001_0001_000000000-A1B2C",
    "type": "collection",
    "metadata": {
      "run_id": "220101_M00001_0001_000000000-A1B2C",
      "instrument": "M00001",
      "date": "1/1/2022",
      "chemistry": "Amplicon",
      "sample_count": "2",
      "run_type": "miseq",
      "status": "metadata_extracted"
    }
  }
]
```

#### Get Metadata for a Specific Object

```bash
curl "http://localhost:8000/metadata/object?path=/tempZone/home/rods/sequencer/miseq/220101_M00001_0001_000000000-A1B2C"
```

Response:
```json
{
  "path": "/tempZone/home/rods/sequencer/miseq/220101_M00001_0001_000000000-A1B2C",
  "type": "collection",
  "metadata": {
    "run_id": "220101_M00001_0001_000000000-A1B2C",
    "instrument": "M00001",
    "date": "1/1/2022",
    "chemistry": "Amplicon",
    "sample_count": "2",
    "run_type": "miseq",
    "status": "metadata_extracted"
  }
}
```

#### Update Metadata

```bash
curl -X POST http://localhost:8000/metadata/update \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/tempZone/home/rods/sequencer/miseq/220101_M00001_0001_000000000-A1B2C",
    "metadata": {
      "status": "processed",
      "processing_date": "2023-04-18"
    }
  }'
```

Response:
```json
{
  "success": true,
  "path": "/tempZone/home/rods/sequencer/miseq/220101_M00001_0001_000000000-A1B2C",
  "metadata": {
    "status": "processed",
    "processing_date": "2023-04-18"
  }
}
```

## Advanced Usage

### Using the API with Python Requests

```python
import requests

# Base URL for the API
base_url = "http://localhost:8000"

# List available workflows
response = requests.get(f"{base_url}/workflows/list")
workflows = response.json()
print(workflows)

# Run a workflow
workflow_data = {
    "workflow_name": "Ingest Sequencer Runs",
    "parameters": {
        "sequencer_type": "miseq",
        "root_dir": "/path/to/sequencer/miseq"
    }
}
response = requests.post(f"{base_url}/workflows/run", json=workflow_data)
run_info = response.json()
flow_run_id = run_info["flow_run_id"]
print(f"Flow run ID: {flow_run_id}")

# Check workflow status
response = requests.get(f"{base_url}/workflows/status/{flow_run_id}")
status = response.json()
print(f"Status: {status['status']}")

# Search for metadata
response = requests.get(
    f"{base_url}/metadata/search",
    params={"key": "run_id", "value": "220101_M00001_0001_000000000-A1B2C"}
)
search_results = response.json()
print(search_results)

# Get metadata for a specific object
response = requests.get(
    f"{base_url}/metadata/object",
    params={"path": "/tempZone/home/rods/sequencer/miseq/220101_M00001_0001_000000000-A1B2C"}
)
object_metadata = response.json()
print(object_metadata)

# Update metadata
metadata_data = {
    "path": "/tempZone/home/rods/sequencer/miseq/220101_M00001_0001_000000000-A1B2C",
    "metadata": {
        "status": "processed",
        "processing_date": "2023-04-18"
    }
}
response = requests.post(f"{base_url}/metadata/update", json=metadata_data)
update_result = response.json()
print(update_result)
```

### Creating a Custom API Client

```python
import requests
from typing import Dict, Any, List, Optional

class RodRunnerClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List available workflows."""
        response = requests.get(f"{self.base_url}/workflows/list")
        response.raise_for_status()
        return response.json()
    
    def run_workflow(self, workflow_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Run a workflow."""
        workflow_data = {
            "workflow_name": workflow_name,
            "parameters": parameters
        }
        response = requests.post(f"{self.base_url}/workflows/run", json=workflow_data)
        response.raise_for_status()
        return response.json()
    
    def get_workflow_status(self, flow_run_id: str) -> Dict[str, Any]:
        """Get workflow status."""
        response = requests.get(f"{self.base_url}/workflows/status/{flow_run_id}")
        response.raise_for_status()
        return response.json()
    
    def search_metadata(self, key: str, value: str) -> List[Dict[str, Any]]:
        """Search for metadata by key and value."""
        response = requests.get(
            f"{self.base_url}/metadata/search",
            params={"key": key, "value": value}
        )
        response.raise_for_status()
        return response.json()
    
    def get_object_metadata(self, path: str) -> Dict[str, Any]:
        """Get metadata for a specific object."""
        response = requests.get(
            f"{self.base_url}/metadata/object",
            params={"path": path}
        )
        response.raise_for_status()
        return response.json()
    
    def update_metadata(self, path: str, metadata: Dict[str, str]) -> Dict[str, Any]:
        """Update metadata for an object."""
        metadata_data = {
            "path": path,
            "metadata": metadata
        }
        response = requests.post(f"{self.base_url}/metadata/update", json=metadata_data)
        response.raise_for_status()
        return response.json()

# Usage
client = RodRunnerClient()
workflows = client.list_workflows()
print(workflows)

run_info = client.run_workflow(
    workflow_name="Ingest Sequencer Runs",
    parameters={
        "sequencer_type": "miseq",
        "root_dir": "/path/to/sequencer/miseq"
    }
)
print(run_info)
```

## Examples

### Complete Workflow with API

```python
import requests
import time
from typing import Dict, Any

def run_complete_workflow(
    api_url: str,
    sequencer_type: str,
    root_dir: str,
    poll_interval: int = 10,
    timeout: int = 3600
) -> Dict[str, Any]:
    """Run a complete workflow and wait for it to finish."""
    # Base URL for the API
    base_url = api_url.rstrip("/")
    
    # Run the ingest workflow
    workflow_data = {
        "workflow_name": "Ingest Sequencer Runs",
        "parameters": {
            "sequencer_type": sequencer_type,
            "root_dir": root_dir
        }
    }
    response = requests.post(f"{base_url}/workflows/run", json=workflow_data)
    response.raise_for_status()
    run_info = response.json()
    flow_run_id = run_info["flow_run_id"]
    print(f"Started workflow with flow run ID: {flow_run_id}")
    
    # Poll for workflow completion
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = requests.get(f"{base_url}/workflows/status/{flow_run_id}")
        response.raise_for_status()
        status = response.json()
        
        if status["status"] in ["COMPLETED", "FAILED"]:
            print(f"Workflow {status['status']}")
            return status
        
        print(f"Workflow status: {status['status']}")
        time.sleep(poll_interval)
    
    raise TimeoutError(f"Workflow did not complete within {timeout} seconds")

# Run the workflow
result = run_complete_workflow(
    api_url="http://localhost:8000",
    sequencer_type="miseq",
    root_dir="/path/to/sequencer/miseq",
    poll_interval=30,
    timeout=7200
)

# Process the results
if result["status"] == "COMPLETED" and result.get("result", {}).get("success", False):
    print("Workflow completed successfully")
    
    # Get the iRODS paths for the ingested runs
    irods_paths = []
    for detail in result.get("result", {}).get("details", []):
        if detail.get("success", False) and "irods_path" in detail:
            irods_paths.append(detail["irods_path"])
    
    print(f"Ingested {len(irods_paths)} runs:")
    for path in irods_paths:
        print(f"- {path}")
else:
    print("Workflow failed")
    print(result.get("result", {}).get("message", "Unknown error"))
```

### Batch Processing with the API

```python
import requests
import concurrent.futures
from typing import Dict, Any, List

def process_sequencer_type(api_url: str, sequencer_type: str, root_dir: str) -> Dict[str, Any]:
    """Process a single sequencer type."""
    # Base URL for the API
    base_url = api_url.rstrip("/")
    
    # Run the ingest workflow
    workflow_data = {
        "workflow_name": "Ingest Sequencer Runs",
        "parameters": {
            "sequencer_type": sequencer_type,
            "root_dir": f"{root_dir}/{sequencer_type}"
        }
    }
    response = requests.post(f"{base_url}/workflows/run", json=workflow_data)
    response.raise_for_status()
    run_info = response.json()
    
    return {
        "sequencer_type": sequencer_type,
        "flow_run_id": run_info["flow_run_id"],
        "status": run_info["status"]
    }

def batch_process_sequencers(
    api_url: str,
    root_dir: str,
    sequencer_types: List[str]
) -> List[Dict[str, Any]]:
    """Process multiple sequencer types in parallel."""
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(sequencer_types)) as executor:
        future_to_type = {
            executor.submit(process_sequencer_type, api_url, seq_type, root_dir): seq_type
            for seq_type in sequencer_types
        }
        
        for future in concurrent.futures.as_completed(future_to_type):
            sequencer_type = future_to_type[future]
            try:
                result = future.result()
                results.append(result)
                print(f"Started workflow for {sequencer_type}: {result['flow_run_id']}")
            except Exception as e:
                print(f"Error processing {sequencer_type}: {str(e)}")
                results.append({
                    "sequencer_type": sequencer_type,
                    "error": str(e)
                })
    
    return results

# Process multiple sequencer types
results = batch_process_sequencers(
    api_url="http://localhost:8000",
    root_dir="/path/to/sequencer",
    sequencer_types=["miseq", "novaseq", "pacbio", "nanopore"]
)

print(results)
```

## API Reference

For detailed API documentation, see the [API Endpoints Reference](../api-reference/api-endpoints.md).
