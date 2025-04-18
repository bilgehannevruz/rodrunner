# Other Sequencers

This page contains information about handling data from other sequencer types.

## Supported Sequencer Types

In addition to MiSeq and NovaSeq, the following sequencer types are supported:

- **PacBio**: Pacific Biosciences sequencers
- **Nanopore**: Oxford Nanopore sequencers
- **NovaSeqXPlus**: Illumina NovaSeq X Plus sequencers

## PacBio Sequencers

### PacBio Run Structure

PacBio runs typically have the following directory structure:

```
r54228_20220103_123456/
├── metadata.xml
├── sts.xml
└── [other files]
```

### Required Files

The following files are required for processing PacBio runs:

- `metadata.xml`: Contains information about the run, including the run ID, instrument, and sample information.
- `sts.xml`: Contains status information about the run.

## Nanopore Sequencers

### Nanopore Run Structure

Nanopore runs typically have the following directory structure:

```
20220104_1234_X1_FAO12345_a1b2c3d4/
├── final_summary.txt
├── sequencing_summary.txt
└── [other files]
```

### Required Files

The following files are required for processing Nanopore runs:

- `final_summary.txt`: Contains summary information about the run.
- `sequencing_summary.txt`: Contains detailed information about the sequencing.

## NovaSeqXPlus Sequencers

### NovaSeqXPlus Run Structure

NovaSeqXPlus runs typically have the following directory structure:

```
20220105_LH00001_0001_A123456789/
├── Data/
├── InterOp/
├── Logs/
├── Recipe/
├── RTAComplete.txt
├── RunInfo.xml
├── RunParameters.xml
└── SampleSheet.csv
```

### Required Files

The following files are required for processing NovaSeqXPlus runs:

- `RunInfo.xml`: Contains information about the run, including the run ID, instrument, flowcell, and read configuration.
- `RunParameters.xml`: Contains parameters used for the run, including chemistry, application version, and experiment name.
- `SampleSheet.csv`: Contains information about the samples in the run, including sample IDs, indices, and projects.
- `RTAComplete.txt`: Indicates that the run has completed.

## Adding Support for New Sequencer Types

To add support for a new sequencer type:

1. Create a new module in the `rodrunner/sequencers` directory
2. Implement the required functions for finding and validating runs
3. Implement the required functions for extracting metadata
4. Update the configuration to include the new sequencer type
5. Update the workflows to handle the new sequencer type

For more information, see the [Development](../development/contributing.md) section.
