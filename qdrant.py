from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Optional, Union, Any


class QdrantDB:
    def __init__(self, url: str = "localhost", port: int = 6333, api_key: Optional[str] = None):
        """
        Initialize the Qdrant client.
        
        Args:
            url: URL of the Qdrant server
            port: Port of the Qdrant server
            api_key: API key for authentication (if needed)
        """
        if api_key:
            self.client = QdrantClient(url=url, port=port, api_key=api_key, check_compatibility=False)
        else:
            self.client = QdrantClient(url=url, port=port, check_compatibility=False)
    
    def create_collection(self, collection_name: str, vector_size: int, distance: str = "Cosine"):
        """
        Create a new collection in Qdrant.
        
        Args:
            collection_name: Name of the collection
            vector_size: Dimensionality of vectors
            distance: Distance metric ("Cosine", "Euclid", or "Dot")
        
        Returns:
            True if collection was created successfully
        """
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=distance
                )
            )
            return True
        except Exception as e:
            print(f"Error creating collection: {e}")
            return False
    
    def list_collections(self):
        """
        List all collections in the database.
        
        Returns:
            List of collection names
        """
        return self.client.get_collections().collections
    
    def delete_collection(self, collection_name: str):
        """
        Delete a collection from Qdrant.
        
        Args:
            collection_name: Name of the collection to delete
        
        Returns:
            True if collection was deleted successfully
        """
        try:
            self.client.delete_collection(collection_name=collection_name)
            return True
        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False
    
    def add_points(self, collection_name: str, points: List[models.PointStruct]):
        """
        Add points to the collection.
        
        Args:
            collection_name: Name of the collection
            points: List of points to add (with id, vector, and payload)
        
        Returns:
            True if points were added successfully
        """
        try:
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            return True
        except Exception as e:
            print(f"Error adding points: {e}")
            return False
    
    def add_point(self, collection_name: str, id: Union[str, int], vector: List[float], payload: Optional[Dict] = None):
        """
        Add a single point to the collection.
        
        Args:
            collection_name: Name of the collection
            id: Unique identifier for the point
            vector: Vector data
            payload: Optional metadata
        
        Returns:
            True if point was added successfully
        """
        try:
            point = models.PointStruct(
                id=id,
                vector=vector,
                payload=payload
            )
            return self.add_points(collection_name, [point])
        except Exception as e:
            print(f"Error adding point: {e}")
            return False
    
    def search(self, collection_name: str, query_vector: List[float], limit: int = 10, 
               filter: Optional[models.Filter] = None):
        """
        Search for similar vectors in the collection.
        
        Args:
            collection_name: Name of the collection
            query_vector: Vector to search for
            limit: Maximum number of results
            filter: Optional filter conditions
        
        Returns:
            List of search results with points
        """
        try:
            return self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=filter
            )
        except Exception as e:
            print(f"Error searching: {e}")
            return []
    
    def get_point(self, collection_name: str, id: Union[str, int]):
        """
        Retrieve a point by its ID.
        
        Args:
            collection_name: Name of the collection
            id: ID of the point to retrieve
        
        Returns:
            The point if found, None otherwise
        """
        try:
            return self.client.retrieve(
                collection_name=collection_name,
                ids=[id]
            )[0]
        except Exception as e:
            print(f"Error retrieving point: {e}")
            return None
    
    def delete_points(self, collection_name: str, ids: List[Union[str, int]]):
        """
        Delete points by their IDs.
        
        Args:
            collection_name: Name of the collection
            ids: List of point IDs to delete
        
        Returns:
            True if points were deleted successfully
        """
        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=models.PointIdsList(
                    points=ids
                )
            )
            return True
        except Exception as e:
            print(f"Error deleting points: {e}")
            return False
    
    def delete_by_filter(self, collection_name: str, filter: models.Filter):
        """
        Delete points that match a filter.
        
        Args:
            collection_name: Name of the collection
            filter: Filter condition for points to delete
        
        Returns:
            True if points were deleted successfully
        """
        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=models.FilterSelector(
                    filter=filter
                )
            )
            return True
        except Exception as e:
            print(f"Error deleting points by filter: {e}")
            return False
    
    def update_payload(self, collection_name: str, id: Union[str, int], payload: Dict[str, Any]):
        """
        Update the payload of a point.
        
        Args:
            collection_name: Name of the collection
            id: ID of the point to update
            payload: New payload data
        
        Returns:
            True if payload was updated successfully
        """
        try:
            self.client.set_payload(
                collection_name=collection_name,
                payload=payload,
                points=[id]
            )
            return True
        except Exception as e:
            print(f"Error updating payload: {e}")
            return False
    
    def count_points(self, collection_name: str, filter: Optional[models.Filter] = None):
        """
        Count points in a collection, optionally filtered.
        
        Args:
            collection_name: Name of the collection
            filter: Optional filter to count specific points
            
        Returns:
            Count of points
        """
        try:
            return self.client.count(
                collection_name=collection_name,
                count_filter=filter
            ).count
        except Exception as e:
            print(f"Error counting points: {e}")
            return 0
