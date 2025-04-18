# API Endpoints Reference

This page contains the reference for the API endpoints.

## Root Endpoints

### `GET /`

Returns a welcome message.

#### Response

```json
{
  "message": "Welcome to the iRODS Prefect API"
}
```

### `GET /health`

Returns the health status of the API.

#### Response

```json
{
  "status": "ok"
}
```

## Workflow Endpoints

### `GET /workflows/list`

Returns a list of available workflows.

#### Response

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

### `POST /workflows/run`

Runs a workflow.

#### Request

```json
{
  "workflow_name": "Ingest Sequencer Runs",
  "parameters": {
    "sequencer_type": "miseq",
    "root_dir": "/path/to/sequencer/miseq"
  }
}
```

#### Response

```json
{
  "flow_run_id": "12345678-1234-5678-1234-567812345678",
  "status": "RUNNING",
  "start_time": "2023-04-18T12:34:56.789Z"
}
```

### `GET /workflows/status/{flow_run_id}`

Returns the status of a workflow.

#### Parameters

- `flow_run_id`: ID of the workflow run

#### Response

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

## Metadata Endpoints

### `GET /metadata/search`

Searches for metadata by key and value.

#### Parameters

- `key`: Metadata key
- `value`: Metadata value

#### Response

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

### `GET /metadata/object`

Returns metadata for a specific object.

#### Parameters

- `path`: Path to the object

#### Response

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

### `POST /metadata/update`

Updates metadata for an object.

#### Request

```json
{
  "path": "/tempZone/home/rods/sequencer/miseq/220101_M00001_0001_000000000-A1B2C",
  "metadata": {
    "status": "processed",
    "processing_date": "2023-04-18"
  }
}
```

#### Response

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

## Error Responses

### 400 Bad Request

Returned when the request is invalid.

```json
{
  "detail": "Invalid request"
}
```

### 404 Not Found

Returned when the requested resource is not found.

```json
{
  "detail": "Resource not found"
}
```

### 422 Unprocessable Entity

Returned when the request is valid but cannot be processed.

```json
{
  "detail": [
    {
      "loc": ["body", "workflow_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error

Returned when an internal server error occurs.

```json
{
  "detail": "Internal server error"
}
```

## Using the API

### Example: Running a Workflow

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

### Example: Checking Workflow Status

```bash
curl http://localhost:8000/workflows/status/12345678-1234-5678-1234-567812345678
```

### Example: Searching for Metadata

```bash
curl "http://localhost:8000/metadata/search?key=run_id&value=220101_M00001_0001_000000000-A1B2C"
```

### Example: Getting Metadata for an Object

```bash
curl "http://localhost:8000/metadata/object?path=/tempZone/home/rods/sequencer/miseq/220101_M00001_0001_000000000-A1B2C"
```

### Example: Updating Metadata

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
