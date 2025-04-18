# MiSeq Sequencer

This page contains information about handling MiSeq sequencer data.

## MiSeq Run Structure

MiSeq runs typically have the following directory structure:

```
220101_M00001_0001_000000000-A1B2C/
├── Data/
├── InterOp/
├── Logs/
├── Recipe/
├── RTAComplete.txt
├── RunInfo.xml
├── RunParameters.xml
└── SampleSheet.csv
```

## Required Files

The following files are required for processing MiSeq runs:

- `RunInfo.xml`: Contains information about the run, including the run ID, instrument, flowcell, and read configuration.
- `RunParameters.xml`: Contains parameters used for the run, including chemistry, application version, and experiment name.
- `SampleSheet.csv`: Contains information about the samples in the run, including sample IDs, indices, and projects.
- `RTAComplete.txt`: Indicates that the run has completed.

## Metadata Extraction

The following metadata is extracted from MiSeq runs:

- Run ID
- Instrument ID
- Flowcell ID
- Date
- Chemistry
- Application version
- Sample count
- Read configuration

## Workflow

The MiSeq ingest workflow performs the following steps:

1. Find completed MiSeq runs
2. Validate the run structure
3. Extract metadata from the run files
4. Upload the run to iRODS
5. Add metadata to the iRODS collection

For more information, see the [Workflows](../user-guide/workflows.md) section.
