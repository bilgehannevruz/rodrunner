"""
Metadata query endpoints.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from rodrunner.api.models.requests import MetadataQueryRequest
from rodrunner.api.models.responses import MetadataQueryResponse, OperationResponse
from rodrunner.irods.client import iRODSClient
from rodrunner.irods.query import QueryOperations
from rodrunner.api.dependencies import get_irods_client


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
    instrument_id: Optional[str] = None,
    run_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    irods_client: iRODSClient = Depends(get_irods_client)
):
    """
    Get sequencer runs based on various criteria.

    This endpoint allows searching for sequencer runs in iRODS
    based on sequencer type, status, instrument ID, run ID, and date range.
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

        if instrument_id:
            metadata_items.append(("instrument_id", instrument_id, None))

        if run_id:
            metadata_items.append(("run_id", run_id, None))

        # Query collections
        results = query_ops.query_collections_by_metadata(
            metadata_items=metadata_items,
            limit=limit,
            offset=offset,
            sort_by="modify_time",
            sort_order="desc"
        )

        # Filter by date range if specified
        filtered_results = []
        for coll in results:
            # Get date metadata
            date_value = None
            for meta in coll.metadata.items():
                if meta.name == "date":
                    date_value = meta.value
                    break

            # Skip if no date metadata and date filtering is requested
            if (date_from or date_to) and not date_value:
                continue

            # Apply date filtering if requested
            if date_value:
                include = True
                if date_from and date_value < date_from:
                    include = False
                if date_to and date_value > date_to:
                    include = False

                if not include:
                    continue

            filtered_results.append(coll)

        # Convert results to Pydantic models
        collections = []
        for coll in filtered_results:
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


@router.get("/sequencer-runs/summary", response_model=Dict[str, Any])
async def get_sequencer_runs_summary(
    irods_client: iRODSClient = Depends(get_irods_client)
):
    """
    Get a summary of sequencer runs.

    This endpoint returns a summary of sequencer runs in iRODS,
    including counts by sequencer type, status, and date.
    """
    try:
        # Create query operations
        query_ops = QueryOperations(irods_client)

        # Query all sequencer runs
        results = query_ops.query_collections_by_metadata(
            metadata_items=[("sequencer_type", None, None)],
            limit=1000,
            operator="like"
        )

        # Initialize summary
        summary = {
            "total": len(results),
            "by_sequencer_type": {},
            "by_status": {},
            "by_month": {},
            "recent_runs": []
        }

        # Process results
        for coll in results:
            # Extract metadata
            sequencer_type = None
            status = None
            date = None
            run_id = None
            instrument_id = None

            for meta in coll.metadata.items():
                if meta.name == "sequencer_type":
                    sequencer_type = meta.value
                elif meta.name == "status":
                    status = meta.value
                elif meta.name == "date":
                    date = meta.value
                elif meta.name == "run_id":
                    run_id = meta.value
                elif meta.name == "instrument_id":
                    instrument_id = meta.value

            # Count by sequencer type
            if sequencer_type:
                if sequencer_type not in summary["by_sequencer_type"]:
                    summary["by_sequencer_type"][sequencer_type] = 0
                summary["by_sequencer_type"][sequencer_type] += 1

            # Count by status
            if status:
                if status not in summary["by_status"]:
                    summary["by_status"][status] = 0
                summary["by_status"][status] += 1

            # Count by month
            if date:
                try:
                    # Try to parse date in various formats
                    parsed_date = None
                    for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]:
                        try:
                            parsed_date = datetime.strptime(date, fmt)
                            break
                        except ValueError:
                            continue

                    if parsed_date:
                        month_key = parsed_date.strftime("%Y-%m")
                        if month_key not in summary["by_month"]:
                            summary["by_month"][month_key] = 0
                        summary["by_month"][month_key] += 1
                except Exception:
                    # Skip if date parsing fails
                    pass

            # Add to recent runs
            if len(summary["recent_runs"]) < 10:
                summary["recent_runs"].append({
                    "path": coll.path,
                    "name": coll.name,
                    "sequencer_type": sequencer_type,
                    "status": status,
                    "date": date,
                    "run_id": run_id,
                    "instrument_id": instrument_id
                })

        # Sort recent runs by date (if available)
        summary["recent_runs"] = sorted(
            summary["recent_runs"],
            key=lambda x: x.get("date", ""),
            reverse=True
        )

        return summary

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting sequencer runs summary: {str(e)}"
        )
