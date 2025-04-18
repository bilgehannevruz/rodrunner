"""
Models for iRODS objects.
"""
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, validator

from rodrunner.models.metadata import MetadataItem


class DataObject(BaseModel):
    """Model for an iRODS data object."""
    path: str = Field(..., description="Path to the data object")
    name: str = Field(..., description="Name of the data object")
    size: int = Field(..., description="Size of the data object in bytes")
    checksum: Optional[str] = Field(None, description="Checksum of the data object")
    create_time: str = Field(..., description="Creation time")
    modify_time: str = Field(..., description="Last modification time")
    metadata: List[MetadataItem] = Field(
        default_factory=list,
        description="List of metadata items"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "path": "/tempZone/home/rods/data/file.txt",
                "name": "file.txt",
                "size": 1024,
                "checksum": "sha2:12345",
                "create_time": "2022-01-01T00:00:00Z",
                "modify_time": "2022-01-01T00:00:00Z",
                "metadata": [
                    {
                        "name": "key1",
                        "value": "value1",
                        "units": None
                    }
                ]
            }
        }


class Collection(BaseModel):
    """Model for an iRODS collection."""
    path: str = Field(..., description="Path to the collection")
    name: str = Field(..., description="Name of the collection")
    create_time: str = Field(..., description="Creation time")
    modify_time: str = Field(..., description="Last modification time")
    metadata: List[MetadataItem] = Field(
        default_factory=list,
        description="List of metadata items"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "path": "/tempZone/home/rods/data",
                "name": "data",
                "create_time": "2022-01-01T00:00:00Z",
                "modify_time": "2022-01-01T00:00:00Z",
                "metadata": [
                    {
                        "name": "key1",
                        "value": "value1",
                        "units": None
                    }
                ]
            }
        }


class Resource(BaseModel):
    """Model for an iRODS resource."""
    name: str = Field(..., description="Name of the resource")
    type: str = Field(..., description="Type of the resource")
    host: str = Field(..., description="Host of the resource")
    path: str = Field(..., description="Path of the resource")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "demoResc",
                "type": "unixfilesystem",
                "host": "localhost",
                "path": "/var/lib/irods/Vault"
            }
        }


class User(BaseModel):
    """Model for an iRODS user."""
    name: str = Field(..., description="Name of the user")
    zone: str = Field(..., description="Zone of the user")
    type: str = Field(..., description="Type of the user")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "rods",
                "zone": "tempZone",
                "type": "rodsadmin"
            }
        }
