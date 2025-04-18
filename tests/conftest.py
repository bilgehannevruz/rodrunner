"""
Common test fixtures for the rodrunner package.
"""
import os
import tempfile
import shutil
from typing import Dict, Generator, Any

import pytest
from fastapi.testclient import TestClient

from rodrunner.models.config import AppConfig
from rodrunner.config import get_config
from rodrunner.irods.client import iRODSClient
from rodrunner.api.main import create_app


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def app_config() -> AppConfig:
    """Get the application configuration from environment variables or config file."""
    return get_config()


@pytest.fixture
def irods_client(app_config: AppConfig) -> iRODSClient:
    """Create an iRODS client using the application configuration."""
    return iRODSClient(app_config.irods)


@pytest.fixture
def api_client(app_config: AppConfig) -> TestClient:
    """Create a test client for the FastAPI application."""
    app = create_app(app_config)
    return TestClient(app)


@pytest.fixture
def sample_run_info_xml() -> str:
    """Sample RunInfo.xml content for testing."""
    return """<?xml version="1.0"?>
<RunInfo Version="2">
  <Run Id="220101_M00001_0001_000000000-A1B2C" Number="1">
    <Flowcell>000000000-A1B2C</Flowcell>
    <Instrument>M00001</Instrument>
    <Date>1/1/2022</Date>
    <Reads>
      <Read Number="1" NumCycles="151" IsIndexedRead="N" />
      <Read Number="2" NumCycles="8" IsIndexedRead="Y" />
      <Read Number="3" NumCycles="8" IsIndexedRead="Y" />
      <Read Number="4" NumCycles="151" IsIndexedRead="N" />
    </Reads>
    <FlowcellLayout LaneCount="1" SurfaceCount="2" SwathCount="1" TileCount="14" />
  </Run>
</RunInfo>
"""


@pytest.fixture
def sample_run_parameters_xml() -> str:
    """Sample RunParameters.xml content for testing."""
    return """<?xml version="1.0"?>
<RunParameters>
  <RunParametersVersion>MiSeq_1_0</RunParametersVersion>
  <Setup>
    <ApplicationName>MiSeq Control Software</ApplicationName>
    <ApplicationVersion>4.0.0.1769</ApplicationVersion>
    <ExperimentName>Test Run</ExperimentName>
  </Setup>
  <RunID>220101_M00001_0001_000000000-A1B2C</RunID>
  <ScannerID>M00001</ScannerID>
  <RTAVersion>2.4.0.3</RTAVersion>
  <Chemistry>Amplicon</Chemistry>
</RunParameters>
"""


@pytest.fixture
def sample_samplesheet_csv() -> str:
    """Sample SampleSheet.csv content for testing."""
    return """[Header]
IEMFileVersion,5
Date,1/1/2022
Workflow,GenerateFASTQ
Application,FASTQ Only
Instrument Type,MiSeq
Assay,Nextera XT
Index Adapters,Nextera XT Index Kit (96 Indexes, 384 Samples)
Chemistry,Amplicon

[Reads]
151
151

[Settings]
ReverseComplement,0
Adapter,CTGTCTCTTATACACATCT

[Data]
Sample_ID,Sample_Name,Sample_Plate,Sample_Well,Index_Plate_Well,I7_Index_ID,index,I5_Index_ID,index2,Sample_Project,Description
Sample1,Sample1,Plate1,A01,A01,N701,TAAGGCGA,S501,TAGATCGC,Project1,Description1
Sample2,Sample2,Plate1,A02,A02,N702,CGTACTAG,S502,CTCTCTAT,Project1,Description2
"""


@pytest.fixture
def sample_sequencer_run(temp_dir: str, sample_run_info_xml: str,
                        sample_run_parameters_xml: str, sample_samplesheet_csv: str) -> str:
    """Create a sample sequencer run directory for testing."""
    run_dir = os.path.join(temp_dir, "220101_M00001_0001_000000000-A1B2C")
    os.makedirs(run_dir)

    # Create required files
    with open(os.path.join(run_dir, "RunInfo.xml"), "w") as f:
        f.write(sample_run_info_xml)

    with open(os.path.join(run_dir, "RunParameters.xml"), "w") as f:
        f.write(sample_run_parameters_xml)

    with open(os.path.join(run_dir, "SampleSheet.csv"), "w") as f:
        f.write(sample_samplesheet_csv)

    with open(os.path.join(run_dir, "RTAComplete.txt"), "w") as f:
        f.write("RTA Complete")

    return run_dir
