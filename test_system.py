#!/usr/bin/env python3
"""
Quick test to demonstrate the working agentic system
"""
import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from src.api.services import AgenticSystemService
from config.settings import settings

async def test_agentic_system():
    """Test the complete agentic workflow"""
    print("🚀 Testing Agentic Business Rules System")
    print("=" * 50)
    
    # Initialize system
    print("🔧 Initializing system...")
    service = AgenticSystemService(
        rules_directory=settings.business_rules_path,
        qdrant_host=settings.qdrant_host,
        qdrant_port=settings.qdrant_port,
        ollama_base_url=settings.ollama_base_url,
        ollama_model=settings.ollama_model
    )
    
    success = await service.initialize()
    if not success:
        print("❌ System initialization failed")
        return
    
    print("✅ System initialized successfully!")
    
    # Test scenario analysis
    print("\n🧠 Testing scenario analysis...")
    scenario = "Customer wants a $8000 loan with credit score 720"
    print(f"Scenario: {scenario}")
    
    try:
        result = await service.analyze_and_execute(scenario)
        
        print("\n📊 Analysis Results:")
        print(f"  • Rules found: {len(result['analysis']['applicable_rules'])}")
        print(f"  • Confidence: {result['analysis']['confidence']:.2f}")
        print(f"  • Decision: {result['analysis']['decision_outcome']}")
        
        if result['analysis']['applicable_rules']:
            print("\n📋 Applicable Rules:")
            for rule in result['analysis']['applicable_rules']:
                print(f"  • {rule['name']}: {rule['action']}")
        
        print(f"\n🎯 Execution Results:")
        print(f"  • Status: {result['execution']['overall_status']}")
        print(f"  • Rules executed: {result['execution']['successful_rules']}")
        
        print("\n✅ Agentic workflow completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    asyncio.run(test_agentic_system())

if __name__ == "__main__":
    main()