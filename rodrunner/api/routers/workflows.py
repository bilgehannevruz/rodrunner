"""
Workflow management endpoints.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from fastapi.responses import JSONResponse

# Prefect v3 imports
from prefect.client.orchestration import get_client
from prefect.deployments import run_deployment
from prefect.client.schemas.filters import FlowRunFilter, DeploymentFilter
from prefect.client.schemas.objects import FlowRun, Deployment
from prefect.client.schemas.sorting import FlowRunSort
from prefect.client.schemas.states import StateType

from rodrunner.api.models.requests import WorkflowRunRequest, RunStatusUpdateRequest
from rodrunner.api.models.responses import WorkflowRunResponse, OperationResponse
from rodrunner.models.config import AppConfig, PrefectConfig
from rodrunner.api.dependencies import get_app_config, get_prefect_config
from rodrunner.irods.client import iRODSClient
from rodrunner.api.dependencies import get_irods_client


router = APIRouter(
    prefix="/workflows",
    tags=["workflows"],
    responses={404: {"description": "Not found"}},
)


@router.post("/run", response_model=WorkflowRunResponse)
async def run_workflow(
    request: WorkflowRunRequest,
    prefect_config: PrefectConfig = Depends(get_prefect_config)
):
    """
    Run a workflow.

    This endpoint allows running a workflow with the specified parameters.
    """
    try:
        # Get deployment from config
        if request.workflow_name not in prefect_config.deployments:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown workflow: {request.workflow_name}. Available workflows: {list(prefect_config.deployments.keys())}"
            )

        deployment_path = prefect_config.deployments[request.workflow_name]

        # Run the workflow
        async with get_client() as client:
            flow_run = await run_deployment(
                deployment=deployment_path,
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
    prefect_config: PrefectConfig = Depends(get_prefect_config),
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


@router.get("/deployments", response_model=List[Dict[str, Any]])
async def get_deployments(
    name: Optional[str] = None,
    flow_name: Optional[str] = None,
    limit: int = 100,
    prefect_config: PrefectConfig = Depends(get_prefect_config)
):
    """
    Get available workflow deployments.

    This endpoint returns a list of available workflow deployments.
    """
    try:
        async with get_client() as client:
            # Build filter
            filters = []
            if name:
                filters.append(DeploymentFilter.NAME.contains(name))
            if flow_name:
                filters.append(DeploymentFilter.FLOW_NAME.contains(flow_name))

            # Get deployments
            deployments = await client.read_deployments(
                limit=limit,
                filters=filters if filters else None
            )

            # Format response
            result = []
            for deployment in deployments:
                result.append({
                    "id": deployment.id,
                    "name": deployment.name,
                    "flow_name": deployment.flow_name,
                    "description": deployment.description,
                    "version": deployment.version,
                    "created": deployment.created,
                    "updated": deployment.updated,
                    "parameters": deployment.parameters,
                    "tags": deployment.tags,
                    "path": f"{deployment.flow_name}/{deployment.name}"
                })

            return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting deployments: {str(e)}"
        )


@router.get("/runs", response_model=List[Dict[str, Any]])
async def get_flow_runs(
    deployment_id: Optional[str] = None,
    flow_name: Optional[str] = None,
    state_type: Optional[str] = None,
    limit: int = 100,
    prefect_config: PrefectConfig = Depends(get_prefect_config)
):
    """
    Get flow runs.

    This endpoint returns a list of flow runs.
    """
    try:
        async with get_client() as client:
            # Build filter
            filters = []
            if deployment_id:
                filters.append(FlowRunFilter.DEPLOYMENT_ID == deployment_id)
            if flow_name:
                filters.append(FlowRunFilter.FLOW_NAME.contains(flow_name))
            if state_type:
                filters.append(FlowRunFilter.STATE_TYPE == state_type)

            # Get flow runs
            flow_runs = await client.read_flow_runs(
                limit=limit,
                filters=filters if filters else None,
                sort=FlowRunSort.EXPECTED_START_TIME_DESC
            )

            # Format response
            result = []
            for flow_run in flow_runs:
                result.append({
                    "id": flow_run.id,
                    "name": flow_run.name,
                    "flow_name": flow_run.flow_name,
                    "deployment_id": flow_run.deployment_id,
                    "state_type": flow_run.state_type,
                    "state_name": flow_run.state_name,
                    "state_message": flow_run.state_message,
                    "created": flow_run.created,
                    "start_time": flow_run.start_time,
                    "end_time": flow_run.end_time,
                    "parameters": flow_run.parameters
                })

            return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting flow runs: {str(e)}"
        )


@router.get("/runs/{flow_run_id}", response_model=Dict[str, Any])
async def get_flow_run(
    flow_run_id: str = Path(..., description="Flow run ID"),
    prefect_config: PrefectConfig = Depends(get_prefect_config)
):
    """
    Get a specific flow run.

    This endpoint returns details about a specific flow run.
    """
    try:
        async with get_client() as client:
            # Get flow run
            flow_run = await client.read_flow_run(flow_run_id)

            # Format response
            result = {
                "id": flow_run.id,
                "name": flow_run.name,
                "flow_name": flow_run.flow_name,
                "deployment_id": flow_run.deployment_id,
                "state_type": flow_run.state_type,
                "state_name": flow_run.state_name,
                "state_message": flow_run.state_message,
                "created": flow_run.created,
                "start_time": flow_run.start_time,
                "end_time": flow_run.end_time,
                "parameters": flow_run.parameters
            }

            # Get logs
            logs = await client.read_logs(flow_run_id=flow_run_id, limit=100)
            result["logs"] = [{
                "level": log.level,
                "message": log.message,
                "timestamp": log.timestamp
            } for log in logs]

            return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting flow run: {str(e)}"
        )
