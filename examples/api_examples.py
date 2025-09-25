"""
Simple API Client Examples

Examples of how to interact with the Agentic Business Rules API.
"""
import requests
import json
from typing import Dict, Any, Optional


class AgenticAPIClient:
    """Simple client for the Agentic Business Rules API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def analyze_scenario(
        self,
        scenario: str,
        context: Optional[Dict[str, Any]] = None,
        domain_hint: Optional[str] = None,
        category_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze a business scenario"""
        payload = {
            "scenario": scenario,
            "context": context,
            "domain_hint": domain_hint,
            "category_hint": category_hint
        }
        
        response = requests.post(f"{self.base_url}/analyze", json=payload)
        response.raise_for_status()
        return response.json()
    
    def execute_rules(
        self,
        scenario: str,
        context: Optional[Dict[str, Any]] = None,
        rules: Optional[list] = None,
        domain_hint: Optional[str] = None,
        category_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute business rules for a scenario"""
        payload = {
            "scenario": scenario,
            "context": context,
            "rules": rules,
            "domain_hint": domain_hint,
            "category_hint": category_hint
        }
        
        response = requests.post(f"{self.base_url}/execute", json=payload)
        response.raise_for_status()
        return response.json()
    
    def analyze_and_execute(
        self,
        scenario: str,
        context: Optional[Dict[str, Any]] = None,
        domain_hint: Optional[str] = None,
        category_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze and execute in one call"""
        payload = {
            "scenario": scenario,
            "context": context,
            "domain_hint": domain_hint,
            "category_hint": category_hint
        }
        
        response = requests.post(f"{self.base_url}/analyze-and-execute", json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_rules(
        self,
        domain: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get business rules"""
        params = {"limit": limit, "offset": offset}
        if domain:
            params["domain"] = domain
        if category:
            params["category"] = category
        
        response = requests.get(f"{self.base_url}/rules", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_rule(self, rule_id: str) -> Dict[str, Any]:
        """Get a specific rule"""
        response = requests.get(f"{self.base_url}/rules/{rule_id}")
        response.raise_for_status()
        return response.json()
    
    def get_history(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Get execution history"""
        params = {"limit": limit, "offset": offset}
        response = requests.get(f"{self.base_url}/history", params=params)
        response.raise_for_status()
        return response.json()
    
    def chat(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[list] = None
    ) -> Dict[str, Any]:
        """Chat with the agent"""
        payload = {
            "message": message,
            "context": context,
            "conversation_history": conversation_history
        }
        
        response = requests.post(f"{self.base_url}/chat", json=payload)
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict[str, Any]:
        """Check system health"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()


def example_loan_analysis():
    """Example: Loan application analysis"""
    print("🏦 Loan Application Analysis Example")
    print("=" * 50)
    
    client = AgenticAPIClient()
    
    # High credit score loan
    scenario = "Customer with credit score 780 and income $90,000 applying for a $30,000 personal loan"
    context = {
        "credit_score": 780,
        "annual_income": 90000,
        "loan_amount": 30000,
        "debt_to_income": 0.2,
        "employment_years": 4
    }
    
    try:
        result = client.analyze_and_execute(scenario, context, "finance", "loan_approval")
        
        print(f"📝 Scenario: {scenario}")
        print(f"🎯 Decision: {result['analysis']['decision_outcome']}")
        print(f"📊 Confidence: {result['analysis']['overall_confidence']:.2f}")
        print(f"⚡ Execution Status: {result['execution']['overall_status']}")
        
        if result['execution']['results']:
            print("🔧 Actions Performed:")
            for res in result['execution']['results']:
                if res['status'] == 'completed':
                    print(f"   ✅ {res['output'].get('action_taken', 'Unknown')}")
        
        print(f"🧠 Reasoning: {result['analysis']['reasoning'][:200]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_inventory_management():
    """Example: Inventory management"""
    print("\n📦 Inventory Management Example")
    print("=" * 50)
    
    client = AgenticAPIClient()
    
    scenario = "Medical supply inventory dropped to 25 units, minimum stock level is 200 units"
    context = {
        "product_id": "MED_SUPPLY_001",
        "current_stock": 25,
        "minimum_stock_level": 200,
        "maximum_stock_level": 1000,
        "product_category": "essential"
    }
    
    try:
        result = client.analyze_and_execute(scenario, context, "inventory")
        
        print(f"📝 Scenario: {scenario}")
        print(f"🎯 Decision: {result['analysis']['decision_outcome']}")
        print(f"⚡ Execution Status: {result['execution']['overall_status']}")
        
        if result['execution']['results']:
            print("🔧 Actions Performed:")
            for res in result['execution']['results']:
                if res['status'] == 'completed':
                    print(f"   ✅ {res['output'].get('action_taken', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_compliance_check():
    """Example: Compliance data check"""
    print("\n🔒 Compliance Check Example")
    print("=" * 50)
    
    client = AgenticAPIClient()
    
    scenario = "Employee from marketing department attempting to access financial revenue data"
    context = {
        "user_role": "marketing",
        "data_classification": "financial",
        "data_type": "revenue_report",
        "access_requested": True
    }
    
    try:
        result = client.analyze_and_execute(scenario, context, "compliance")
        
        print(f"📝 Scenario: {scenario}")
        print(f"🎯 Decision: {result['analysis']['decision_outcome']}")
        print(f"⚡ Execution Status: {result['execution']['overall_status']}")
        
        if result['execution']['results']:
            print("🔧 Actions Performed:")
            for res in result['execution']['results']:
                if res['status'] == 'completed':
                    print(f"   ✅ {res['output'].get('action_taken', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_chat_interaction():
    """Example: Chat with the agent"""
    print("\n💬 Chat Interaction Example")
    print("=" * 50)
    
    client = AgenticAPIClient()
    
    try:
        # Ask about loan rules
        response = client.chat("What are the criteria for instant loan approval?")
        print(f"🤖 Agent: {response['response']}")
        
        if response.get('suggested_actions'):
            print(f"💡 Suggestions: {', '.join(response['suggested_actions'])}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_rules_exploration():
    """Example: Explore available rules"""
    print("\n📚 Rules Exploration Example")
    print("=" * 50)
    
    client = AgenticAPIClient()
    
    try:
        # Get all finance rules
        rules = client.get_rules(domain="finance", limit=5)
        
        print(f"📋 Finance Rules ({len(rules['rules'])} shown):")
        for rule in rules['rules']:
            print(f"   • {rule['name']}: {rule['action']}")
            print(f"     Condition: {rule['condition']}")
        
        # Get system overview
        print(f"\n📊 System Overview:")
        print(f"   • Total Rules: {rules['total_count']}")
        print(f"   • Domains: {', '.join(rules['domains'])}")
        print(f"   • Categories: {', '.join(rules['categories'])}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all examples"""
    print("🎯 Agentic Business Rules API - Examples")
    print("=" * 60)
    
    # Check if API is running
    try:
        client = AgenticAPIClient()
        health = client.health_check()
        print(f"✅ API Status: {health['status']}")
    except Exception as e:
        print(f"❌ API not available: {e}")
        print("Please start the API server first: python -m src.api.main")
        return
    
    # Run examples
    example_loan_analysis()
    example_inventory_management()
    example_compliance_check()
    example_chat_interaction()
    example_rules_exploration()
    
    print(f"\n🎉 Examples completed!")
    print("💡 Try the interactive demo: python examples/demo_scenarios.py")


if __name__ == "__main__":
    main()