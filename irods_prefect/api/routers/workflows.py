"""
Workflow management endpoints.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

# Prefect v3 imports
from prefect.client.orchestration import get_client
from prefect.deployments import run_deployment

from irods_prefect.api.models.requests import WorkflowRunRequest, RunStatusUpdateRequest
from irods_prefect.api.models.responses import WorkflowRunResponse, OperationResponse
from irods_prefect.models.config import AppConfig
from irods_prefect.api.dependencies import get_app_config
from irods_prefect.irods.client import iRODSClient
from irods_prefect.api.dependencies import get_irods_client


router = APIRouter(
    prefix="/workflows",
    tags=["workflows"],
    responses={404: {"description": "Not found"}},
)


@router.post("/run", response_model=WorkflowRunResponse)
async def run_workflow(
    request: WorkflowRunRequest,
    config: AppConfig = Depends(get_app_config)
):
    """
    Run a workflow.

    This endpoint allows running a workflow with the specified parameters.
    """
    try:
        # Map workflow name to deployment
        workflow_deployments = {
            "ingest_sequencer_runs": "ingest-sequencer-runs/production",
            "ingest_all_sequencer_runs": "ingest-all-sequencer-runs/production",
            "process_new_runs": "process-new-runs/production",
            "update_run_status": "update-run-status/production"
        }

        if request.workflow_name not in workflow_deployments:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown workflow: {request.workflow_name}"
            )

        deployment = workflow_deployments[request.workflow_name]

        # Run the deployment
        async with get_client() as client:
            flow_run = await run_deployment(
                deployment=deployment,
                parameters=request.parameters,
                client=client
            )

            return {
                "success": True,
                "message": f"Workflow {request.workflow_name} started successfully",
                "flow_run_id": flow_run.id,
                "parameters": request.parameters
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error running workflow: {str(e)}"
        )


@router.post("/runs/{collection_path}/status", response_model=OperationResponse)
async def update_run_status(
    collection_path: str,
    request: RunStatusUpdateRequest,
    config: AppConfig = Depends(get_app_config),
    irods_client: iRODSClient = Depends(get_irods_client)
):
    """
    Update the status of a sequencer run.

    This endpoint allows updating the status of a sequencer run in iRODS.
    """
    try:
        # Check if collection exists
        if not irods_client.collection_exists(collection_path):
            raise HTTPException(
                status_code=404,
                detail=f"Collection not found: {collection_path}"
            )

        # Run the workflow to update status
        async with get_client() as client:
            flow_run = await run_deployment(
                deployment="update-run-status/production",
                parameters={
                    "collection_path": collection_path,
                    "status": request.status
                },
                client=client
            )

            return {
                "success": True,
                "message": f"Status updated to {request.status}",
                "data": {
                    "collection_path": collection_path,
                    "status": request.status,
                    "flow_run_id": flow_run.id
                }
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating run status: {str(e)}"
        )
