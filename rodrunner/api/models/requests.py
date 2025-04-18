"""
Request models for the API.
"""
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, validator
from enum import Enum

from rodrunner.models.metadata import MetadataQuery, MetadataItem


class ObjectType(str, Enum):
    """Enum for iRODS object types."""
    DATA_OBJECT = "data_object"
    COLLECTION = "collection"


class MetadataQueryRequest(BaseModel):
    """Request model for metadata queries."""
    object_type: ObjectType = Field(
        ..., 
        description="Type of iRODS object to query"
    )
    metadata: MetadataQuery = Field(
        ..., 
        description="Metadata query parameters"
    )
    limit: Optional[int] = Field(
        100, 
        description="Maximum number of results to return"
    )
    offset: Optional[int] = Field(
        0, 
        description="Number of results to skip"
    )
    sort_by: Optional[str] = Field(
        None, 
        description="Field to sort results by"
    )
    sort_order: Optional[str] = Field(
        "asc", 
        description="Sort order (asc/desc)"
    )
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v not in ["asc", "desc"]:
            raise ValueError("Sort order must be either 'asc' or 'desc'")
        return v


class DataObjectUploadRequest(BaseModel):
    """Request model for data object upload."""
    destination_path: str = Field(
        ..., 
        description="Destination path in iRODS"
    )
    metadata: Optional[List[MetadataItem]] = Field(
        None, 
        description="Metadata to attach to the data object"
    )
    resource: Optional[str] = Field(
        None, 
        description="Resource to use for upload"
    )
    force: Optional[bool] = Field(
        False, 
        description="Whether to overwrite existing data object"
    )


class RunStatusUpdateRequest(BaseModel):
    """Request model for run status update."""
    status: str = Field(
        ..., 
        description="New status"
    )
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ["new", "processing", "processed", "error", "complete"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v


class WorkflowRunRequest(BaseModel):
    """Request model for running a workflow."""
    workflow_name: str = Field(
        ..., 
        description="Name of the workflow to run"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Parameters for the workflow"
    )
