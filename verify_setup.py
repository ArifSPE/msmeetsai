#!/usr/bin/env python3
"""
Import verification script

Tests that all core modules can be imported successfully.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def test_imports():
    """Test importing all core modules"""
    print("🔍 Testing core module imports...")
    
    try:
        print("  → Config...")
        from config.settings import settings
        print("  ✅ Config imported successfully")
        
        print("  → Business Rules...")
        from src.business_rules import BusinessRulesManager, BusinessRule
        print("  ✅ Business Rules imported successfully")
        
        print("  → RAG Services...")
        from src.rag import BusinessRulesRAG, EmbeddingsService, QdrantRAG
        print("  ✅ RAG Services imported successfully")
        
        print("  → Agents...")
        from src.agents import BusinessRuleAgent, LocalLLMService
        print("  ✅ Agents imported successfully")
        
        print("  → Execution Engine...")
        from src.execution import BusinessRuleExecutionEngine
        print("  ✅ Execution Engine imported successfully")
        
        print("  → API...")
        from src.api.main import app
        from src.api.services import AgenticSystemService
        print("  ✅ API imported successfully")
        
        print("\n🎉 All core modules imported successfully!")
        print("\n📊 Configuration Summary:")
        print(f"  - Qdrant: {settings.qdrant_host}:{settings.qdrant_port}")
        print(f"  - Ollama: {settings.ollama_base_url}")
        print(f"  - API: {settings.api_host}:{settings.api_port}")
        print(f"  - Business Rules: {settings.business_rules_path}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Import failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🚀 Agentic POC - Import Verification")
    print("=" * 50)
    
    success = test_imports()
    
    if success:
        print("\n✅ System ready! You can now:")
        print("  1. Run demos: python run.py --mode demo")
        print("  2. Start API: python run.py --mode api")
        print("  3. Interactive mode: python run.py --mode interactive")
        print("\n💡 Tip: Make sure Qdrant and Ollama are running first!")
        sys.exit(0)
    else:
        print("\n❌ Some imports failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()