# Workflows

The workflows module provides Prefect v3 workflows for data ingestion and metadata management. It includes workflows for ingesting sequencer data, updating metadata, and more.

## Key Features

- **Prefect v3 workflows** for orchestrating complex tasks
- **Sequencer-specific workflows** for different sequencer types
- **Metadata extraction and management** workflows
- **Error handling and notifications** for workflow failures
- **Integration with iRODS** for data management

## Available Workflows

The following workflows are available:

- **Ingest Sequencer Runs**: Ingests sequencer runs of a specific type
- **Ingest All Sequencer Runs**: Ingests sequencer runs of all supported types
- **Update Run Metadata**: Updates metadata for a sequencer run in iRODS

## Basic Usage

### Running Workflows Directly

You can run the workflows directly using Python:

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

### Running Workflows via the API

You can also run the workflows via the API:

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

## Workflow Details

### Ingest Sequencer Runs

The `ingest_sequencer_runs` workflow ingests sequencer runs of a specific type:

```python
from rodrunner.config import get_config
from rodrunner.workflows.ingest import ingest_sequencer_runs

# Load the configuration
config = get_config()

# Run the ingest workflow
results = ingest_sequencer_runs(
    config=config,
    sequencer_type="miseq",
    root_dir="/path/to/sequencer/miseq",
    completion_indicator="RTAComplete.txt"
)
```

Parameters:
- `config`: Application configuration
- `sequencer_type`: Type of sequencer (miseq, nextseq, novaseq, etc.)
- `root_dir`: Root directory to search for sequencer runs (defaults to config.sequencer.base_dir)
- `completion_indicator`: Filename that indicates a completed run (defaults to "RTAComplete.txt")

Returns:
- List of dictionaries with the results of the ingestion

### Ingest All Sequencer Runs

The `ingest_all_sequencer_runs` workflow ingests sequencer runs of all supported types:

```python
from rodrunner.config import get_config
from rodrunner.workflows.ingest import ingest_all_sequencer_runs

# Load the configuration
config = get_config()

# Run the ingest workflow
results = ingest_all_sequencer_runs(
    config=config,
    root_dir="/path/to/sequencer",
    completion_indicator="RTAComplete.txt"
)
```

Parameters:
- `config`: Application configuration
- `root_dir`: Root directory to search for sequencer runs (defaults to config.sequencer.base_dir)
- `completion_indicator`: Filename that indicates a completed run (defaults to "RTAComplete.txt")

Returns:
- Dictionary mapping sequencer types to lists of ingestion results

### Update Run Metadata

The `update_run_metadata` workflow updates metadata for a sequencer run in iRODS:

```python
from rodrunner.config import get_config
from rodrunner.workflows.metadata import update_run_metadata

# Load the configuration
config = get_config()

# Run the metadata update workflow
result = update_run_metadata(
    config=config,
    irods_path="/tempZone/home/rods/sequencer/miseq/220101_M00001_0001_000000000-A1B2C",
    sequencer_type="miseq"
)
```

Parameters:
- `config`: Application configuration
- `irods_path`: Path to the sequencer run in iRODS
- `sequencer_type`: Type of sequencer (miseq, nextseq, novaseq, etc.)

Returns:
- Dictionary with the result of the metadata update

## Advanced Usage

### Scheduling Workflows

You can schedule workflows to run at specific intervals using Prefect:

```python
from prefect import flow
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule

from rodrunner.config import get_config
from rodrunner.workflows.ingest import ingest_all_sequencer_runs

# Create a deployment
deployment = Deployment.build_from_flow(
    flow=ingest_all_sequencer_runs,
    name="scheduled-ingest",
    schedule=CronSchedule(cron="0 0 * * *"),  # Run daily at midnight
    parameters={
        "config": get_config(),
        "root_dir": "/path/to/sequencer"
    }
)

# Apply the deployment
deployment.apply()
```

### Customizing Workflows

You can customize the workflows by creating your own flows that call the existing tasks:

```python
from prefect import flow, task
from rodrunner.config import get_config
from rodrunner.tasks.filesystem import find_sequencer_runs_task
from rodrunner.tasks.parsing import parse_sequencer_run
from rodrunner.irods.client import iRODSClient

@task
def process_run(run_dir, config):
    # Parse the run metadata
    metadata = parse_sequencer_run(run_dir)
    
    # Create an iRODS client
    irods_client = iRODSClient(config.irods)
    
    # Upload the run to iRODS
    irods_path = f"/tempZone/home/rods/sequencer/{os.path.basename(run_dir)}"
    irods_client.upload_directory(run_dir, irods_path, metadata=metadata)
    
    return {
        "run_dir": run_dir,
        "irods_path": irods_path,
        "success": True
    }

@flow
def custom_ingest_workflow(config, sequencer_type, root_dir):
    # Find sequencer runs
    run_dirs = find_sequencer_runs_task(
        root_dir=root_dir,
        sequencer_type=sequencer_type
    )
    
    # Process each run
    results = []
    for run_dir in run_dirs:
        result = process_run(run_dir, config)
        results.append(result)
    
    return results
```

### Error Handling and Notifications

You can add error handling and notifications to your workflows:

```python
from prefect import flow, task
from prefect.tasks import task_input_hash
from datetime import timedelta
import smtplib
from email.message import EmailMessage

@task(cache_key_fn=task_input_hash, cache_expiration=timedelta(hours=1))
def send_notification(subject, message, to_email):
    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = subject
    msg['From'] = 'noreply@example.com'
    msg['To'] = to_email
    
    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.starttls()
        server.login('username', 'password')
        server.send_message(msg)
    
    return True

@flow
def ingest_with_notifications(config, sequencer_type, root_dir, notify_email):
    try:
        # Run the ingest workflow
        results = ingest_sequencer_runs(
            config=config,
            sequencer_type=sequencer_type,
            root_dir=root_dir
        )
        
        # Count successes and failures
        successes = sum(1 for r in results if r.get('success', False))
        failures = len(results) - successes
        
        # Send notification
        subject = f"Ingest Workflow Completed: {successes} succeeded, {failures} failed"
        message = f"Ingest workflow for {sequencer_type} completed.\n\n"
        message += f"Successes: {successes}\n"
        message += f"Failures: {failures}\n\n"
        
        if failures > 0:
            message += "Failed runs:\n"
            for result in results:
                if not result.get('success', False):
                    message += f"- {result.get('run_dir', 'Unknown')}: {result.get('error', 'Unknown error')}\n"
        
        send_notification(subject, message, notify_email)
        
        return results
    
    except Exception as e:
        # Send error notification
        subject = f"Ingest Workflow Failed: {str(e)}"
        message = f"Ingest workflow for {sequencer_type} failed with error:\n\n{str(e)}"
        send_notification(subject, message, notify_email)
        
        raise
```

## Examples

### Complete Ingest and Metadata Update Workflow

```python
from rodrunner.config import get_config
from rodrunner.workflows.ingest import ingest_sequencer_runs
from rodrunner.workflows.metadata import update_run_metadata
from prefect import flow

@flow
def complete_ingest_workflow(sequencer_type, root_dir):
    # Load the configuration
    config = get_config()
    
    # Run the ingest workflow
    ingest_results = ingest_sequencer_runs(
        config=config,
        sequencer_type=sequencer_type,
        root_dir=root_dir
    )
    
    # Update metadata for each successful ingest
    metadata_results = []
    for result in ingest_results:
        if result.get('success', False) and 'irods_path' in result:
            metadata_result = update_run_metadata(
                config=config,
                irods_path=result['irods_path'],
                sequencer_type=sequencer_type
            )
            metadata_results.append(metadata_result)
    
    return {
        "ingest_results": ingest_results,
        "metadata_results": metadata_results
    }

# Run the workflow
results = complete_ingest_workflow("miseq", "/path/to/sequencer/miseq")
print(results)
```

### Parallel Processing of Multiple Sequencer Types

```python
from rodrunner.config import get_config
from rodrunner.workflows.ingest import ingest_sequencer_runs
from prefect import flow, task
from concurrent.futures import ThreadPoolExecutor

@task
def ingest_sequencer_type(config, sequencer_type, root_dir):
    return {
        "sequencer_type": sequencer_type,
        "results": ingest_sequencer_runs(
            config=config,
            sequencer_type=sequencer_type,
            root_dir=f"{root_dir}/{sequencer_type}"
        )
    }

@flow
def parallel_ingest_workflow(root_dir, sequencer_types):
    # Load the configuration
    config = get_config()
    
    # Process each sequencer type in parallel
    with ThreadPoolExecutor(max_workers=len(sequencer_types)) as executor:
        futures = []
        for sequencer_type in sequencer_types:
            future = executor.submit(
                ingest_sequencer_type.fn,
                config=config,
                sequencer_type=sequencer_type,
                root_dir=root_dir
            )
            futures.append(future)
        
        # Collect results
        results = {}
        for future in futures:
            result = future.result()
            results[result["sequencer_type"]] = result["results"]
    
    return results

# Run the workflow
results = parallel_ingest_workflow(
    root_dir="/path/to/sequencer",
    sequencer_types=["miseq", "novaseq", "pacbio"]
)
print(results)
```

## API Reference

For detailed API documentation, see the [Workflows API Reference](../api-reference/workflows.md).
