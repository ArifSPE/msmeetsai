"""
Test suite for the Agentic Business Rules POC

This module provides comprehensive tests for the core components.
"""
import asyncio
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Test configuration
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.business_rules.manager import BusinessRulesManager, BusinessRule
from src.rag.embeddings import EmbeddingsService
from src.agents.business_rule_agent import BusinessRuleAgent
from src.execution.engine import BusinessRuleExecutionEngine


class TestBusinessRulesManager:
    """Test the BusinessRulesManager component"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.rules_dir = Path(self.temp_dir)
        
        # Create test rule file
        test_rule = """
finance:
  loan_approval:
    - id: "test_rule_1"
      name: "Basic Loan Approval"
      description: "Approve loans under $10,000 with credit score > 700"
      conditions:
        - "loan_amount < 10000"
        - "credit_score > 700"
      actions:
        - "approve_loan"
      priority: "high"
      active: true
"""
        (self.rules_dir / "test_rules.yaml").write_text(test_rule)
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_load_rules(self):
        """Test loading rules from YAML files"""
        manager = BusinessRulesManager(str(self.rules_dir))
        manager.load_rules()
        
        assert len(manager.rules) == 1
        rule = manager.rules[0]
        assert rule.id == "test_rule_1"
        assert rule.name == "Basic Loan Approval"
        assert "finance" in rule.domain
        assert "loan_approval" in rule.category
    
    def test_get_rules_by_domain(self):
        """Test filtering rules by domain"""
        manager = BusinessRulesManager(str(self.rules_dir))
        manager.load_rules()
        
        finance_rules = manager.get_rules_by_domain("finance")
        assert len(finance_rules) == 1
        
        inventory_rules = manager.get_rules_by_domain("inventory")
        assert len(inventory_rules) == 0
    
    def test_rule_to_text(self):
        """Test converting rule to text format"""
        manager = BusinessRulesManager(str(self.rules_dir))
        manager.load_rules()
        
        rule = manager.rules[0]
        text = manager.rule_to_text(rule)
        
        assert "Basic Loan Approval" in text
        assert "loan_amount < 10000" in text
        assert "approve_loan" in text


class TestEmbeddingsService:
    """Test the EmbeddingsService component"""
    
    @pytest.mark.asyncio
    async def test_generate_embeddings(self):
        """Test generating embeddings for text"""
        service = EmbeddingsService()
        
        with patch.object(service, 'embeddings_model') as mock_model:
            mock_model.get_text_embedding = AsyncMock(return_value=[0.1, 0.2, 0.3])
            
            embedding = await service.generate_embeddings("test text")
            assert embedding == [0.1, 0.2, 0.3]
            mock_model.get_text_embedding.assert_called_once_with("test text")
    
    @pytest.mark.asyncio
    async def test_batch_generate_embeddings(self):
        """Test generating embeddings for multiple texts"""
        service = EmbeddingsService()
        
        with patch.object(service, 'embeddings_model') as mock_model:
            mock_model.get_text_embedding = AsyncMock(
                side_effect=[[0.1, 0.2], [0.3, 0.4]]
            )
            
            embeddings = await service.batch_generate_embeddings(["text1", "text2"])
            assert len(embeddings) == 2
            assert embeddings[0] == [0.1, 0.2]
            assert embeddings[1] == [0.3, 0.4]


class TestBusinessRuleAgent:
    """Test the BusinessRuleAgent component"""
    
    def setup_method(self):
        """Set up test environment"""
        self.mock_rag = Mock()
        self.mock_llm = Mock()
        self.agent = BusinessRuleAgent(self.mock_rag, self.mock_llm)
    
    @pytest.mark.asyncio
    async def test_analyze_scenario(self):
        """Test scenario analysis"""
        # Mock RAG response
        mock_rule = BusinessRule(
            id="test_rule",
            name="Test Rule",
            description="Test description",
            conditions=["test_condition"],
            actions=["test_action"],
            domain="finance",
            category="loan",
            priority="high",
            active=True
        )
        
        self.mock_rag.query_rules = AsyncMock(return_value=[mock_rule])
        self.mock_llm.generate_response = AsyncMock(
            return_value="The rule should be applied based on the scenario."
        )
        
        scenario = "Customer wants a $5000 loan with credit score 750"
        result = await self.agent.analyze_scenario(scenario)
        
        assert result is not None
        assert "scenario" in result
        assert "rules_found" in result
        assert "analysis" in result
        assert len(result["rules_found"]) == 1


class TestExecutionEngine:
    """Test the BusinessRuleExecutionEngine component"""
    
    def setup_method(self):
        """Set up test environment"""
        self.engine = BusinessRuleExecutionEngine()
    
    @pytest.mark.asyncio
    async def test_execute_plan(self):
        """Test executing a business rule plan"""
        plan = {
            "actions": [
                {
                    "type": "log_info",
                    "parameters": {"message": "Test execution"}
                }
            ]
        }
        
        result = await self.engine.execute_plan(plan)
        
        assert result["success"] is True
        assert len(result["results"]) == 1
        assert result["results"][0]["success"] is True
    
    @pytest.mark.asyncio
    async def test_execute_unknown_action(self):
        """Test executing unknown action type"""
        plan = {
            "actions": [
                {
                    "type": "unknown_action",
                    "parameters": {}
                }
            ]
        }
        
        result = await self.engine.execute_plan(plan)
        
        assert result["success"] is True
        assert len(result["results"]) == 1
        assert result["results"][0]["success"] is False
        assert "Unknown action type" in result["results"][0]["error"]


class TestIntegration:
    """Integration tests for the complete system"""
    
    def setup_method(self):
        """Set up integration test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.rules_dir = Path(self.temp_dir)
        
        # Create comprehensive test rules
        test_rules = """
finance:
  loan_approval:
    - id: "integration_test_1"
      name: "Integration Test Loan"
      description: "Test loan approval for integration"
      conditions:
        - "loan_amount < 5000"
        - "credit_score > 650"
      actions:
        - "approve_loan"
      priority: "high"
      active: true

inventory:
  stock_management:
    - id: "integration_test_2"
      name: "Integration Test Stock"
      description: "Test stock reorder for integration"
      conditions:
        - "current_stock < minimum_stock"
      actions:
        - "reorder_product"
      priority: "medium"
      active: true
"""
        (self.rules_dir / "integration_test.yaml").write_text(test_rules)
    
    def teardown_method(self):
        """Clean up integration test environment"""
        shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        # This would require mocking external services
        # In a real implementation, this would test the complete flow:
        # 1. Load business rules
        # 2. Initialize RAG system
        # 3. Process scenario through agent
        # 4. Execute determined actions
        
        manager = BusinessRulesManager(str(self.rules_dir))
        manager.load_rules()
        
        assert len(manager.rules) == 2
        
        # Test rule retrieval
        finance_rules = manager.get_rules_by_domain("finance")
        inventory_rules = manager.get_rules_by_domain("inventory")
        
        assert len(finance_rules) == 1
        assert len(inventory_rules) == 1


# Test utilities
def run_tests():
    """Run all tests"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    run_tests()