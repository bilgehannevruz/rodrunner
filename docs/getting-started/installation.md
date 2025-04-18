# Installation

This guide will walk you through the installation process for the Rodrunner project.

## Prerequisites

Before installing the project, ensure you have the following prerequisites:

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) for package management (recommended)
- Docker and Docker Compose (for running with iRODS and Prefect servers)
- Access to an iRODS server (or use the provided Docker setup)

## Installation Methods

There are two main ways to install and run the project:

1. **Docker-based installation** (recommended for development and testing)
2. **Local installation** (for production or custom setups)

## Docker-based Installation

The Docker-based installation is the easiest way to get started with the project. It includes all the necessary components, including an iRODS server and Prefect server.

### Step 1: Clone the repository

```bash
git clone https://github.com/bilgehannevruz/rodrunner.git
cd rodrunner
```

### Step 2: Start the Docker containers

```bash
docker-compose up -d
```

This will start the following containers:
- iRODS catalog provider (iCAT server)
- Prefect server
- The application container with the Rodrunner

### Step 3: Verify the installation

```bash
# Check that all containers are running
docker-compose ps

# Check the API is accessible
curl http://localhost:8000/health
```

## Local Installation

For a local installation, you'll need to install the package and its dependencies.

### Step 1: Clone the repository

```bash
git clone https://github.com/bilgehannevruz/rodrunner.git
cd rodrunner
```

### Step 2: Create a virtual environment and install dependencies

Using `uv` (recommended):

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

Using `pip`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Step 3: Configure the application

Create a `.env` file in the project root with your iRODS and Prefect configuration:

```
IRODS_HOST=localhost
IRODS_PORT=1247
IRODS_USER=rods
IRODS_PASSWORD=rods
IRODS_ZONE=tempZone
IRODS_RESOURCE=demoResc

PREFECT_API_URL=http://localhost:4200/api

SEQUENCER_BASE_DIR=/path/to/sequencer/data
SEQUENCER_MISEQ_DIR=/path/to/sequencer/data/miseq
SEQUENCER_NOVASEQ_DIR=/path/to/sequencer/data/novaseq
SEQUENCER_PACBIO_DIR=/path/to/sequencer/data/pacbio
SEQUENCER_NANOPORE_DIR=/path/to/sequencer/data/nanopore
SEQUENCER_NOVASEQXPLUS_DIR=/path/to/sequencer/data/novaseqxplus

API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true
```

### Step 4: Start the API server

```bash
uvicorn rodrunner.api.main:app --host 0.0.0.0 --port 8000 --reload
```

## Next Steps

Now that you have installed the project, you can:

- [Configure the application](configuration.md) for your specific needs
- Follow the [Quickstart guide](quickstart.md) to run your first workflow
- Explore the [User Guide](../user-guide/overview.md) for more detailed information
