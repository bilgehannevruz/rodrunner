# User Guide Overview

This user guide provides detailed information about the Rodrunner project and how to use it effectively.

## Project Components

The project consists of several key components:

### Filesystem Module

The filesystem module provides generator-based file finding utilities similar to the Unix find command. It allows you to search for files with various filters, including depth, name patterns, and custom filters.

[Learn more about the Filesystem Module](filesystem.md)

### iRODS Client

The iRODS client is a comprehensive wrapper for the python-irodsclient library. It provides a simplified interface for common iRODS operations, including collection and data object management, metadata operations, and more.

[Learn more about the iRODS Client](irods-client.md)

### Parsers

The parsers module provides parsers for extracting metadata from sequencer-specific files, including RunInfo.xml, RunParameters.xml, and SampleSheet.csv. It supports various sequencer types and file formats.

[Learn more about the Parsers](parsers.md)

### Workflows

The workflows module provides Prefect v3 workflows for data ingestion and metadata management. It includes workflows for ingesting sequencer data, updating metadata, and more.

[Learn more about the Workflows](workflows.md)

### API

The API module provides a FastAPI-based REST API for interacting with the workflows and querying metadata. It includes endpoints for running workflows, checking workflow status, and querying metadata.

[Learn more about the API](api.md)

## Workflow Overview

The typical workflow for using the project is:

1. **Configure the project** for your environment
2. **Ingest sequencer data** into iRODS using the ingest workflows
3. **Extract and update metadata** using the metadata workflows
4. **Query metadata** using the API

## Use Cases

### Sequencer Data Management

The primary use case for the project is managing sequencer data from various sequencer types (MiSeq, NextSeq, NovaSeq, PacBio, Nanopore, NovaSeqXPlus). The project provides workflows for ingesting data, extracting metadata, and managing the data in iRODS.

### Metadata Management

The project provides tools for extracting, updating, and querying metadata from sequencer data. This includes metadata from RunInfo.xml, RunParameters.xml, and SampleSheet.csv files.

### Workflow Automation

The project uses Prefect v3 for workflow orchestration, allowing you to automate common tasks and create complex workflows. You can schedule workflows, monitor their status, and receive notifications when they complete or fail.

### API Integration

The project provides a REST API for interacting with the workflows and querying metadata. This allows you to integrate the project with other systems and build custom applications on top of it.

## Next Steps

- [Learn about the Filesystem Module](filesystem.md)
- [Learn about the iRODS Client](irods-client.md)
- [Learn about the Parsers](parsers.md)
- [Learn about the Workflows](workflows.md)
- [Learn about the API](api.md)
