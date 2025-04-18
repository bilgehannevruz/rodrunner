# Rodrunner

Welcome to the documentation for the Rodrunner project. This project provides a comprehensive solution for managing sequencer data using iRODS and Prefect v3.

## Project Overview

The Rodrunner project is designed to automate the ingestion, metadata extraction, and management of sequencing data from various sequencer types (MiSeq, NextSeq, NovaSeq, PacBio, Nanopore, NovaSeqXPlus) into an iRODS data management system. It uses Prefect v3 for workflow orchestration and provides a FastAPI-based REST API for interacting with the workflows and querying metadata.

### Key Features

- **Filesystem Operations**: Generator-based file finding utilities similar to the Unix find command
- **iRODS Client**: A comprehensive wrapper for the python-irodsclient library
- **Metadata Parsers**: Parsers for extracting metadata from sequencer-specific files (RunInfo.xml, RunParameters.xml, SampleSheet.csv)
- **Prefect Workflows**: Workflows for data ingestion and metadata management
- **FastAPI REST API**: API for querying metadata and triggering workflows
- **Docker Integration**: Docker-based deployment for easy setup and testing

## Quick Links

- [Installation](getting-started/installation.md): How to install the project
- [Configuration](getting-started/configuration.md): How to configure the project
- [Quickstart](getting-started/quickstart.md): Get up and running quickly
- [User Guide](user-guide/overview.md): Detailed user guide
- [API Reference](api-reference/filesystem.md): API documentation
- [Development](development/contributing.md): Development guidelines

## Project Structure

```
rodrunner/
├── api/                  # FastAPI application
│   ├── models/           # Pydantic models for API
│   └── routers/          # API route definitions
├── filesystem/           # Filesystem operations
├── irods/                # iRODS client wrapper
├── models/               # Data models
├── parsers/              # Metadata parsers
├── sequencers/           # Sequencer-specific workflows
├── tasks/                # Common Prefect tasks
└── workflows/            # Prefect workflows
```

## License

This project is licensed under the MIT License - see the [License](about/license.md) file for details.
