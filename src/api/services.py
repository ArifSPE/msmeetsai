"""
AgenticSystemService

Service layer that coordinates between RAG, agents, and execution engine.
"""
from typing import List, Dict, Any, Optional, Tuple
import logging
import asyncio
from pathlib import Path

from ..rag import BusinessRulesRAG
from ..agents import BusinessRuleAgent, LocalLLMService
from ..execution import BusinessRuleExecutionEngine

logger = logging.getLogger(__name__)


class AgenticSystemService:
    """Service that orchestrates the entire agentic system"""
    
    def __init__(
        self,
        rules_directory: Path,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        collection_name: str = "business_rules",
        ollama_base_url: str = "http://localhost:11434",
        ollama_model: str = "llama2:7b",
        embedding_model: str = "nomic-embed-text",
        confidence_threshold: float = 0.7
    ):
        self.rules_directory = rules_directory
        self.qdrant_host = qdrant_host
        self.qdrant_port = qdrant_port
        self.collection_name = collection_name
        self.ollama_base_url = ollama_base_url
        self.ollama_model = ollama_model
        self.embedding_model = embedding_model
        self.confidence_threshold = confidence_threshold
        
        # Core components
        self.rag_service = None
        self.llm_service = None
        self.agent = None
        self.execution_engine = None
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialize all system components"""
        try:
            logger.info("Initializing agentic system components...")
            
            # Initialize RAG service
            self.rag_service = BusinessRulesRAG(
                rules_directory=self.rules_directory,
                qdrant_host=self.qdrant_host,
                qdrant_port=self.qdrant_port,
                collection_name=self.collection_name,
                embedding_model=self.embedding_model,
                ollama_base_url=self.ollama_base_url
            )
            
            if not self.rag_service.initialize():
                logger.error("Failed to initialize RAG service")
                return False
            
            # Index business rules
            if not self.rag_service.index_rules():
                logger.error("Failed to index business rules")
                return False
            
            # Initialize LLM service
            self.llm_service = LocalLLMService(
                model=self.ollama_model,
                base_url=self.ollama_base_url
            )
            
            if not self.llm_service.initialize():
                logger.error("Failed to initialize LLM service")
                return False
            
            # Initialize agent
            self.agent = BusinessRuleAgent(
                rag_service=self.rag_service,
                llm_service=self.llm_service,
                confidence_threshold=self.confidence_threshold
            )
            
            # Initialize execution engine
            self.execution_engine = BusinessRuleExecutionEngine()
            
            self.initialized = True
            logger.info("Agentic system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize agentic system: {str(e)}")
            return False
    
    async def analyze_scenario(
        self,
        scenario: str,
        context: Optional[Dict[str, Any]] = None,
        domain_hint: Optional[str] = None,
        category_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze a business scenario"""
        if not self.initialized:
            raise RuntimeError("System not initialized")
        
        # Run analysis in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        decision = await loop.run_in_executor(
            None,
            self.agent.analyze_scenario,
            scenario,
            context,
            domain_hint,
            category_hint
        )
        
        return {
            "scenario": decision.scenario,
            "applicable_rules": decision.applicable_rules,
            "decision_outcome": decision.decision_outcome,
            "confidence": decision.confidence,
            "reasoning": decision.reasoning,
            "execution_plan": decision.execution_plan,
            "metadata": decision.metadata
        }
    
    async def execute_rules(
        self,
        scenario: str,
        rules: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute business rules"""
        if not self.initialized:
            raise RuntimeError("System not initialized")
        
        # Create execution plan
        plan = self.execution_engine.create_execution_plan(scenario, rules, context)
        
        # Execute in thread pool
        loop = asyncio.get_event_loop()
        executed_plan = await loop.run_in_executor(
            None,
            self.execution_engine.execute_plan,
            plan
        )
        
        return self.execution_engine.get_execution_summary(executed_plan)
    
    async def analyze_and_execute(
        self,
        scenario: str,
        context: Optional[Dict[str, Any]] = None,
        domain_hint: Optional[str] = None,
        category_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze scenario and execute rules in one operation"""
        
        # Analyze scenario
        analysis = await self.analyze_scenario(scenario, context, domain_hint, category_hint)
        
        # Execute if rules found
        execution = None
        if analysis["applicable_rules"]:
            execution = await self.execute_rules(
                scenario=scenario,
                rules=analysis["applicable_rules"],
                context=context or {}
            )
        else:
            execution = {
                "plan_id": "no_execution",
                "scenario": scenario,
                "overall_status": "skipped",
                "total_rules": 0,
                "successful_rules": 0,
                "failed_rules": 0,
                "execution_time": 0,
                "results": [],
                "message": "No applicable rules found"
            }
        
        return {
            "scenario": scenario,
            "analysis": analysis,
            "execution": execution
        }
    
    async def get_rules(
        self,
        domain: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get business rules with filtering"""
        if not self.initialized:
            raise RuntimeError("System not initialized")
        
        all_rules = self.rag_service.rules_manager.get_all_rules()
        
        # Apply filters
        filtered_rules = all_rules
        if domain:
            filtered_rules = [r for r in filtered_rules if r.domain == domain]
        if category:
            filtered_rules = [r for r in filtered_rules if r.category == category]
        
        # Apply pagination
        total_count = len(filtered_rules)
        paginated_rules = filtered_rules[offset:offset + limit]
        
        return {
            "rules": [rule.to_dict() for rule in paginated_rules],
            "total_count": total_count,
            "domains": self.rag_service.rules_manager.get_domains(),
            "categories": self.rag_service.rules_manager.get_categories()
        }
    
    async def get_rule_by_id(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific rule by ID"""
        if not self.initialized:
            raise RuntimeError("System not initialized")
        
        rule = self.rag_service.get_rule_by_id(rule_id)
        return rule.to_dict() if rule else None
    
    async def get_execution_history(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Get execution history"""
        if not self.initialized:
            raise RuntimeError("System not initialized")
        
        history = self.execution_engine.get_execution_history()
        
        # Apply pagination
        total_count = len(history)
        paginated_history = history[offset:offset + limit]
        
        return paginated_history
    
    async def chat_with_agent(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Chat with the business rules agent"""
        if not self.initialized:
            raise RuntimeError("System not initialized")
        
        # Build system prompt for business rules context
        system_prompt = """You are a business rules expert assistant. You help users understand and work with business rules across different domains like finance, inventory, compliance, and customer service.

You have access to a comprehensive database of business rules and can:
1. Explain how specific rules work
2. Help identify which rules apply to business scenarios
3. Provide guidance on rule implementation
4. Answer questions about rule priorities and conflicts

Be helpful, accurate, and provide specific examples when possible."""
        
        messages = conversation_history or []
        messages.append({"role": "user", "content": message})
        
        # Use LLM service for chat
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            self.llm_service.chat_with_context,
            messages,
            system_prompt
        )
        
        # Suggest actions based on message content
        suggested_actions = []
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["scenario", "analyze", "check"]):
            suggested_actions.append("Analyze a business scenario")
        
        if any(word in message_lower for word in ["rules", "list", "show"]):
            suggested_actions.append("View available business rules")
        
        if any(word in message_lower for word in ["execute", "run", "apply"]):
            suggested_actions.append("Execute business rules")
        
        return {
            "message": response,
            "context": context,
            "suggested_actions": suggested_actions
        }
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        if not self.initialized:
            return {
                "initialized": False,
                "error": "System not initialized"
            }
        
        return self.rag_service.get_system_info()
    
    async def cleanup(self) -> None:
        """Cleanup system resources"""
        logger.info("Cleaning up agentic system...")
        # Add any cleanup logic here if needed
        self.initialized = False