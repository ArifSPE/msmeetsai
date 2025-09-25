"""
Business Rule Execution Engine

This module provides the execution engine for business rules determined by the agent.
It handles validation, execution, logging, and result tracking.
"""
from typing import List, Dict, Any, Optional, Callable
import logging
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
import traceback
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Status of rule execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ExecutionResult:
    """Result of executing a single rule"""
    rule_id: str
    rule_name: str
    status: ExecutionStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    output: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    execution_logs: List[str] = field(default_factory=list)
    
    @property
    def duration(self) -> Optional[float]:
        """Get execution duration in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


@dataclass
class ExecutionPlan:
    """Plan for executing multiple rules"""
    plan_id: str
    scenario: str
    rules: List[Dict[str, Any]]
    context: Dict[str, Any]
    execution_results: List[ExecutionResult] = field(default_factory=list)
    overall_status: ExecutionStatus = ExecutionStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class ActionExecutor(ABC):
    """Abstract base class for action executors"""
    
    @abstractmethod
    def execute(self, action: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action with given parameters and context"""
        pass
    
    @abstractmethod
    def validate_parameters(self, action: str, parameters: Dict[str, Any]) -> bool:
        """Validate if parameters are correct for the action"""
        pass


class DefaultActionExecutor(ActionExecutor):
    """Default implementation of action executor with common business actions"""
    
    def __init__(self):
        self.supported_actions = {
            # Finance actions
            "approve_basic_review": self._approve_basic_review,
            "require_manual_review": self._require_manual_review,
            "instant_approve": self._instant_approve,
            "require_collateral": self._require_collateral,
            "deny_access": self._deny_access,
            
            # Inventory actions
            "generate_low_stock_alert": self._generate_low_stock_alert,
            "emergency_reorder": self._emergency_reorder,
            "block_reorder": self._block_reorder,
            "increase_reorder_quantity": self._increase_reorder_quantity,
            "mark_for_clearance": self._mark_for_clearance,
            
            # Compliance actions
            "schedule_data_deletion": self._schedule_data_deletion,
            "request_consent_renewal": self._request_consent_renewal,
            "execute_data_deletion": self._execute_data_deletion,
            "enforce_encryption": self._enforce_encryption,
            
            # Customer service actions
            "route_to_senior_agent": self._route_to_senior_agent,
            "escalate_to_technical_team": self._escalate_to_technical_team,
            "route_to_global_team": self._route_to_global_team,
            "route_to_billing_specialist": self._route_to_billing_specialist,
        }
    
    def execute(self, action: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the specified action"""
        if action not in self.supported_actions:
            return {
                "success": False,
                "error": f"Unsupported action: {action}",
                "supported_actions": list(self.supported_actions.keys())
            }
        
        try:
            return self.supported_actions[action](parameters, context)
        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing {action}: {str(e)}",
                "traceback": traceback.format_exc()
            }
    
    def validate_parameters(self, action: str, parameters: Dict[str, Any]) -> bool:
        """Validate parameters for the action"""
        # Basic validation - can be extended for each action type
        return isinstance(parameters, dict)
    
    # Finance action implementations
    def _approve_basic_review(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Approve loan for basic review"""
        return {
            "success": True,
            "action_taken": "loan_approved_for_basic_review",
            "next_steps": ["Basic underwriting review", "Document verification"],
            "approval_level": "basic",
            "timestamp": datetime.now().isoformat()
        }
    
    def _require_manual_review(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Require manual review for high-risk cases"""
        return {
            "success": True,
            "action_taken": "manual_review_required",
            "assigned_to": "senior_underwriter",
            "priority": "high",
            "review_criteria": parameters,
            "timestamp": datetime.now().isoformat()
        }
    
    def _instant_approve(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Instantly approve loan"""
        return {
            "success": True,
            "action_taken": "instant_approval",
            "approval_amount": context.get("loan_amount", 0),
            "approval_rate": context.get("interest_rate", "TBD"),
            "timestamp": datetime.now().isoformat()
        }
    
    def _require_collateral(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Require collateral for loan"""
        return {
            "success": True,
            "action_taken": "collateral_required",
            "collateral_percentage": 80,  # Default 80% LTV
            "acceptable_collateral_types": ["real_estate", "securities", "cash_deposit"],
            "timestamp": datetime.now().isoformat()
        }
    
    def _deny_access(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Deny access to financial data"""
        return {
            "success": True,
            "action_taken": "access_denied",
            "reason": "Insufficient privileges for financial data access",
            "required_roles": parameters.get("authorized_roles", []),
            "timestamp": datetime.now().isoformat()
        }
    
    # Inventory action implementations
    def _generate_low_stock_alert(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate low stock alert"""
        return {
            "success": True,
            "action_taken": "low_stock_alert_generated",
            "alert_sent_to": ["inventory_manager", "procurement_team"],
            "current_stock": context.get("current_stock", 0),
            "minimum_stock": context.get("minimum_stock_level", 0),
            "timestamp": datetime.now().isoformat()
        }
    
    def _emergency_reorder(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute emergency reorder"""
        reorder_quantity = context.get("minimum_stock_level", 100) * 2  # Default 2x minimum
        return {
            "success": True,
            "action_taken": "emergency_reorder_initiated",
            "reorder_quantity": reorder_quantity,
            "supplier": "primary_supplier",
            "expected_delivery": "24-48 hours",
            "timestamp": datetime.now().isoformat()
        }
    
    def _block_reorder(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Block reorder due to overstock"""
        return {
            "success": True,
            "action_taken": "reorder_blocked",
            "reason": "Current stock exceeds maximum threshold",
            "current_stock": context.get("current_stock", 0),
            "maximum_stock": context.get("maximum_stock_level", 0),
            "timestamp": datetime.now().isoformat()
        }
    
    def _increase_reorder_quantity(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Increase reorder quantity for seasonal demand"""
        base_quantity = context.get("normal_reorder_quantity", 100)
        multiplier = parameters.get("seasonal_multiplier", 1.5)
        new_quantity = int(base_quantity * multiplier)
        
        return {
            "success": True,
            "action_taken": "reorder_quantity_increased",
            "original_quantity": base_quantity,
            "new_quantity": new_quantity,
            "multiplier": multiplier,
            "reason": "Seasonal demand adjustment",
            "timestamp": datetime.now().isoformat()
        }
    
    def _mark_for_clearance(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Mark products for clearance sale"""
        return {
            "success": True,
            "action_taken": "marked_for_clearance",
            "clearance_discount": "50%",
            "expiry_date": context.get("expiry_date"),
            "notification_sent": "sales_team",
            "timestamp": datetime.now().isoformat()
        }
    
    # Compliance action implementations
    def _schedule_data_deletion(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule data deletion per retention policy"""
        return {
            "success": True,
            "action_taken": "data_deletion_scheduled",
            "scheduled_date": "30 days from now",  # Grace period
            "data_categories": context.get("data_type", "personal"),
            "compliance_regulation": "GDPR",
            "timestamp": datetime.now().isoformat()
        }
    
    def _request_consent_renewal(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Request consent renewal from user"""
        return {
            "success": True,
            "action_taken": "consent_renewal_requested",
            "notification_sent": context.get("user_email", "user"),
            "consent_type": "data_processing",
            "deadline": "30 days",
            "timestamp": datetime.now().isoformat()
        }
    
    def _execute_data_deletion(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data deletion request"""
        return {
            "success": True,
            "action_taken": "data_deleted",
            "deletion_scope": "all_personal_data",
            "verification_required": True,
            "compliance_log_updated": True,
            "timestamp": datetime.now().isoformat()
        }
    
    def _enforce_encryption(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Enforce encryption on payment data"""
        return {
            "success": True,
            "action_taken": "encryption_enforced",
            "encryption_standard": parameters.get("required_encryption_standard", "AES256"),
            "data_encrypted": True,
            "compliance_status": "PCI-DSS compliant",
            "timestamp": datetime.now().isoformat()
        }
    
    # Customer service action implementations
    def _route_to_senior_agent(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Route to senior support agent"""
        return {
            "success": True,
            "action_taken": "routed_to_senior_agent",
            "agent_type": "senior_support",
            "priority": "high",
            "customer_tier": context.get("customer_tier", "VIP"),
            "timestamp": datetime.now().isoformat()
        }
    
    def _escalate_to_technical_team(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Escalate to technical support team"""
        return {
            "success": True,
            "action_taken": "escalated_to_technical_team",
            "team": "technical_support",
            "complexity_score": context.get("complexity_score", 8),
            "issue_category": "technical",
            "timestamp": datetime.now().isoformat()
        }
    
    def _route_to_global_team(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Route to global support team for after-hours"""
        return {
            "success": True,
            "action_taken": "routed_to_global_team",
            "team_location": "asia_pacific",
            "reason": "after_hours_support",
            "local_time": datetime.now().isoformat(),
            "timestamp": datetime.now().isoformat()
        }
    
    def _route_to_billing_specialist(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Route billing dispute to specialist"""
        return {
            "success": True,
            "action_taken": "routed_to_billing_specialist",
            "specialist_team": "billing_disputes",
            "dispute_amount": context.get("dispute_amount", 0),
            "priority": "high" if context.get("dispute_amount", 0) > 1000 else "normal",
            "timestamp": datetime.now().isoformat()
        }


class BusinessRuleExecutionEngine:
    """Engine for executing business rules determined by the agent"""
    
    def __init__(self, action_executor: Optional[ActionExecutor] = None):
        self.action_executor = action_executor or DefaultActionExecutor()
        self.execution_history: List[ExecutionPlan] = []
        
    def create_execution_plan(
        self,
        scenario: str,
        rules: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> ExecutionPlan:
        """Create an execution plan for the given rules"""
        plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.execution_history)}"
        
        return ExecutionPlan(
            plan_id=plan_id,
            scenario=scenario,
            rules=rules,
            context=context
        )
    
    def execute_plan(self, plan: ExecutionPlan) -> ExecutionPlan:
        """Execute the business rules according to the plan"""
        logger.info(f"Starting execution of plan {plan.plan_id} with {len(plan.rules)} rules")
        
        plan.start_time = datetime.now()
        plan.overall_status = ExecutionStatus.RUNNING
        
        try:
            # Execute rules in order
            for rule in plan.rules:
                result = self._execute_single_rule(rule, plan.context)
                plan.execution_results.append(result)
                
                # If a critical rule fails, consider stopping
                if result.status == ExecutionStatus.FAILED and rule.get("priority", 1) >= 3:
                    logger.warning(f"Critical rule {rule['id']} failed, continuing with remaining rules")
            
            # Determine overall status
            failed_results = [r for r in plan.execution_results if r.status == ExecutionStatus.FAILED]
            if failed_results:
                critical_failures = [r for r in failed_results if any(
                    rule["priority"] >= 3 for rule in plan.rules if rule["id"] == r.rule_id
                )]
                if critical_failures:
                    plan.overall_status = ExecutionStatus.FAILED
                else:
                    plan.overall_status = ExecutionStatus.COMPLETED  # Partial success
            else:
                plan.overall_status = ExecutionStatus.COMPLETED
                
        except Exception as e:
            logger.error(f"Error executing plan {plan.plan_id}: {str(e)}")
            plan.overall_status = ExecutionStatus.FAILED
            
        finally:
            plan.end_time = datetime.now()
            self.execution_history.append(plan)
        
        logger.info(f"Completed execution of plan {plan.plan_id}. Status: {plan.overall_status}")
        return plan
    
    def _execute_single_rule(self, rule: Dict[str, Any], context: Dict[str, Any]) -> ExecutionResult:
        """Execute a single business rule"""
        result = ExecutionResult(
            rule_id=rule["id"],
            rule_name=rule["name"],
            status=ExecutionStatus.RUNNING,
            start_time=datetime.now()
        )
        
        try:
            # Validate parameters
            if not self.action_executor.validate_parameters(rule["action"], rule.get("parameters", {})):
                result.status = ExecutionStatus.FAILED
                result.error_message = "Parameter validation failed"
                return result
            
            # Log execution start
            result.execution_logs.append(f"Starting execution of rule {rule['id']}: {rule['name']}")
            
            # Execute the action
            execution_output = self.action_executor.execute(
                action=rule["action"],
                parameters=rule.get("parameters", {}),
                context=context
            )
            
            result.output = execution_output
            
            if execution_output.get("success", False):
                result.status = ExecutionStatus.COMPLETED
                result.execution_logs.append(f"Rule executed successfully: {execution_output.get('action_taken', 'Unknown')}")
            else:
                result.status = ExecutionStatus.FAILED
                result.error_message = execution_output.get("error", "Unknown error")
                result.execution_logs.append(f"Rule execution failed: {result.error_message}")
                
        except Exception as e:
            result.status = ExecutionStatus.FAILED
            result.error_message = str(e)
            result.execution_logs.append(f"Exception during execution: {str(e)}")
            logger.error(f"Error executing rule {rule['id']}: {str(e)}")
            
        finally:
            result.end_time = datetime.now()
        
        return result
    
    def get_execution_summary(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """Get summary of execution results"""
        successful_rules = [r for r in plan.execution_results if r.status == ExecutionStatus.COMPLETED]
        failed_rules = [r for r in plan.execution_results if r.status == ExecutionStatus.FAILED]
        
        return {
            "plan_id": plan.plan_id,
            "scenario": plan.scenario,
            "overall_status": plan.overall_status.value,
            "total_rules": len(plan.rules),
            "successful_rules": len(successful_rules),
            "failed_rules": len(failed_rules),
            "execution_time": (plan.end_time - plan.start_time).total_seconds() if plan.end_time and plan.start_time else None,
            "results": [
                {
                    "rule_id": result.rule_id,
                    "rule_name": result.rule_name,
                    "status": result.status.value,
                    "duration": result.duration,
                    "output": result.output,
                    "error": result.error_message
                }
                for result in plan.execution_results
            ]
        }
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get summary of all execution history"""
        return [self.get_execution_summary(plan) for plan in self.execution_history]