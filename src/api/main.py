"""
FastAPI Main Application

Main FastAPI application for the Agentic Business Rules POC.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional
import logging
import uvicorn

from config.settings import settings
from src.rag import BusinessRulesRAG
from src.agents import BusinessRuleAgent, LocalLLMService
from src.execution import BusinessRuleExecutionEngine
from .models import (
    AnalysisRequest, AnalysisResponse, ExecutionRequest, ExecutionResponse,
    FullProcessResponse, RulesListResponse, HistoryResponse, ChatRequest,
    ChatResponse, HealthResponse, RuleInfo, ExecutionResultInfo, ExecutionSummary
)
from .services import AgenticSystemService

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Global service instance
agentic_service: Optional[AgenticSystemService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global agentic_service
    
    # Startup
    logger.info("Starting Agentic Business Rules POC...")
    
    try:
        # Initialize the agentic system
        agentic_service = AgenticSystemService(
            rules_directory=settings.business_rules_path,
            qdrant_host=settings.qdrant_host,
            qdrant_port=settings.qdrant_port,
            collection_name=settings.qdrant_collection_name,
            ollama_base_url=settings.ollama_base_url,
            ollama_model=settings.ollama_model,
            embedding_model=settings.ollama_embedding_model,
            confidence_threshold=settings.confidence_threshold
        )
        
        # Initialize and index rules
        success = await agentic_service.initialize()
        if success:
            logger.info("Agentic system initialized successfully")
        else:
            logger.error("Failed to initialize agentic system")
            
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        agentic_service = None
    
    yield
    
    # Shutdown
    logger.info("Shutting down Agentic Business Rules POC...")
    if agentic_service:
        await agentic_service.cleanup()


# Create FastAPI app
app = FastAPI(
    title="Agentic Business Rules POC",
    description="A POC demonstrating agentic architecture with business rules stored in RAG and executed by LLM agents",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with system health"""
    global agentic_service
    
    if not agentic_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    system_info = await agentic_service.get_system_info()
    
    return HealthResponse(
        status="healthy" if system_info["initialized"] else "unhealthy",
        message="Agentic Business Rules POC is running",
        system_info=system_info
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return await root()


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_scenario(request: AnalysisRequest):
    """Analyze a business scenario and determine applicable rules"""
    global agentic_service
    
    if not agentic_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        decision = await agentic_service.analyze_scenario(
            scenario=request.scenario,
            context=request.context,
            domain_hint=request.domain_hint,
            category_hint=request.category_hint
        )
        
        return AnalysisResponse(
            scenario=decision["scenario"],
            applicable_rules=[
                RuleInfo(
                    id=rule["id"],
                    name=rule["name"],
                    description=rule["description"],
                    domain=rule.get("domain", "unknown"),
                    category=rule.get("category", "general"),
                    condition=rule["condition"],
                    action=rule["action"],
                    priority=rule["priority"],
                    confidence=rule.get("confidence", 0.0),
                    reasoning=rule.get("reasoning", "")
                )
                for rule in decision["applicable_rules"]
            ],
            decision_outcome=decision["decision_outcome"],
            overall_confidence=decision["confidence"],
            reasoning=decision["reasoning"],
            execution_plan=decision["execution_plan"],
            metadata=decision["metadata"]
        )
        
    except Exception as e:
        logger.error(f"Error analyzing scenario: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/execute", response_model=ExecutionResponse)
async def execute_rules(request: ExecutionRequest):
    """Execute business rules for a scenario"""
    global agentic_service
    
    if not agentic_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # First analyze the scenario if rules not provided
        if not request.rules:
            decision = await agentic_service.analyze_scenario(
                scenario=request.scenario,
                context=request.context,
                domain_hint=request.domain_hint,
                category_hint=request.category_hint
            )
            rules_to_execute = decision["applicable_rules"]
        else:
            # Use provided rules
            rules_to_execute = [
                {
                    "id": rule.id,
                    "name": rule.name,
                    "description": rule.description,
                    "condition": rule.condition,
                    "action": rule.action,
                    "priority": rule.priority,
                    "parameters": rule.parameters or {}
                }
                for rule in request.rules
            ]
        
        if not rules_to_execute:
            return ExecutionResponse(
                scenario=request.scenario,
                execution_plan_id="no_execution",
                overall_status="skipped",
                message="No applicable rules found for execution"
            )
        
        # Execute the rules
        execution_result = await agentic_service.execute_rules(
            scenario=request.scenario,
            rules=rules_to_execute,
            context=request.context or {}
        )
        
        return ExecutionResponse(
            scenario=request.scenario,
            execution_plan_id=execution_result["plan_id"],
            overall_status=execution_result["overall_status"],
            total_rules=execution_result["total_rules"],
            successful_rules=execution_result["successful_rules"],
            failed_rules=execution_result["failed_rules"],
            execution_time=execution_result["execution_time"],
            results=[
                ExecutionResultInfo(
                    rule_id=result["rule_id"],
                    rule_name=result["rule_name"],
                    status=result["status"],
                    duration=result["duration"],
                    output=result["output"],
                    error=result["error"]
                )
                for result in execution_result["results"]
            ],
            message=f"Executed {execution_result['successful_rules']} of {execution_result['total_rules']} rules successfully"
        )
        
    except Exception as e:
        logger.error(f"Error executing rules: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


@app.post("/analyze-and-execute", response_model=FullProcessResponse)
async def analyze_and_execute(request: AnalysisRequest):
    """Analyze a scenario and execute applicable rules in one call"""
    global agentic_service
    
    if not agentic_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        result = await agentic_service.analyze_and_execute(
            scenario=request.scenario,
            context=request.context,
            domain_hint=request.domain_hint,
            category_hint=request.category_hint
        )
        
        return FullProcessResponse(
            scenario=result["scenario"],
            analysis=AnalysisResponse(
                scenario=result["analysis"]["scenario"],
                applicable_rules=[
                    RuleInfo(
                        id=rule["id"],
                        name=rule["name"],
                        description=rule["description"],
                        domain=rule.get("domain", "unknown"),
                        category=rule.get("category", "general"),
                        condition=rule["condition"],
                        action=rule["action"],
                        priority=rule["priority"],
                        confidence=rule.get("confidence", 0.0),
                        reasoning=rule.get("reasoning", "")
                    )
                    for rule in result["analysis"]["applicable_rules"]
                ],
                decision_outcome=result["analysis"]["decision_outcome"],
                overall_confidence=result["analysis"]["confidence"],
                reasoning=result["analysis"]["reasoning"],
                execution_plan=result["analysis"]["execution_plan"],
                metadata=result["analysis"]["metadata"]
            ),
            execution=ExecutionResponse(
                scenario=result["scenario"],
                execution_plan_id=result["execution"]["plan_id"],
                overall_status=result["execution"]["overall_status"],
                total_rules=result["execution"]["total_rules"],
                successful_rules=result["execution"]["successful_rules"],
                failed_rules=result["execution"]["failed_rules"],
                execution_time=result["execution"]["execution_time"],
                results=[
                    ExecutionResultInfo(
                        rule_id=res["rule_id"],
                        rule_name=res["rule_name"],
                        status=res["status"],
                        duration=res["duration"],
                        output=res["output"],
                        error=res["error"]
                    )
                    for res in result["execution"]["results"]
                ]
            )
        )
        
    except Exception as e:
        logger.error(f"Error in analyze and execute: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Process failed: {str(e)}")


@app.get("/rules", response_model=RulesListResponse)
async def list_rules(
    domain: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """List available business rules"""
    global agentic_service
    
    if not agentic_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        rules_info = await agentic_service.get_rules(domain, category, limit, offset)
        
        return RulesListResponse(
            rules=[
                RuleInfo(
                    id=rule["id"],
                    name=rule["name"],
                    description=rule["description"],
                    domain=rule["domain"],
                    category=rule["category"],
                    condition=rule["condition"],
                    action=rule["action"],
                    priority=rule["priority"]
                )
                for rule in rules_info["rules"]
            ],
            total_count=rules_info["total_count"],
            domains=rules_info["domains"],
            categories=rules_info["categories"]
        )
        
    except Exception as e:
        logger.error(f"Error listing rules: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list rules: {str(e)}")


@app.get("/rules/{rule_id}", response_model=RuleInfo)
async def get_rule(rule_id: str):
    """Get a specific rule by ID"""
    global agentic_service
    
    if not agentic_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        rule = await agentic_service.get_rule_by_id(rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        return RuleInfo(
            id=rule["id"],
            name=rule["name"],
            description=rule["description"],
            domain=rule["domain"],
            category=rule["category"],
            condition=rule["condition"],
            action=rule["action"],
            priority=rule["priority"],
            parameters=rule.get("parameters", {}),
            metadata=rule.get("metadata", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting rule {rule_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get rule: {str(e)}")


@app.get("/history", response_model=HistoryResponse)
async def get_execution_history(limit: int = 20, offset: int = 0):
    """Get execution history"""
    global agentic_service
    
    if not agentic_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        history = await agentic_service.get_execution_history(limit, offset)
        
        return HistoryResponse(
            executions=[
                ExecutionSummary(
                    plan_id=execution["plan_id"],
                    scenario=execution["scenario"],
                    overall_status=execution["overall_status"],
                    total_rules=execution["total_rules"],
                    successful_rules=execution["successful_rules"],
                    failed_rules=execution["failed_rules"],
                    execution_time=execution["execution_time"]
                )
                for execution in history
            ],
            total_count=len(history)
        )
        
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Chat with the agent about business rules"""
    global agentic_service
    
    if not agentic_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # Convert ChatMessage objects to dictionaries
        conversation_history = None
        if request.conversation_history:
            conversation_history = [
                {"role": msg.role, "content": msg.content}
                for msg in request.conversation_history
            ]
        
        response = await agentic_service.chat_with_agent(
            message=request.message,
            context=request.context,
            conversation_history=conversation_history
        )
        
        return ChatResponse(
            response=response["message"],
            context=response.get("context", {}),
            suggested_actions=response.get("suggested_actions", [])
        )
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )