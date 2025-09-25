"""
Qdrant Vector Database Integration for RAG

This module handles Qdrant vector database operations for storing and retrieving business rules.
"""
from typing import List, Dict, Any, Optional, Tuple
import logging
from dataclasses import dataclass
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
import uuid

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Represents a search result from Qdrant"""
    rule_id: str
    score: float
    content: str
    metadata: Dict[str, Any]


class QdrantRAG:
    """Qdrant-based Retrieval Augmented Generation for business rules"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "business_rules",
        vector_size: int = 384
    ):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.client = None
        
    def connect(self) -> bool:
        """Connect to Qdrant database"""
        try:
            self.client = QdrantClient(host=self.host, port=self.port)
            logger.info(f"Connected to Qdrant at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {str(e)}")
            return False
    
    def create_collection(self, recreate: bool = False) -> bool:
        """Create collection for business rules"""
        if not self.client:
            logger.error("Not connected to Qdrant")
            return False
            
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_exists = any(col.name == self.collection_name for col in collections.collections)
            
            if collection_exists and recreate:
                logger.info(f"Deleting existing collection: {self.collection_name}")
                self.client.delete_collection(collection_name=self.collection_name)
                collection_exists = False
            
            if not collection_exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
                )
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection already exists: {self.collection_name}")
                
            return True
        except Exception as e:
            logger.error(f"Failed to create collection: {str(e)}")
            return False
    
    def add_rules(self, rules_data: List[Dict[str, Any]], embeddings: List[List[float]]) -> bool:
        """Add business rules to the vector database"""
        if not self.client:
            logger.error("Not connected to Qdrant")
            return False
            
        if len(rules_data) != len(embeddings):
            logger.error("Mismatch between rules data and embeddings count")
            return False
        
        try:
            points = []
            for i, (rule_data, embedding) in enumerate(zip(rules_data, embeddings)):
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        "rule_id": rule_data["id"],
                        "name": rule_data["name"],
                        "description": rule_data["description"],
                        "domain": rule_data["domain"],
                        "category": rule_data["category"],
                        "condition": rule_data["condition"],
                        "action": rule_data["action"],
                        "priority": rule_data["priority"],
                        "parameters": rule_data["parameters"],
                        "metadata": rule_data["metadata"],
                        "text_content": rule_data.get("text_content", "")
                    }
                )
                points.append(point)
            
            # Batch insert points
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
                
            logger.info(f"Added {len(points)} rules to Qdrant")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add rules to Qdrant: {str(e)}")
            return False
    
    def search_similar_rules(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        domain_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
        min_priority: Optional[int] = None
    ) -> List[SearchResult]:
        """Search for similar business rules"""
        if not self.client:
            logger.error("Not connected to Qdrant")
            return []
        
        try:
            # Build filters
            must_conditions = []
            
            if domain_filter:
                must_conditions.append(
                    FieldCondition(key="domain", match=MatchValue(value=domain_filter))
                )
            
            if category_filter:
                must_conditions.append(
                    FieldCondition(key="category", match=MatchValue(value=category_filter))
                )
            
            if min_priority:
                must_conditions.append(
                    FieldCondition(
                        key="priority",
                        range=models.Range(gte=min_priority)
                    )
                )
            
            query_filter = Filter(must=must_conditions) if must_conditions else None
            
            # Perform search
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=query_filter,
                limit=top_k,
                with_payload=True
            )
            
            # Convert to SearchResult objects
            results = []
            for hit in search_result:
                result = SearchResult(
                    rule_id=hit.payload["rule_id"],
                    score=hit.score,
                    content=hit.payload.get("text_content", ""),
                    metadata={
                        "name": hit.payload["name"],
                        "description": hit.payload["description"],
                        "domain": hit.payload["domain"],
                        "category": hit.payload["category"],
                        "condition": hit.payload["condition"],
                        "action": hit.payload["action"],
                        "priority": hit.payload["priority"],
                        "parameters": hit.payload["parameters"],
                        "metadata": hit.payload["metadata"]
                    }
                )
                results.append(result)
            
            logger.info(f"Found {len(results)} similar rules")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search rules: {str(e)}")
            return []
    
    def get_rule_by_id(self, rule_id: str) -> Optional[SearchResult]:
        """Get a specific rule by ID"""
        if not self.client:
            logger.error("Not connected to Qdrant")
            return None
        
        try:
            search_result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[FieldCondition(key="rule_id", match=MatchValue(value=rule_id))]
                ),
                limit=1,
                with_payload=True
            )
            
            if search_result[0]:  # search_result is a tuple (points, next_page_offset)
                hit = search_result[0][0]
                result = SearchResult(
                    rule_id=hit.payload["rule_id"],
                    score=1.0,  # Perfect match
                    content=hit.payload.get("text_content", ""),
                    metadata={
                        "name": hit.payload["name"],
                        "description": hit.payload["description"],
                        "domain": hit.payload["domain"],
                        "category": hit.payload["category"],
                        "condition": hit.payload["condition"],
                        "action": hit.payload["action"],
                        "priority": hit.payload["priority"],
                        "parameters": hit.payload["parameters"],
                        "metadata": hit.payload["metadata"]
                    }
                )
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get rule by ID: {str(e)}")
            return None
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection"""
        if not self.client:
            return {"error": "Not connected"}
        
        try:
            info = self.client.get_collection(collection_name=self.collection_name)
            return {
                "status": "connected",
                "collection_name": self.collection_name,
                "points_count": info.points_count,
                "vector_size": info.config.params.vectors.size,
                "distance": info.config.params.vectors.distance.value
            }
        except Exception as e:
            return {"error": str(e)}
    
    def clear_collection(self) -> bool:
        """Clear all points from the collection"""
        if not self.client:
            logger.error("Not connected to Qdrant")
            return False
        
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            self.create_collection()
            logger.info("Collection cleared and recreated")
            return True
        except Exception as e:
            logger.error(f"Failed to clear collection: {str(e)}")
            return False