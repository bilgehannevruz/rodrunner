"""
Response models for the API.
"""
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field

from irods_prefect.models.metadata import DataObjectMetadata, CollectionMetadata


class MetadataQueryResponse(BaseModel):
    """Response model for metadata queries."""
    total: int = Field(..., description="Total number of results")
    limit: int = Field(..., description="Maximum number of results returned")
    offset: int = Field(..., description="Number of results skipped")
    data_objects: Optional[List[DataObjectMetadata]] = Field(
        None, 
        description="List of data objects matching the query"
    )
    collections: Optional[List[CollectionMetadata]] = Field(
        None, 
        description="List of collections matching the query"
    )


class OperationResponse(BaseModel):
    """Response model for operations."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Message describing the result")
    data: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional data about the operation"
    )


class WorkflowRunResponse(BaseModel):
    """Response model for workflow runs."""
    success: bool = Field(..., description="Whether the workflow was started successfully")
    message: str = Field(..., description="Message describing the result")
    flow_run_id: Optional[str] = Field(
        None, 
        description="ID of the flow run"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Parameters used for the workflow"
    )
