# Configuration

This guide explains how to configure the Rodrunner project for your environment.

## Configuration Methods

The project can be configured using:

1. Environment variables
2. A `.env` file in the project root
3. A configuration file

The configuration is loaded in the following order, with later methods overriding earlier ones:
1. Default values
2. Configuration file
3. `.env` file
4. Environment variables

## Configuration Options

### iRODS Configuration

| Environment Variable | Description | Default |
|----------------------|-------------|---------|
| `IRODS_HOST` | iRODS server hostname | `localhost` |
| `IRODS_PORT` | iRODS server port | `1247` |
| `IRODS_USER` | iRODS username | `rods` |
| `IRODS_PASSWORD` | iRODS password | `rods` |
| `IRODS_ZONE` | iRODS zone name | `tempZone` |
| `IRODS_RESOURCE` | Default iRODS resource | `demoResc` |

### Sequencer Configuration

| Environment Variable | Description | Default |
|----------------------|-------------|---------|
| `SEQUENCER_BASE_DIR` | Base directory for all sequencer data | `/data/sequencer` |
| `SEQUENCER_MISEQ_DIR` | Directory for MiSeq data | `/data/sequencer/miseq` |
| `SEQUENCER_NOVASEQ_DIR` | Directory for NovaSeq data | `/data/sequencer/novaseq` |
| `SEQUENCER_PACBIO_DIR` | Directory for PacBio data | `/data/sequencer/pacbio` |
| `SEQUENCER_NANOPORE_DIR` | Directory for Nanopore data | `/data/sequencer/nanopore` |
| `SEQUENCER_NOVASEQXPLUS_DIR` | Directory for NovaSeqXPlus data | `/data/sequencer/novaseqxplus` |

### API Configuration

| Environment Variable | Description | Default |
|----------------------|-------------|---------|
| `API_HOST` | Host to bind the API server | `0.0.0.0` |
| `API_PORT` | Port for the API server | `8000` |
| `API_DEBUG` | Enable debug mode for the API | `false` |

### Prefect Configuration

| Environment Variable | Description | Default |
|----------------------|-------------|---------|
| `PREFECT_API_URL` | URL for the Prefect API | `http://localhost:4200/api` |

## Example .env File

```
IRODS_HOST=localhost
IRODS_PORT=1247
IRODS_USER=rods
IRODS_PASSWORD=rods
IRODS_ZONE=tempZone
IRODS_RESOURCE=demoResc

PREFECT_API_URL=http://localhost:4200/api

SEQUENCER_BASE_DIR=/data/sequencer
SEQUENCER_MISEQ_DIR=/data/sequencer/miseq
SEQUENCER_NOVASEQ_DIR=/data/sequencer/novaseq
SEQUENCER_PACBIO_DIR=/data/sequencer/pacbio
SEQUENCER_NANOPORE_DIR=/data/sequencer/nanopore
SEQUENCER_NOVASEQXPLUS_DIR=/data/sequencer/novaseqxplus

API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true
```

## Docker Configuration

When using Docker, you can configure the application by:

1. Creating a `.env` file in the project root
2. Modifying the `docker-compose.yml` file to include environment variables
3. Using Docker Compose environment files

### Example Docker Compose Environment Configuration

```yaml
version: '3'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - IRODS_HOST=irods-catalog
      - IRODS_PORT=1247
      - IRODS_USER=rods
      - IRODS_PASSWORD=rods
      - IRODS_ZONE=tempZone
      - IRODS_RESOURCE=demoResc
      - PREFECT_API_URL=http://prefect:4200/api
      - SEQUENCER_BASE_DIR=/data/sequencer
      - API_DEBUG=true
    volumes:
      - ./data:/data
```

## Configuration in Code

The configuration is loaded using the `get_config()` function from the `rodrunner.config` module:

```python
from rodrunner.config import get_config

# Load the configuration
config = get_config()

# Access configuration values
irods_host = config.irods.host
sequencer_base_dir = config.sequencer.base_dir
```

## Next Steps

Now that you have configured the project, you can:

- Follow the [Quickstart guide](quickstart.md) to run your first workflow
- Explore the [User Guide](../user-guide/overview.md) for more detailed information
