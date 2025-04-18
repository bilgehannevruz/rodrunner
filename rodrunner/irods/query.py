"""
Advanced query operations for iRODS.
"""
from typing import Dict, List, Optional, Union, Any, Tuple, Generator
from irods.session import iRODSSession
from irods.models import Collection, DataObject, CollectionMeta, DataObjectMeta
from irods.column import Criterion
from irods.meta import iRODSMeta

from rodrunner.irods.client import iRODSClient


class QueryOperations:
    """Class for iRODS query operations."""
    
    def __init__(self, client: iRODSClient):
        """
        Initialize the query operations.
        
        Args:
            client: iRODS client
        """
        self.client = client
    
    def query_data_objects_by_metadata(
        self,
        metadata_items: List[Tuple[str, str, Optional[str]]],
        operator: str = "AND",
        limit: int = 100,
        offset: int = 0,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> List[Any]:
        """
        Query data objects by metadata.
        
        Args:
            metadata_items: List of (name, value, units) tuples
            operator: Logical operator to use between items ("AND" or "OR")
            limit: Maximum number of results to return
            offset: Number of results to skip
            sort_by: Field to sort results by
            sort_order: Sort order ("asc" or "desc")
            
        Returns:
            List of data objects matching the query
        """
        with self.client.session() as session:
            # Build query
            query = session.query(DataObject)
            
            # Add metadata conditions
            for i, (name, value, units) in enumerate(metadata_items):
                alias = f"meta{i}"
                query = query.filter(
                    Criterion('=', DataObjectMeta.name, name, alias),
                    Criterion('=', DataObjectMeta.value, value, alias)
                )
                if units:
                    query = query.filter(
                        Criterion('=', DataObjectMeta.units, units, alias)
                    )
            
            # Apply sorting
            if sort_by:
                if sort_by == "name":
                    if sort_order == "asc":
                        query = query.order_by(DataObject.name)
                    else:
                        query = query.order_by(DataObject.name, order="desc")
                elif sort_by == "size":
                    if sort_order == "asc":
                        query = query.order_by(DataObject.size)
                    else:
                        query = query.order_by(DataObject.size, order="desc")
                elif sort_by == "create_time":
                    if sort_order == "asc":
                        query = query.order_by(DataObject.create_time)
                    else:
                        query = query.order_by(DataObject.create_time, order="desc")
                elif sort_by == "modify_time":
                    if sort_order == "asc":
                        query = query.order_by(DataObject.modify_time)
                    else:
                        query = query.order_by(DataObject.modify_time, order="desc")
            
            # Apply limit and offset
            query = query.limit(limit).offset(offset)
            
            # Execute query and fetch results
            results = []
            for row in query:
                obj = session.data_objects.get(f"{row[DataObject.collection_name]}/{row[DataObject.name]}")
                results.append(obj)
            
            return results
    
    def query_collections_by_metadata(
        self,
        metadata_items: List[Tuple[str, str, Optional[str]]],
        operator: str = "AND",
        limit: int = 100,
        offset: int = 0,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> List[Any]:
        """
        Query collections by metadata.
        
        Args:
            metadata_items: List of (name, value, units) tuples
            operator: Logical operator to use between items ("AND" or "OR")
            limit: Maximum number of results to return
            offset: Number of results to skip
            sort_by: Field to sort results by
            sort_order: Sort order ("asc" or "desc")
            
        Returns:
            List of collections matching the query
        """
        with self.client.session() as session:
            # Build query
            query = session.query(Collection)
            
            # Add metadata conditions
            for i, (name, value, units) in enumerate(metadata_items):
                alias = f"meta{i}"
                query = query.filter(
                    Criterion('=', CollectionMeta.name, name, alias),
                    Criterion('=', CollectionMeta.value, value, alias)
                )
                if units:
                    query = query.filter(
                        Criterion('=', CollectionMeta.units, units, alias)
                    )
            
            # Apply sorting
            if sort_by:
                if sort_by == "name":
                    if sort_order == "asc":
                        query = query.order_by(Collection.name)
                    else:
                        query = query.order_by(Collection.name, order="desc")
                elif sort_by == "create_time":
                    if sort_order == "asc":
                        query = query.order_by(Collection.create_time)
                    else:
                        query = query.order_by(Collection.create_time, order="desc")
                elif sort_by == "modify_time":
                    if sort_order == "asc":
                        query = query.order_by(Collection.modify_time)
                    else:
                        query = query.order_by(Collection.modify_time, order="desc")
            
            # Apply limit and offset
            query = query.limit(limit).offset(offset)
            
            # Execute query and fetch results
            results = []
            for row in query:
                coll = session.collections.get(row[Collection.name])
                results.append(coll)
            
            return results
    
    def find_sequencer_runs(
        self,
        sequencer_type: str,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Any]:
        """
        Find sequencer runs in iRODS.
        
        Args:
            sequencer_type: Type of sequencer
            status: Optional status to filter by
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List of collections matching the query
        """
        metadata_items = [("sequencer_type", sequencer_type, None)]
        
        if status:
            metadata_items.append(("status", status, None))
        
        return self.query_collections_by_metadata(
            metadata_items=metadata_items,
            limit=limit,
            offset=offset,
            sort_by="modify_time",
            sort_order="desc"
        )
