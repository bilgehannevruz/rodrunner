"""
Tests for the workflow API routes.
"""
import os
import pytest
from typing import Dict, Any
import json

from fastapi.testclient import TestClient
from rodrunner.models.config import AppConfig
from rodrunner.irods.client import iRODSClient


@pytest.mark.api
def test_list_workflows(api_client: TestClient) -> None:
    """Test listing available workflows."""
    response = api_client.get("/workflows/list")
    assert response.status_code == 200
    data = response.json()
    
    # Check that the response contains the expected workflows
    workflow_names = [w["name"] for w in data]
    assert "Ingest Sequencer Runs" in workflow_names
    assert "Ingest All Sequencer Runs" in workflow_names
    assert "Update Run Metadata" in workflow_names


@pytest.mark.api
def test_run_ingest_workflow(api_client: TestClient, sample_sequencer_run: str, temp_dir: str) -> None:
    """Test running the ingest workflow via API."""
    # Set up a test directory with a sequencer run
    sequencer_dir = os.path.join(temp_dir, "sequencer_api_test")
    miseq_dir = os.path.join(sequencer_dir, "miseq")
    os.makedirs(miseq_dir)
    
    # Copy the sample run to the miseq directory
    run_name = os.path.basename(sample_sequencer_run)
    os.system(f"cp -r {sample_sequencer_run} {miseq_dir}/{run_name}")
    
    # Test running the workflow
    workflow_data = {
        "workflow_name": "Ingest Sequencer Runs",
        "parameters": {
            "sequencer_type": "miseq",
            "root_dir": miseq_dir
        }
    }
    
    response = api_client.post("/workflows/run", json=workflow_data)
    assert response.status_code == 202  # Accepted, workflow started
    data = response.json()
    
    assert "flow_run_id" in data
    assert "status" in data
    assert data["status"] == "RUNNING" or data["status"] == "PENDING"
    
    # Test with invalid workflow name
    workflow_data["workflow_name"] = "Non-existent Workflow"
    response = api_client.post("/workflows/run", json=workflow_data)
    assert response.status_code == 404


@pytest.mark.api
def test_get_workflow_status(api_client: TestClient) -> None:
    """Test getting workflow status."""
    # First, run a workflow to get a flow_run_id
    workflow_data = {
        "workflow_name": "Ingest All Sequencer Runs",
        "parameters": {}
    }
    
    run_response = api_client.post("/workflows/run", json=workflow_data)
    assert run_response.status_code == 202
    run_data = run_response.json()
    flow_run_id = run_data["flow_run_id"]
    
    # Now get the status
    response = api_client.get(f"/workflows/status/{flow_run_id}")
    assert response.status_code == 200
    data = response.json()
    
    assert "flow_run_id" in data
    assert data["flow_run_id"] == flow_run_id
    assert "status" in data
    assert "start_time" in data
    
    # Test with invalid flow_run_id
    response = api_client.get("/workflows/status/invalid-id")
    assert response.status_code == 404
