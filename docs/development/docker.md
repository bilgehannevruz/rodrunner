# Docker

This guide explains how to use Docker with the Rodrunner project.

## Docker Setup

The project includes Docker configuration for running the application with all its dependencies, including an iRODS server and Prefect server.

### Docker Components

The Docker setup includes the following components:

- **Application Container**: The main application container with the Rodrunner
- **iRODS Catalog Provider**: The iRODS iCAT server
- **Prefect Server**: The Prefect server for workflow orchestration

### Docker Files

The project includes the following Docker files:

- `Dockerfile`: The main Dockerfile for the application container
- `docker-compose.yml`: The Docker Compose configuration for running all containers
- `docker/irods_catalog/Dockerfile`: Dockerfile for the iRODS catalog provider
- `docker/irods_catalog_provider/setup_irods.sh`: Script for setting up the iRODS server
- `docker/prefect_data/Dockerfile`: Dockerfile for the Prefect server

## Building and Running with Docker

### Prerequisites

- Docker
- Docker Compose

### Building the Docker Images

```bash
# Build all images
docker-compose build

# Build a specific image
docker-compose build app
```

### Running the Docker Containers

```bash
# Start all containers
docker-compose up -d

# Start a specific container
docker-compose up -d app

# View container logs
docker-compose logs -f

# View logs for a specific container
docker-compose logs -f app
```

### Stopping the Docker Containers

```bash
# Stop all containers
docker-compose down

# Stop a specific container
docker-compose stop app
```

## Docker Configuration

### Environment Variables

You can configure the Docker containers using environment variables in the `docker-compose.yml` file or a `.env` file.

Example `.env` file:

```
IRODS_HOST=irods-catalog
IRODS_PORT=1247
IRODS_USER=rods
IRODS_PASSWORD=rods
IRODS_ZONE=tempZone
IRODS_RESOURCE=demoResc

PREFECT_API_URL=http://prefect:4200/api

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

### Volumes

The Docker setup includes the following volumes:

- `./data`: Mounted to `/data` in the application container for storing sequencer data
- `./docker/irods_catalog_provider`: Mounted to `/etc/irods` in the iRODS container for iRODS configuration
- `./docker/prefect_data`: Mounted to `/data` in the Prefect container for Prefect data

## Using Docker for Development

### Running Tests in Docker

```bash
# Run all tests
docker-compose exec app python -m pytest

# Run specific tests
docker-compose exec app python -m pytest tests/test_filesystem
```

### Running the API in Docker

The API is automatically started in the application container. You can access it at http://localhost:8000.

### Accessing the iRODS Server

You can access the iRODS server using the icommands in the application container:

```bash
# List collections
docker-compose exec app ils

# Add metadata
docker-compose exec app imeta add -C /tempZone/home/rods/test key value

# Query metadata
docker-compose exec app imeta qu -C key = value
```

### Accessing the Prefect Server

You can access the Prefect server at http://localhost:4200.

## Docker for Production

For production use, you should:

1. Use a production-ready iRODS server
2. Use a production-ready Prefect server
3. Configure appropriate security settings
4. Use a reverse proxy for the API
5. Set up monitoring and logging

### Production Docker Compose Example

```yaml
version: '3'

services:
  app:
    build: .
    restart: always
    ports:
      - "8000:8000"
    environment:
      - IRODS_HOST=irods-server.example.com
      - IRODS_PORT=1247
      - IRODS_USER=rods
      - IRODS_PASSWORD=${IRODS_PASSWORD}
      - IRODS_ZONE=tempZone
      - IRODS_RESOURCE=demoResc
      - PREFECT_API_URL=http://prefect-server.example.com:4200/api
      - SEQUENCER_BASE_DIR=/data/sequencer
      - API_DEBUG=false
    volumes:
      - /path/to/sequencer/data:/data/sequencer
    networks:
      - app-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  app-network:
    driver: bridge
```

## Troubleshooting Docker

### Common Issues

#### Container Fails to Start

Check the container logs:

```bash
docker-compose logs app
```

#### iRODS Connection Issues

Check the iRODS server logs:

```bash
docker-compose logs irods-catalog
```

Verify the iRODS connection settings:

```bash
docker-compose exec app env | grep IRODS
```

#### Prefect Connection Issues

Check the Prefect server logs:

```bash
docker-compose logs prefect
```

Verify the Prefect connection settings:

```bash
docker-compose exec app env | grep PREFECT
```

### Resetting the Docker Environment

If you need to reset the Docker environment:

```bash
# Stop and remove all containers
docker-compose down

# Remove volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Start fresh
docker-compose up -d
```

## Docker Best Practices

- **Use specific versions**: Use specific versions for base images
- **Minimize image size**: Use multi-stage builds and remove unnecessary files
- **Use environment variables**: Use environment variables for configuration
- **Use health checks**: Add health checks to containers
- **Use non-root users**: Run containers as non-root users
- **Use volume mounts**: Use volume mounts for persistent data
- **Use networks**: Use Docker networks for container communication
- **Use logging**: Configure appropriate logging
- **Use monitoring**: Set up monitoring for containers
