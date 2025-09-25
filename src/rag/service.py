"""
RAG Service for Business Rules

This module provides the main RAG interface that combines business rules management,
embeddings generation, and vector database operations.
"""
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

from ..business_rules import BusinessRulesManager, BusinessRule
from .embeddings import EmbeddingsService
from .qdrant_client import QdrantRAG, SearchResult

logger = logging.getLogger(__name__)


class BusinessRulesRAG:
    """Main RAG service for business rules"""
    
    def __init__(
        self,
        rules_directory: Path,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        collection_name: str = "business_rules",
        embedding_model: str = "nomic-embed-text",
        ollama_base_url: str = "http://localhost:11434"
    ):
        self.rules_manager = BusinessRulesManager(rules_directory)
        self.embeddings_service = EmbeddingsService(
            base_url=ollama_base_url,
            model_name=embedding_model
        )
        
        # Get embedding dimension from the service
        self.vector_size = self.embeddings_service.get_embedding_dimension()
        
        self.qdrant_rag = QdrantRAG(
            host=qdrant_host,
            port=qdrant_port,
            collection_name=collection_name,
            vector_size=self.vector_size
        )
        
        self.initialized = False
    
    def initialize(self, recreate_collection: bool = False) -> bool:
        """Initialize the RAG system"""
        try:
            # Initialize embeddings service
            if not self.embeddings_service.initialize():
                logger.error("Failed to initialize embeddings service")
                return False
            
            # Connect to Qdrant
            if not self.qdrant_rag.connect():
                logger.error("Failed to connect to Qdrant")
                return False
            
            # Create collection
            if not self.qdrant_rag.create_collection(recreate=recreate_collection):
                logger.error("Failed to create Qdrant collection")
                return False
            
            # Load business rules
            self.rules_manager.load_rules()
            if not self.rules_manager.rules:
                logger.warning("No business rules loaded")
            
            self.initialized = True
            logger.info("RAG system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {str(e)}")
            return False
    
    def index_rules(self) -> bool:
        """Index all business rules in the vector database"""
        if not self.initialized:
            logger.error("RAG system not initialized")
            return False
        
        try:
            rules = self.rules_manager.get_all_rules()
            if not rules:
                logger.warning("No rules to index")
                return True
            
            # Convert rules to text and generate embeddings
            rule_texts = [rule.to_text() for rule in rules]
            embeddings = self.embeddings_service.generate_embeddings(rule_texts)
            
            if embeddings is None:
                logger.error("Failed to generate embeddings")
                return False
            
            # Prepare rule data for indexing
            rules_data = []
            for rule, text in zip(rules, rule_texts):
                rule_data = rule.to_dict()
                rule_data["text_content"] = text
                rules_data.append(rule_data)
            
            # Add rules to Qdrant
            success = self.qdrant_rag.add_rules(rules_data, embeddings)
            if success:
                logger.info(f"Successfully indexed {len(rules)} business rules")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to index rules: {str(e)}")
            return False
    
    def query_rules(
        self,
        query: str,
        top_k: int = 5,
        domain_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
        min_priority: Optional[int] = None,
        confidence_threshold: float = 0.5
    ) -> List[SearchResult]:
        """Query for relevant business rules"""
        if not self.initialized:
            logger.error("RAG system not initialized")
            return []
        
        try:
            # Generate embedding for the query
            query_embedding = self.embeddings_service.generate_single_embedding(query)
            if query_embedding is None:
                logger.error("Failed to generate query embedding")
                return []
            
            # Search in Qdrant
            results = self.qdrant_rag.search_similar_rules(
                query_embedding=query_embedding,
                top_k=top_k,
                domain_filter=domain_filter,
                category_filter=category_filter,
                min_priority=min_priority
            )
            
            # Filter by confidence threshold
            filtered_results = [r for r in results if r.score >= confidence_threshold]
            
            logger.info(f"Query '{query}' returned {len(filtered_results)} relevant rules")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Failed to query rules: {str(e)}")
            return []
    
    def get_rule_by_id(self, rule_id: str) -> Optional[BusinessRule]:
        """Get a specific rule by its ID"""
        return self.rules_manager.get_rule_by_id(rule_id)
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information and status"""
        return {
            "initialized": self.initialized,
            "total_rules": len(self.rules_manager.rules),
            "domains": self.rules_manager.get_domains(),
            "categories": self.rules_manager.get_categories(),
            "vector_db_info": self.qdrant_rag.get_collection_info(),
            "embedding_model": self.embeddings_service.model_name,
            "vector_dimension": self.vector_size
        }
    
    def reinitialize(self) -> bool:
        """Reinitialize the system with fresh data"""
        logger.info("Reinitializing RAG system...")
        
        # Clear the collection and reload everything
        if self.qdrant_rag.clear_collection():
            self.rules_manager.load_rules()
            return self.index_rules()
        
        return False