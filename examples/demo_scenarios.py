"""
Demo Scenarios for the Agentic Business Rules POC

This script demonstrates various business scenarios and how the agentic system
analyzes and executes appropriate business rules.
"""
import asyncio
import json
from pathlib import Path
from typing import Dict, Any
import sys
import os

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from src.api.services import AgenticSystemService


class BusinessRulesDemoRunner:
    """Demonstrates the agentic business rules system"""
    
    def __init__(self):
        self.service = None
        self.scenarios = self._create_demo_scenarios()
    
    async def initialize(self) -> bool:
        """Initialize the agentic system"""
        print("🚀 Initializing Agentic Business Rules POC...")
        
        try:
            self.service = AgenticSystemService(
                rules_directory=settings.business_rules_path,
                qdrant_host=settings.qdrant_host,
                qdrant_port=settings.qdrant_port,
                collection_name=settings.qdrant_collection_name,
                ollama_base_url=settings.ollama_base_url,
                ollama_model=settings.ollama_model,
                embedding_model=settings.ollama_embedding_model,
                confidence_threshold=settings.confidence_threshold
            )
            
            success = await self.service.initialize()
            if success:
                print("✅ System initialized successfully!")
                return True
            else:
                print("❌ Failed to initialize system")
                return False
                
        except Exception as e:
            print(f"❌ Error during initialization: {str(e)}")
            return False
    
    def _create_demo_scenarios(self) -> Dict[str, Dict[str, Any]]:
        """Create demo scenarios for different business domains"""
        return {
            "finance_loan_1": {
                "title": "High Credit Score Loan Application",
                "scenario": "A customer with credit score 780, annual income $85,000, and debt-to-income ratio 0.25 is applying for a $35,000 personal loan for home improvement",
                "context": {
                    "credit_score": 780,
                    "annual_income": 85000,
                    "debt_to_income": 0.25,
                    "loan_amount": 35000,
                    "loan_purpose": "home_improvement",
                    "employment_years": 5
                },
                "domain_hint": "finance",
                "category_hint": "loan_approval",
                "expected_outcome": "Should trigger instant approval due to excellent credit and low DTI"
            },
            
            "finance_loan_2": {
                "title": "High-Risk Loan Application",
                "scenario": "A customer with credit score 680, annual income $45,000, and debt-to-income ratio 0.45 is applying for a $75,000 business loan",
                "context": {
                    "credit_score": 680,
                    "annual_income": 45000,
                    "debt_to_income": 0.45,
                    "loan_amount": 75000,
                    "loan_purpose": "business",
                    "employment_years": 3
                },
                "domain_hint": "finance",
                "category_hint": "loan_approval",
                "expected_outcome": "Should require manual review and collateral due to high amount and DTI"
            },
            
            "inventory_1": {
                "title": "Critical Low Stock Situation",
                "scenario": "Essential medical supplies inventory has dropped to 50 units while minimum stock level is 500 units. The product category is classified as essential and high-demand",
                "context": {
                    "product_id": "MED_001",
                    "product_name": "Surgical Masks",
                    "current_stock": 50,
                    "minimum_stock_level": 500,
                    "maximum_stock_level": 2000,
                    "product_category": "essential",
                    "product_type": "medical_supply"
                },
                "domain_hint": "inventory",
                "category_hint": "stock_management",
                "expected_outcome": "Should trigger emergency reorder due to critical low stock"
            },
            
            "inventory_2": {
                "title": "Seasonal Inventory Adjustment",
                "scenario": "Holiday decorations need to be restocked during peak season. Current stock is adequate but seasonal demand requires increased quantities",
                "context": {
                    "product_id": "DEC_001", 
                    "product_name": "Holiday Decorations",
                    "current_stock": 200,
                    "minimum_stock_level": 150,
                    "maximum_stock_level": 800,
                    "product_category": "seasonal",
                    "season": "peak",
                    "normal_reorder_quantity": 100
                },
                "domain_hint": "inventory",
                "category_hint": "stock_management",
                "expected_outcome": "Should increase reorder quantity due to seasonal demand"
            },
            
            "compliance_1": {
                "title": "GDPR Data Retention Check",
                "scenario": "Personal customer data has been stored for 8 years (2920 days) in our system, exceeding the 7-year retention policy",
                "context": {
                    "data_type": "personal",
                    "data_age_days": 2920,
                    "retention_period_days": 2555,
                    "customer_id": "CUST_12345",
                    "data_categories": ["personal", "financial"]
                },
                "domain_hint": "compliance",
                "category_hint": "data_protection",
                "expected_outcome": "Should schedule data deletion due to retention policy violation"
            },
            
            "compliance_2": {
                "title": "Unauthorized Financial Data Access",
                "scenario": "A marketing team member is attempting to access financial revenue data, but their role is not authorized for this data classification",
                "context": {
                    "user_id": "USER_456",
                    "user_role": "marketing",
                    "data_classification": "financial",
                    "data_type": "revenue_report",
                    "access_requested": True
                },
                "domain_hint": "compliance", 
                "category_hint": "data_protection",
                "expected_outcome": "Should deny access due to insufficient privileges"
            },
            
            "customer_service_1": {
                "title": "VIP Customer Support Request",
                "scenario": "A VIP customer with account value $150,000 has submitted a support ticket about API integration issues",
                "context": {
                    "customer_id": "VIP_789",
                    "customer_tier": "VIP",
                    "account_value": 150000,
                    "issue_category": "technical",
                    "issue_description": "API integration problems",
                    "complexity_score": 7
                },
                "domain_hint": "customer_service",
                "category_hint": "support_routing",
                "expected_outcome": "Should route to senior agent due to VIP status"
            },
            
            "customer_service_2": {
                "title": "After-Hours Support Request",
                "scenario": "A customer submitted a support request at 2 AM local time, outside of business hours (9 AM - 5 PM)",
                "context": {
                    "customer_id": "CUST_101",
                    "customer_tier": "standard",
                    "current_time": 2,  # 2 AM
                    "business_start_time": 9,
                    "business_end_time": 17,
                    "issue_category": "general",
                    "timezone": "UTC"
                },
                "domain_hint": "customer_service",
                "category_hint": "support_routing",
                "expected_outcome": "Should route to global team for after-hours support"
            }
        }
    
    async def run_all_demos(self):
        """Run all demo scenarios"""
        if not await self.initialize():
            return
        
        print("\n" + "="*80)
        print("🎯 AGENTIC BUSINESS RULES POC - DEMO SCENARIOS")
        print("="*80)
        
        system_info = await self.service.get_system_info()
        print(f"\n📊 System Info:")
        print(f"   • Total Rules Loaded: {system_info.get('total_rules', 0)}")
        print(f"   • Domains: {', '.join(system_info.get('domains', []))}")
        print(f"   • Vector DB Status: {system_info.get('vector_db_info', {}).get('status', 'unknown')}")
        print(f"   • LLM Model: {system_info.get('embedding_model', 'unknown')}")
        
        print(f"\n🚀 Running {len(self.scenarios)} demo scenarios...\n")
        
        for i, (scenario_id, scenario_data) in enumerate(self.scenarios.items(), 1):
            print(f"\n{'='*60}")
            print(f"📋 SCENARIO {i}: {scenario_data['title']}")
            print(f"{'='*60}")
            
            await self._run_single_scenario(scenario_id, scenario_data)
            
            if i < len(self.scenarios):
                print("\n⏳ Waiting 2 seconds before next scenario...")
                await asyncio.sleep(2)
        
        print(f"\n{'='*80}")
        print("🎉 All demo scenarios completed!")
        print(f"{'='*80}")
        
        # Show execution history summary
        await self._show_execution_summary()
    
    async def _run_single_scenario(self, scenario_id: str, scenario_data: Dict[str, Any]):
        """Run a single demo scenario"""
        print(f"\n📝 Scenario: {scenario_data['scenario']}")
        print(f"🎯 Expected: {scenario_data['expected_outcome']}")
        
        try:
            # Analyze and execute the scenario
            print(f"\n🔍 Analyzing scenario...")
            result = await self.service.analyze_and_execute(
                scenario=scenario_data['scenario'],
                context=scenario_data.get('context'),
                domain_hint=scenario_data.get('domain_hint'),
                category_hint=scenario_data.get('category_hint')
            )
            
            # Display analysis results
            analysis = result['analysis']
            print(f"\n📊 Analysis Results:")
            print(f"   • Decision: {analysis['decision_outcome']}")
            print(f"   • Confidence: {analysis['confidence']:.2f}")
            print(f"   • Applicable Rules: {len(analysis['applicable_rules'])}")
            
            if analysis['applicable_rules']:
                print(f"\n📋 Rules Found:")
                for rule in analysis['applicable_rules']:
                    print(f"   • {rule['name']} (Priority: {rule['priority']}, Confidence: {rule.get('confidence', 0):.2f})")
                    print(f"     Action: {rule['action']}")
            
            # Display execution results
            execution = result['execution']
            print(f"\n⚡ Execution Results:")
            print(f"   • Status: {execution['overall_status']}")
            print(f"   • Rules Executed: {execution['successful_rules']}/{execution['total_rules']}")
            if execution.get('execution_time'):
                print(f"   • Execution Time: {execution['execution_time']:.3f}s")
            
            if execution.get('results'):
                print(f"\n🔧 Actions Performed:")
                for result_info in execution['results']:
                    if result_info['status'] == 'completed':
                        action_taken = result_info['output'].get('action_taken', 'Unknown')
                        print(f"   ✅ {result_info['rule_name']}: {action_taken}")
                    else:
                        print(f"   ❌ {result_info['rule_name']}: Failed - {result_info.get('error', 'Unknown error')}")
            
            # Display reasoning
            print(f"\n🧠 Agent Reasoning:")
            reasoning_lines = analysis['reasoning'].split('\n')
            for line in reasoning_lines[:3]:  # Show first 3 lines
                if line.strip():
                    print(f"   {line.strip()}")
            if len(reasoning_lines) > 3:
                print(f"   ...")
                
        except Exception as e:
            print(f"❌ Error running scenario: {str(e)}")
    
    async def _show_execution_summary(self):
        """Show summary of all executions"""
        try:
            history = await self.service.get_execution_history(limit=100)
            
            if not history:
                print("\n📊 No execution history available")
                return
            
            print(f"\n📊 EXECUTION SUMMARY:")
            print(f"   • Total Executions: {len(history)}")
            
            successful = sum(1 for h in history if h['overall_status'] == 'completed')
            failed = sum(1 for h in history if h['overall_status'] == 'failed')
            
            print(f"   • Successful: {successful}")
            print(f"   • Failed: {failed}")
            
            total_rules = sum(h['total_rules'] for h in history)
            total_successful_rules = sum(h['successful_rules'] for h in history)
            
            if total_rules > 0:
                success_rate = (total_successful_rules / total_rules) * 100
                print(f"   • Rule Success Rate: {success_rate:.1f}%")
            
            avg_time = sum(h.get('execution_time', 0) for h in history if h.get('execution_time')) / len(history)
            print(f"   • Average Execution Time: {avg_time:.3f}s")
            
        except Exception as e:
            print(f"❌ Error showing execution summary: {str(e)}")
    
    async def run_interactive_demo(self):
        """Run interactive demo where user can input scenarios"""
        if not await self.initialize():
            return
        
        print("\n" + "="*80)
        print("🎯 INTERACTIVE AGENTIC BUSINESS RULES DEMO")
        print("="*80)
        print("Enter your business scenarios and see how the agent analyzes them!")
        print("Type 'quit' to exit, 'list' to see available domains, or 'help' for commands")
        
        while True:
            print("\n" + "-"*60)
            user_input = input("📝 Enter a business scenario: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            elif user_input.lower() == 'list':
                await self._show_available_domains()
                continue
            elif user_input.lower() == 'help':
                self._show_help()
                continue
            elif not user_input:
                continue
            
            # Get optional context
            print("💡 You can provide additional context (or press Enter to skip):")
            context_input = input("📊 Context (JSON format): ").strip()
            context = {}
            if context_input:
                try:
                    context = json.loads(context_input)
                except json.JSONDecodeError:
                    print("⚠️ Invalid JSON format, proceeding without context")
            
            # Analyze scenario
            try:
                print("\n🔍 Analyzing scenario...")
                result = await self.service.analyze_and_execute(
                    scenario=user_input,
                    context=context if context else None
                )
                
                self._display_interactive_result(result)
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    async def _show_available_domains(self):
        """Show available domains and categories"""
        try:
            system_info = await self.service.get_system_info()
            print("\n📚 Available Domains:")
            for domain in system_info.get('domains', []):
                print(f"   • {domain}")
            
            print("\n🏷️ Available Categories:")
            for category in system_info.get('categories', []):
                print(f"   • {category}")
                
        except Exception as e:
            print(f"❌ Error getting domains: {str(e)}")
    
    def _show_help(self):
        """Show help information"""
        print("\n📖 HELP:")
        print("Commands:")
        print("   • 'list' - Show available domains and categories")
        print("   • 'help' - Show this help message")
        print("   • 'quit' - Exit the demo")
        print("\nExample scenarios:")
        print("   • 'Customer with credit score 750 applying for $25000 loan'")
        print("   • 'Inventory of surgical masks dropped to 10 units, minimum is 100'")
        print("   • 'VIP customer needs technical support for API integration'")
        print("   • 'Employee trying to access financial data without authorization'")
    
    def _display_interactive_result(self, result: Dict[str, Any]):
        """Display results from interactive analysis"""
        analysis = result['analysis']
        execution = result['execution']
        
        print(f"\n🎯 RESULTS:")
        print(f"Decision: {analysis['decision_outcome']}")
        print(f"Confidence: {analysis['confidence']:.2f}")
        
        if analysis['applicable_rules']:
            print(f"\n📋 Rules Applied ({len(analysis['applicable_rules'])}):")
            for rule in analysis['applicable_rules']:
                print(f"   • {rule['name']} - {rule['action']}")
        else:
            print("\n📋 No applicable rules found")
        
        if execution['results']:
            print(f"\n⚡ Actions Performed:")
            for result_info in execution['results']:
                if result_info['status'] == 'completed':
                    action = result_info['output'].get('action_taken', 'Action completed')
                    print(f"   ✅ {action}")
        
        print(f"\n🧠 Reasoning: {analysis['reasoning'][:200]}...")


async def main():
    """Main function to run demos"""
    demo = BusinessRulesDemoRunner()
    
    print("🎯 Agentic Business Rules POC - Demo Runner")
    print("\nChoose demo mode:")
    print("1. Run all predefined scenarios")
    print("2. Interactive demo (enter your own scenarios)")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == "1":
        await demo.run_all_demos()
    elif choice == "2":
        await demo.run_interactive_demo()
    else:
        print("Invalid choice. Running all demos...")
        await demo.run_all_demos()


if __name__ == "__main__":
    asyncio.run(main())