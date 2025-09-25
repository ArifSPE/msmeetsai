#!/usr/bin/env python3
"""Debug script to test API analyze endpoint issue"""

import asyncio
import json
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

from src.api.services import AgenticSystemService
from src.api.models import AnalysisRequest

async def debug_analyze():
    """Debug the analyze functionality step by step"""
    
    print("🔍 Setting up AgenticSystemService...")
    service = AgenticSystemService(
        rules_directory=Path('./data/business_rules'),
        ollama_model='llama3:latest'
    )
    
    print("🔄 Initializing service...")
    success = await service.initialize()
    if not success:
        print("❌ Service initialization failed")
        return
        
    print("✅ Service initialized successfully")
    
    # Create test request
    print("🧪 Testing analyze_scenario...")
    try:
        result = await service.analyze_scenario(
            scenario="Customer wants a $5000 loan with credit score 680",
            context={"loan_amount": 5000, "credit_score": 680}
        )
        
        print(f"✅ Analysis successful!")
        print(f"📊 Result type: {type(result)}")
        print(f"🔑 Result keys: {list(result.keys())}")
        print(f"📝 Scenario: {result['scenario']}")
        print(f"📏 Applicable rules count: {len(result['applicable_rules'])}")
        print(f"🎯 Decision outcome: {result['decision_outcome']}")
        print(f"📊 Confidence: {result['confidence']}")
        
        # Test the API model creation manually
        from src.api.models import AnalysisResponse, RuleInfo
        
        print("🏗️ Testing API model creation...")
        
        try:
            response = AnalysisResponse(
                scenario=result["scenario"],
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
                    for rule in result["applicable_rules"]
                ],
                decision_outcome=result["decision_outcome"],
                overall_confidence=result["confidence"],
                reasoning=result["reasoning"],
                execution_plan=result["execution_plan"],
                metadata=result["metadata"]
            )
            print("✅ API model creation successful!")
            print(f"📄 Response scenario: {response.scenario}")
            
        except Exception as e:
            print(f"❌ API model creation failed: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_analyze())