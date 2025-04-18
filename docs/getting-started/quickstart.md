# Quickstart

This guide will help you get started with the Rodrunner project quickly. We'll cover the basic steps to ingest sequencer data into iRODS and query metadata.

## Prerequisites

Before starting, make sure you have:

- Installed the project following the [Installation Guide](installation.md)
- Configured the project following the [Configuration Guide](configuration.md)
- Access to an iRODS server (or using the Docker setup)
- Some sequencer data to ingest (or using the sample data)

## Using the Docker Setup

If you're using the Docker setup, you can use the sample data included in the project.

### Step 1: Start the Docker containers

```bash
docker-compose up -d
```

### Step 2: Access the API

The API will be available at http://localhost:8000. You can check the API documentation at http://localhost:8000/docs.

## Ingesting Sequencer Data

There are two ways to ingest sequencer data:

1. Using the API
2. Running the workflows directly

### Using the API

#### Step 1: Check available workflows

```bash
curl http://localhost:8000/workflows/list
```

This will return a list of available workflows, including the ingest workflows.

#### Step 2: Run the ingest workflow

```bash
curl -X POST http://localhost:8000/workflows/run \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_name": "Ingest Sequencer Runs",
    "parameters": {
      "sequencer_type": "miseq",
      "root_dir": "/data/sequencer/miseq"
    }
  }'
```

This will start the ingest workflow for MiSeq data and return a flow run ID.

#### Step 3: Check the workflow status

```bash
curl http://localhost:8000/workflows/status/{flow_run_id}
```

Replace `{flow_run_id}` with the ID returned from the previous step.

### Running Workflows Directly

You can also run the workflows directly using Python:

```python
from rodrunner.config import get_config
from rodrunner.workflows.ingest import ingest_sequencer_runs

# Load the configuration
config = get_config()

# Run the ingest workflow
results = ingest_sequencer_runs(
    config=config,
    sequencer_type="miseq",
    root_dir="/data/sequencer/miseq"
)

# Print the results
for result in results:
    print(f"Run: {result['run_dir']}, Success: {result['success']}")
```

## Querying Metadata

Once you've ingested data, you can query the metadata using the API.

### Search for Metadata by Key and Value

```bash
curl "http://localhost:8000/metadata/search?key=run_id&value=220101_M00001_0001_000000000-A1B2C"
```

This will return all objects with the specified metadata key and value.

### Get Metadata for a Specific Object

```bash
curl "http://localhost:8000/metadata/object?path=/tempZone/home/rods/sequencer/miseq/220101_M00001_0001_000000000-A1B2C"
```

This will return the metadata for the specified object.

## Using the Python Client

You can also use the Python client to interact with iRODS directly:

```python
from rodrunner.config import get_config
from rodrunner.irods.client import iRODSClient

# Load the configuration
config = get_config()

# Create an iRODS client
irods_client = iRODSClient(config.irods)

# Check if a collection exists
if irods_client.collection_exists("/tempZone/home/rods/sequencer/miseq"):
    print("Collection exists")

# Get a collection
collection = irods_client.get_collection("/tempZone/home/rods/sequencer/miseq")

# Print metadata
for meta in collection.metadata.items():
    print(f"{meta.name}: {meta.value}")
```

## Next Steps

Now that you've completed the quickstart, you can:

- Explore the [User Guide](../user-guide/overview.md) for more detailed information
- Learn about the [Filesystem Operations](../user-guide/filesystem.md)
- Learn about the [iRODS Client](../user-guide/irods-client.md)
- Learn about the [Parsers](../user-guide/parsers.md)
- Learn about the [Workflows](../user-guide/workflows.md)
- Learn about the [API](../user-guide/api.md)
