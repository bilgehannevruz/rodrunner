"""
Metadata models for iRODS objects.
"""
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, validator


class MetadataItem(BaseModel):
    """Model for a single metadata item."""
    name: str = Field(..., description="Metadata attribute name")
    value: str = Field(..., description="Metadata attribute value")
    units: Optional[str] = Field(None, description="Metadata attribute units")


class MetadataQuery(BaseModel):
    """Model for metadata query parameters."""
    attributes: List[MetadataItem] = Field(
        ..., 
        description="List of metadata attributes to query for"
    )
    operator: str = Field(
        "AND", 
        description="Logical operator to use between attributes (AND/OR)"
    )
    
    @validator('operator')
    def validate_operator(cls, v):
        if v not in ["AND", "OR"]:
            raise ValueError("Operator must be either 'AND' or 'OR'")
        return v


class DataObjectMetadata(BaseModel):
    """Model for data object with metadata."""
    path: str = Field(..., description="Path to the data object")
    name: str = Field(..., description="Name of the data object")
    size: int = Field(..., description="Size of the data object in bytes")
    create_time: str = Field(..., description="Creation time")
    modify_time: str = Field(..., description="Last modification time")
    metadata: List[MetadataItem] = Field(
        default_factory=list,
        description="List of metadata items"
    )


class CollectionMetadata(BaseModel):
    """Model for collection with metadata."""
    path: str = Field(..., description="Path to the collection")
    name: str = Field(..., description="Name of the collection")
    create_time: str = Field(..., description="Creation time")
    modify_time: str = Field(..., description="Last modification time")
    metadata: List[MetadataItem] = Field(
        default_factory=list,
        description="List of metadata items"
    )


class SequencerRunMetadata(BaseModel):
    """Model for sequencer run metadata."""
    run_id: str = Field(..., description="Run ID")
    run_number: Optional[str] = Field(None, description="Run number")
    flowcell: str = Field(..., description="Flowcell ID")
    instrument: str = Field(..., description="Instrument ID")
    date: str = Field(..., description="Run date")
    sequencer_type: str = Field(..., description="Sequencer type")
    projects: List[str] = Field(
        default_factory=list,
        description="List of projects in the run"
    )
    status: str = Field("new", description="Run status")
    
    class Config:
        schema_extra = {
            "example": {
                "run_id": "220101_M00001_0001_000000000-A1B2C",
                "run_number": "0001",
                "flowcell": "000000000-A1B2C",
                "instrument": "M00001",
                "date": "220101",
                "sequencer_type": "miseq",
                "projects": ["Project1", "Project2"],
                "status": "new"
            }
        }
