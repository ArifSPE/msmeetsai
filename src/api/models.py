"""
Pydantic Models for the FastAPI Application

Defines request and response models for the API endpoints.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# Request Models
class AnalysisRequest(BaseModel):
    """Request for scenario analysis"""
    scenario: str = Field(..., description="Business scenario to analyze")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context data")
    domain_hint: Optional[str] = Field(None, description="Domain hint to filter rules")
    category_hint: Optional[str] = Field(None, description="Category hint to filter rules")


class RuleExecution(BaseModel):
    """Rule to execute"""
    id: str
    name: str
    description: Optional[str] = None
    condition: Optional[str] = None
    action: str
    priority: Optional[int] = 1
    parameters: Optional[Dict[str, Any]] = None


class ExecutionRequest(BaseModel):
    """Request for rule execution"""
    scenario: str = Field(..., description="Business scenario")
    context: Optional[Dict[str, Any]] = Field(None, description="Execution context")
    rules: Optional[List[RuleExecution]] = Field(None, description="Specific rules to execute")
    domain_hint: Optional[str] = Field(None, description="Domain hint if rules not specified")
    category_hint: Optional[str] = Field(None, description="Category hint if rules not specified")


class ChatMessage(BaseModel):
    """Chat message"""
    role: str = Field(..., description="Message role: user or assistant")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request for chat with agent"""
    message: str = Field(..., description="User message")
    context: Optional[Dict[str, Any]] = Field(None, description="Chat context")
    conversation_history: Optional[List[ChatMessage]] = Field(None, description="Previous conversation")


# Response Models
class RuleInfo(BaseModel):
    """Information about a business rule"""
    id: str
    name: str
    description: str
    domain: str
    category: str
    condition: str
    action: str
    priority: int
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class ExecutionStep(BaseModel):
    """Execution step information"""
    step: int
    rule_id: str
    rule_name: str
    action: str
    expected_outcome: str
    parameters: Dict[str, Any]


class AnalysisResponse(BaseModel):
    """Response for scenario analysis"""
    scenario: str
    applicable_rules: List[RuleInfo]
    decision_outcome: str
    overall_confidence: float
    reasoning: str
    execution_plan: List[ExecutionStep]
    metadata: Dict[str, Any]


class ExecutionResultInfo(BaseModel):
    """Information about rule execution result"""
    rule_id: str
    rule_name: str
    status: str
    duration: Optional[float] = None
    output: Dict[str, Any]
    error: Optional[str] = None


class ExecutionResponse(BaseModel):
    """Response for rule execution"""
    scenario: str
    execution_plan_id: str
    overall_status: str
    total_rules: Optional[int] = None
    successful_rules: Optional[int] = None
    failed_rules: Optional[int] = None
    execution_time: Optional[float] = None
    results: Optional[List[ExecutionResultInfo]] = None
    message: Optional[str] = None


class FullProcessResponse(BaseModel):
    """Response for full analyze and execute process"""
    scenario: str
    analysis: AnalysisResponse
    execution: ExecutionResponse


class RulesListResponse(BaseModel):
    """Response for rules list"""
    rules: List[RuleInfo]
    total_count: int
    domains: List[str]
    categories: List[str]


class ExecutionSummary(BaseModel):
    """Summary of an execution"""
    plan_id: str
    scenario: str
    overall_status: str
    total_rules: int
    successful_rules: int
    failed_rules: int
    execution_time: Optional[float] = None


class HistoryResponse(BaseModel):
    """Response for execution history"""
    executions: List[ExecutionSummary]
    total_count: int


class ChatResponse(BaseModel):
    """Response for chat"""
    response: str
    context: Optional[Dict[str, Any]] = None
    suggested_actions: Optional[List[str]] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="System status")
    message: str = Field(..., description="Status message")
    system_info: Optional[Dict[str, Any]] = Field(None, description="System information")


# Error Models
class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())