"""
Local LLM Service using Ollama and LlamaIndex

This module provides integration with local Llama models via Ollama for reasoning about business rules.
"""
from typing import List, Dict, Any, Optional
import logging
import json
from llama_index.llms.ollama import Ollama
from llama_index.core.llms import ChatMessage, MessageRole

logger = logging.getLogger(__name__)


class LocalLLMService:
    """Service for interacting with local Llama models via Ollama"""
    
    def __init__(
        self,
        model: str = "llama3.2:1b",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.3,
        top_p: float = 0.9,
        top_k: int = 40,
        request_timeout: float = 60.0
    ):
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.request_timeout = request_timeout
        self.llm = None
        
    def initialize(self) -> bool:
        """Initialize the LLM service"""
        try:
            self.llm = Ollama(
                model=self.model,
                base_url=self.base_url,
                temperature=self.temperature,
                additional_kwargs={
                    "top_p": self.top_p,
                    "top_k": self.top_k,
                },
                request_timeout=self.request_timeout
            )
            
            # Test the connection
            test_response = self.llm.complete("Hello")
            logger.info(f"LLM service initialized with model: {self.model}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {str(e)}")
            return False
    
    def analyze_scenario(
        self,
        scenario_description: str,
        available_rules: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze a business scenario and determine applicable rules"""
        if not self.llm:
            return {"error": "LLM service not initialized"}
        
        try:
            # Construct the analysis prompt
            prompt = self._build_analysis_prompt(scenario_description, available_rules, context)
            
            # Generate response
            response = self.llm.complete(prompt)
            
            # Parse the response
            analysis = self._parse_analysis_response(response.text)
            
            logger.info(f"Analyzed scenario: {scenario_description[:100]}...")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze scenario: {str(e)}")
            return {"error": str(e)}
    
    def reason_about_rules(
        self,
        rules: List[Dict[str, Any]],
        business_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Reason about which rules should be applied given business context"""
        if not self.llm:
            return {"error": "LLM service not initialized"}
        
        try:
            prompt = self._build_reasoning_prompt(rules, business_context)
            response = self.llm.complete(prompt)
            reasoning = self._parse_reasoning_response(response.text)
            
            logger.info(f"Reasoned about {len(rules)} rules")
            return reasoning
            
        except Exception as e:
            logger.error(f"Failed to reason about rules: {str(e)}")
            return {"error": str(e)}
    
    def generate_explanation(
        self,
        applied_rules: List[Dict[str, Any]],
        decision_outcome: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate human-readable explanation for rule decisions"""
        if not self.llm:
            return "Error: LLM service not initialized"
        
        try:
            prompt = self._build_explanation_prompt(applied_rules, decision_outcome, context)
            response = self.llm.complete(prompt)
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate explanation: {str(e)}")
            return f"Error generating explanation: {str(e)}"
    
    def _build_analysis_prompt(
        self,
        scenario: str,
        rules: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build prompt for scenario analysis"""
        
        rules_text = "\n".join([
            f"- Rule {rule['id']}: {rule['name']}\n"
            f"  Description: {rule['description']}\n"
            f"  Condition: {rule['condition']}\n"
            f"  Action: {rule['action']}\n"
            f"  Domain: {rule['domain']}\n"
            f"  Priority: {rule['priority']}\n"
            for rule in rules
        ])
        
        context_text = ""
        if context:
            context_text = f"\nAdditional Context:\n{json.dumps(context, indent=2)}\n"
        
        prompt = f"""You are a business rules analysis expert. Analyze the following scenario and determine which rules are applicable.

Scenario: {scenario}

Available Rules:
{rules_text}
{context_text}

Instructions:
1. Evaluate which rules are relevant to the scenario
2. Consider the conditions and priorities of each rule
3. Determine the confidence level for each applicable rule
4. Provide reasoning for your decisions

Respond with a JSON object containing:
{{
    "applicable_rules": [
        {{
            "rule_id": "string",
            "confidence": "float (0.0-1.0)",
            "reasoning": "string explaining why this rule applies"
        }}
    ],
    "overall_assessment": "string describing the overall analysis",
    "recommended_actions": ["list of recommended actions"]
}}

Response:"""

        return prompt
    
    def _build_reasoning_prompt(
        self,
        rules: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> str:
        """Build prompt for rule reasoning"""
        
        rules_text = "\n".join([
            f"Rule {rule['id']}: {rule['name']}\n"
            f"  Condition: {rule['condition']}\n"
            f"  Action: {rule['action']}\n"
            f"  Priority: {rule['priority']}\n"
            for rule in rules
        ])
        
        context_text = json.dumps(context, indent=2)
        
        prompt = f"""You are a business rules engine. Given the following rules and business context, determine which rules should be executed and in what order.

Business Context:
{context_text}

Available Rules:
{rules_text}

Instructions:
1. Evaluate each rule's condition against the provided context
2. Consider rule priorities and dependencies
3. Determine execution order
4. Identify any conflicts or dependencies

Respond with a JSON object:
{{
    "executable_rules": [
        {{
            "rule_id": "string",
            "execution_order": "integer",
            "condition_met": "boolean",
            "expected_outcome": "string describing what will happen"
        }}
    ],
    "conflicts": ["list of any conflicting rules"],
    "execution_plan": "string describing the execution strategy"
}}

Response:"""

        return prompt
    
    def _build_explanation_prompt(
        self,
        applied_rules: List[Dict[str, Any]],
        outcome: str,
        context: Dict[str, Any]
    ) -> str:
        """Build prompt for explanation generation"""
        
        rules_text = "\n".join([
            f"- {rule['name']}: {rule['action']}"
            for rule in applied_rules
        ])
        
        prompt = f"""Generate a clear, human-readable explanation for the following business rule decision.

Applied Rules:
{rules_text}

Decision Outcome: {outcome}

Context: {json.dumps(context, indent=2)}

Create a concise explanation that:
1. Explains why these rules were applied
2. Describes the outcome
3. Is understandable to business users
4. Mentions key factors that influenced the decision

Explanation:"""

        return prompt
    
    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the analysis response from the LLM"""
        try:
            # Try to extract JSON from the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback if JSON parsing fails
                return {
                    "applicable_rules": [],
                    "overall_assessment": response_text,
                    "recommended_actions": []
                }
                
        except json.JSONDecodeError:
            return {
                "applicable_rules": [],
                "overall_assessment": response_text,
                "recommended_actions": [],
                "parsing_error": "Failed to parse JSON response"
            }
    
    def _parse_reasoning_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the reasoning response from the LLM"""
        try:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return {
                    "executable_rules": [],
                    "conflicts": [],
                    "execution_plan": response_text
                }
                
        except json.JSONDecodeError:
            return {
                "executable_rules": [],
                "conflicts": [],
                "execution_plan": response_text,
                "parsing_error": "Failed to parse JSON response"
            }
    
    def chat_with_context(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> str:
        """Have a conversation with the LLM about business rules"""
        if not self.llm:
            return "Error: LLM service not initialized"
        
        try:
            chat_messages = []
            
            if system_prompt:
                chat_messages.append(ChatMessage(role=MessageRole.SYSTEM, content=system_prompt))
            
            for msg in messages:
                role = MessageRole.USER if msg["role"] == "user" else MessageRole.ASSISTANT
                chat_messages.append(ChatMessage(role=role, content=msg["content"]))
            
            response = self.llm.chat(chat_messages)
            return response.message.content
            
        except Exception as e:
            logger.error(f"Chat failed: {str(e)}")
            return f"Error: {str(e)}"