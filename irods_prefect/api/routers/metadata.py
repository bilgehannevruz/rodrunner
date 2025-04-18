"""
Metadata query endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from irods_prefect.api.models.requests import MetadataQueryRequest
from irods_prefect.api.models.responses import MetadataQueryResponse, OperationResponse
from irods_prefect.irods.client import iRODSClient
from irods_prefect.irods.query import QueryOperations
from irods_prefect.api.dependencies import get_irods_client


router = APIRouter(
    prefix="/metadata",
    tags=["metadata"],
    responses={404: {"description": "Not found"}},
)


@router.post("/query", response_model=MetadataQueryResponse)
async def query_metadata(
    query: MetadataQueryRequest,
    irods_client: iRODSClient = Depends(get_irods_client)
):
    """
    Query iRODS objects based on metadata.
    
    This endpoint allows searching for data objects or collections
    that match specific metadata criteria.
    """
    try:
        # Create query operations
        query_ops = QueryOperations(irods_client)
        
        # Convert Pydantic model to query parameters
        metadata_items = [
            (item.name, item.value, item.units) 
            for item in query.metadata.attributes
        ]
        
        # Determine which query method to use based on object type
        if query.object_type == "data_object":
            results = query_ops.query_data_objects_by_metadata(
                metadata_items=metadata_items,
                operator=query.metadata.operator,
                limit=query.limit,
                offset=query.offset,
                sort_by=query.sort_by,
                sort_order=query.sort_order
            )
            
            # Convert results to Pydantic models
            data_objects = []
            for obj in results:
                metadata = [
                    {"name": meta.name, "value": meta.value, "units": meta.units}
                    for meta in obj.metadata.items()
                ]
                
                data_objects.append({
                    "path": obj.path,
                    "name": obj.name,
                    "size": obj.size,
                    "create_time": str(obj.create_time),
                    "modify_time": str(obj.modify_time),
                    "metadata": metadata
                })
                
            return {
                "total": len(data_objects),
                "limit": query.limit,
                "offset": query.offset,
                "data_objects": data_objects,
                "collections": None
            }
            
        else:  # collection
            results = query_ops.query_collections_by_metadata(
                metadata_items=metadata_items,
                operator=query.metadata.operator,
                limit=query.limit,
                offset=query.offset,
                sort_by=query.sort_by,
                sort_order=query.sort_order
            )
            
            # Convert results to Pydantic models
            collections = []
            for coll in results:
                metadata = [
                    {"name": meta.name, "value": meta.value, "units": meta.units}
                    for meta in coll.metadata.items()
                ]
                
                collections.append({
                    "path": coll.path,
                    "name": coll.name,
                    "create_time": str(coll.create_time),
                    "modify_time": str(coll.modify_time),
                    "metadata": metadata
                })
                
            return {
                "total": len(collections),
                "limit": query.limit,
                "offset": query.offset,
                "data_objects": None,
                "collections": collections
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error querying metadata: {str(e)}"
        )


@router.get("/sequencer-runs", response_model=MetadataQueryResponse)
async def get_sequencer_runs(
    sequencer_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    irods_client: iRODSClient = Depends(get_irods_client)
):
    """
    Get sequencer runs based on type and status.
    
    This endpoint allows searching for sequencer runs in iRODS
    based on sequencer type and status.
    """
    try:
        # Create query operations
        query_ops = QueryOperations(irods_client)
        
        # Build metadata query
        metadata_items = []
        
        if sequencer_type:
            metadata_items.append(("sequencer_type", sequencer_type, None))
        
        if status:
            metadata_items.append(("status", status, None))
        
        # Query collections
        results = query_ops.query_collections_by_metadata(
            metadata_items=metadata_items,
            limit=limit,
            offset=offset,
            sort_by="modify_time",
            sort_order="desc"
        )
        
        # Convert results to Pydantic models
        collections = []
        for coll in results:
            metadata = [
                {"name": meta.name, "value": meta.value, "units": meta.units}
                for meta in coll.metadata.items()
            ]
            
            collections.append({
                "path": coll.path,
                "name": coll.name,
                "create_time": str(coll.create_time),
                "modify_time": str(coll.modify_time),
                "metadata": metadata
            })
            
        return {
            "total": len(collections),
            "limit": limit,
            "offset": offset,
            "data_objects": None,
            "collections": collections
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error querying sequencer runs: {str(e)}"
        )
