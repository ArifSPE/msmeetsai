"""
Business Rule Agent

This module implements the core agentic behavior for discovering, analyzing, and applying business rules.
"""
from typing import List, Dict, Any, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum
import json

from ..rag import BusinessRulesRAG, SearchResult
from .llm_service import LocalLLMService

logger = logging.getLogger(__name__)


class AgentState(Enum):
    """States of the business rule agent"""
    IDLE = "idle"
    ANALYZING = "analyzing"
    QUERYING_RULES = "querying_rules"
    REASONING = "reasoning"
    DECIDING = "deciding"
    EXPLAINING = "explaining"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class AgentDecision:
    """Represents a decision made by the agent"""
    scenario: str
    applicable_rules: List[Dict[str, Any]]
    decision_outcome: str
    confidence: float
    reasoning: str
    execution_plan: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class BusinessRuleAgent:
    """Intelligent agent for business rule discovery and application"""
    
    def __init__(
        self,
        rag_service: BusinessRulesRAG,
        llm_service: LocalLLMService,
        confidence_threshold: float = 0.7,
        max_iterations: int = 10
    ):
        self.rag_service = rag_service
        self.llm_service = llm_service
        self.confidence_threshold = confidence_threshold
        self.max_iterations = max_iterations
        
        self.state = AgentState.IDLE
        self.current_scenario = None
        self.iteration_count = 0
        self.decision_history: List[AgentDecision] = []
    
    def analyze_scenario(
        self,
        scenario_description: str,
        business_context: Optional[Dict[str, Any]] = None,
        domain_hint: Optional[str] = None,
        category_hint: Optional[str] = None
    ) -> AgentDecision:
        """Analyze a business scenario and make intelligent rule-based decisions"""
        
        logger.info(f"Starting scenario analysis: {scenario_description[:100]}...")
        self.state = AgentState.ANALYZING
        self.current_scenario = scenario_description
        self.iteration_count = 0
        
        try:
            # Step 1: Query RAG for relevant rules
            self.state = AgentState.QUERYING_RULES
            relevant_rules = self._query_relevant_rules(
                scenario_description, domain_hint, category_hint
            )
            
            if not relevant_rules:
                return self._create_no_rules_decision(scenario_description)
            
            # Step 2: Use LLM to analyze scenario and rules
            self.state = AgentState.REASONING
            analysis_result = self._analyze_with_llm(
                scenario_description, relevant_rules, business_context
            )
            
            # Step 3: Determine executable rules
            self.state = AgentState.DECIDING
            executable_rules = self._determine_executable_rules(
                analysis_result, business_context or {}
            )
            
            # Step 4: Generate explanation
            self.state = AgentState.EXPLAINING
            explanation = self._generate_explanation(
                executable_rules, scenario_description, business_context
            )
            
            # Step 5: Create final decision
            decision = self._create_decision(
                scenario_description, executable_rules, analysis_result, explanation, business_context
            )
            
            self.decision_history.append(decision)
            self.state = AgentState.COMPLETED
            
            logger.info(f"Scenario analysis completed. {len(executable_rules)} rules applicable.")
            return decision
            
        except Exception as e:
            logger.error(f"Error in scenario analysis: {str(e)}")
            self.state = AgentState.ERROR
            return self._create_error_decision(scenario_description, str(e))
    
    def _query_relevant_rules(
        self,
        scenario: str,
        domain_hint: Optional[str] = None,
        category_hint: Optional[str] = None
    ) -> List[SearchResult]:
        """Query RAG system for relevant business rules"""
        
        try:
            # Enhanced query with domain-specific keywords
            enhanced_query = self._enhance_query(scenario, domain_hint, category_hint)
            
            results = self.rag_service.query_rules(
                query=enhanced_query,
                top_k=10,
                domain_filter=domain_hint,
                category_filter=category_hint,
                confidence_threshold=self.confidence_threshold * 0.8  # Slightly lower for initial retrieval
            )
            
            logger.info(f"Found {len(results)} relevant rules for scenario")
            return results
            
        except Exception as e:
            logger.error(f"Error querying relevant rules: {str(e)}")
            return []
    
    def _enhance_query(
        self,
        scenario: str,
        domain_hint: Optional[str] = None,
        category_hint: Optional[str] = None
    ) -> str:
        """Enhance query with domain-specific terms"""
        
        query_parts = [scenario]
        
        if domain_hint:
            query_parts.append(f"domain:{domain_hint}")
        
        if category_hint:
            query_parts.append(f"category:{category_hint}")
        
        # Add common business terms based on scenario content
        scenario_lower = scenario.lower()
        
        if any(term in scenario_lower for term in ['loan', 'credit', 'finance', 'money', 'payment']):
            query_parts.append("financial business rules")
        
        if any(term in scenario_lower for term in ['inventory', 'stock', 'product', 'warehouse']):
            query_parts.append("inventory management rules")
        
        if any(term in scenario_lower for term in ['customer', 'support', 'service', 'ticket']):
            query_parts.append("customer service rules")
        
        if any(term in scenario_lower for term in ['data', 'privacy', 'compliance', 'gdpr', 'regulation']):
            query_parts.append("compliance regulatory rules")
        
        return " ".join(query_parts)
    
    def _analyze_with_llm(
        self,
        scenario: str,
        rules: List[SearchResult],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Use LLM to analyze scenario against available rules"""
        
        # Convert SearchResult to dict format for LLM
        rules_data = [
            {
                "id": rule.rule_id,
                "name": rule.metadata["name"],
                "description": rule.metadata["description"],
                "domain": rule.metadata["domain"],
                "category": rule.metadata["category"],
                "condition": rule.metadata["condition"],
                "action": rule.metadata["action"],
                "priority": rule.metadata["priority"],
                "parameters": rule.metadata["parameters"],
                "similarity_score": rule.score
            }
            for rule in rules
        ]
        
        analysis = self.llm_service.analyze_scenario(scenario, rules_data, context)
        
        if "error" in analysis:
            logger.error(f"LLM analysis error: {analysis['error']}")
            return {"applicable_rules": [], "overall_assessment": "Analysis failed", "recommended_actions": []}
        
        return analysis
    
    def _determine_executable_rules(
        self,
        analysis_result: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Determine which rules should actually be executed"""
        
        applicable_rules = analysis_result.get("applicable_rules", [])
        
        # Filter by confidence threshold
        high_confidence_rules = [
            rule for rule in applicable_rules 
            if rule.get("confidence", 0) >= self.confidence_threshold
        ]
        
        if not high_confidence_rules:
            logger.warning("No rules meet confidence threshold")
            return []
        
        # Get full rule details for reasoning
        full_rules = []
        for rule_ref in high_confidence_rules:
            rule_id = rule_ref["rule_id"]
            full_rule = self.rag_service.get_rule_by_id(rule_id)
            if full_rule:
                full_rules.append({
                    "id": full_rule.id,
                    "name": full_rule.name,
                    "description": full_rule.description,
                    "condition": full_rule.condition,
                    "action": full_rule.action,
                    "priority": full_rule.priority,
                    "parameters": full_rule.parameters,
                    "confidence": rule_ref.get("confidence", 0),
                    "reasoning": rule_ref.get("reasoning", "")
                })
        
        # Use LLM to reason about execution order and conflicts
        reasoning_result = self.llm_service.reason_about_rules(full_rules, context)
        
        executable_rules = reasoning_result.get("executable_rules", [])
        
        # Merge reasoning results back with full rule data
        final_rules = []
        for exec_rule in executable_rules:
            if exec_rule.get("condition_met", False):
                # Find the corresponding full rule
                full_rule = next(
                    (r for r in full_rules if r["id"] == exec_rule["rule_id"]), 
                    None
                )
                if full_rule:
                    full_rule.update({
                        "execution_order": exec_rule.get("execution_order", 0),
                        "expected_outcome": exec_rule.get("expected_outcome", "")
                    })
                    final_rules.append(full_rule)
        
        # Sort by execution order
        final_rules.sort(key=lambda x: x.get("execution_order", 0))
        
        return final_rules
    
    def _generate_explanation(
        self,
        executable_rules: List[Dict[str, Any]],
        scenario: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Generate human-readable explanation for the decision"""
        
        if not executable_rules:
            return "No applicable business rules were found for this scenario."
        
        actions = [rule["action"] for rule in executable_rules]
        outcome = " and ".join(actions)
        
        explanation = self.llm_service.generate_explanation(
            executable_rules, outcome, context or {}
        )
        
        return explanation
    
    def _create_decision(
        self,
        scenario: str,
        executable_rules: List[Dict[str, Any]],
        analysis_result: Dict[str, Any],
        explanation: str,
        context: Optional[Dict[str, Any]]
    ) -> AgentDecision:
        """Create the final agent decision"""
        
        # Calculate overall confidence
        if executable_rules:
            confidences = [rule.get("confidence", 0) for rule in executable_rules]
            overall_confidence = sum(confidences) / len(confidences)
        else:
            overall_confidence = 0.0
        
        # Create execution plan
        execution_plan = [
            {
                "step": i + 1,
                "rule_id": rule["id"],
                "rule_name": rule["name"],
                "action": rule["action"],
                "expected_outcome": rule.get("expected_outcome", ""),
                "parameters": rule["parameters"]
            }
            for i, rule in enumerate(executable_rules)
        ]
        
        # Determine outcome
        if executable_rules:
            actions = [rule["action"] for rule in executable_rules]
            outcome = f"Execute {len(actions)} rule(s): {', '.join(actions)}"
        else:
            outcome = "No rules to execute"
        
        return AgentDecision(
            scenario=scenario,
            applicable_rules=executable_rules,
            decision_outcome=outcome,
            confidence=overall_confidence,
            reasoning=explanation,
            execution_plan=execution_plan,
            metadata={
                "analysis_timestamp": None,  # Will be set by execution engine
                "total_rules_considered": len(analysis_result.get("applicable_rules", [])),
                "rules_above_threshold": len(executable_rules),
                "overall_assessment": analysis_result.get("overall_assessment", ""),
                "recommended_actions": analysis_result.get("recommended_actions", []),
                "context_provided": context is not None,
                "agent_iterations": self.iteration_count
            }
        )
    
    def _create_no_rules_decision(self, scenario: str) -> AgentDecision:
        """Create decision when no rules are found"""
        return AgentDecision(
            scenario=scenario,
            applicable_rules=[],
            decision_outcome="No applicable business rules found",
            confidence=0.0,
            reasoning="The RAG system did not find any business rules relevant to this scenario. This could indicate that the scenario is outside the scope of current rule coverage, or the scenario description needs to be more specific.",
            execution_plan=[],
            metadata={
                "analysis_timestamp": None,
                "total_rules_considered": 0,
                "rules_above_threshold": 0,
                "overall_assessment": "No rules found",
                "recommended_actions": ["Review scenario description", "Check rule coverage", "Consider adding new rules"],
                "context_provided": False,
                "agent_iterations": 0
            }
        )
    
    def _create_error_decision(self, scenario: str, error_message: str) -> AgentDecision:
        """Create decision when an error occurs"""
        return AgentDecision(
            scenario=scenario,
            applicable_rules=[],
            decision_outcome=f"Analysis failed: {error_message}",
            confidence=0.0,
            reasoning=f"An error occurred during analysis: {error_message}",
            execution_plan=[],
            metadata={
                "analysis_timestamp": None,
                "error": error_message,
                "total_rules_considered": 0,
                "rules_above_threshold": 0,
                "overall_assessment": "Error occurred",
                "recommended_actions": ["Check system logs", "Verify system components"],
                "context_provided": False,
                "agent_iterations": self.iteration_count
            }
        )
    
    def get_decision_history(self) -> List[AgentDecision]:
        """Get history of all decisions made by this agent"""
        return self.decision_history.copy()
    
    def get_current_state(self) -> AgentState:
        """Get current state of the agent"""
        return self.state
    
    def reset_state(self) -> None:
        """Reset agent to idle state"""
        self.state = AgentState.IDLE
        self.current_scenario = None
        self.iteration_count = 0