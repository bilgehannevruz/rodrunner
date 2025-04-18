"""
Simplified API for testing without Prefect.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

app = FastAPI(
    title="iRODS Prefect API",
    description="API for Rodrunner",
    version="0.1.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class WorkflowRunRequest(BaseModel):
    workflow_name: str
    parameters: Dict[str, Any]

class WorkflowRunResponse(BaseModel):
    success: bool
    message: str
    flow_run_id: str
    parameters: Dict[str, Any]

class RunStatusUpdateRequest(BaseModel):
    status: str

class OperationResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class MetadataQuery(BaseModel):
    key: str
    value: str
    operator: str = "="

class MetadataSearchRequest(BaseModel):
    queries: List[MetadataQuery]
    collection_path: Optional[str] = None
    recursive: bool = True
    limit: int = 100
    offset: int = 0

class MetadataSearchResponse(BaseModel):
    success: bool
    message: str
    total: int
    items: List[Dict[str, Any]]

# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to iRODS Prefect API"}

@app.post("/workflows/run", response_model=WorkflowRunResponse)
async def run_workflow(request: WorkflowRunRequest):
    """
    Simulate running a workflow.
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
        
        # Simulate running the workflow
        return {
            "success": True,
            "message": f"Workflow {request.workflow_name} started successfully (simulation)",
            "flow_run_id": "simulated-flow-run-id",
            "parameters": request.parameters
        }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error running workflow: {str(e)}"
        )

@app.post("/workflows/runs/{collection_path}/status", response_model=OperationResponse)
async def update_run_status(collection_path: str, request: RunStatusUpdateRequest):
    """
    Simulate updating the status of a sequencer run.
    """
    try:
        # Simulate updating the status
        return {
            "success": True,
            "message": f"Status updated to {request.status} (simulation)",
            "data": {
                "collection_path": collection_path,
                "status": request.status,
                "flow_run_id": "simulated-flow-run-id"
            }
        }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating run status: {str(e)}"
        )

@app.post("/metadata/search", response_model=MetadataSearchResponse)
async def search_metadata(request: MetadataSearchRequest):
    """
    Simulate searching for metadata.
    """
    try:
        # Simulate searching for metadata
        return {
            "success": True,
            "message": "Metadata search completed successfully (simulation)",
            "total": 1,
            "items": [
                {
                    "path": "/tempZone/home/rods/sequencer/miseq/run123",
                    "type": "collection",
                    "metadata": [
                        {"key": "instrument_id", "value": "M00123", "units": ""},
                        {"key": "run_id", "value": "123456", "units": ""},
                        {"key": "status", "value": "complete", "units": ""}
                    ]
                }
            ]
        }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching metadata: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
