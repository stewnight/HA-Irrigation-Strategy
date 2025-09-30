#!/usr/bin/env python3
"""Simple test script to validate LLM integration improvements."""

import sys
import os

# Add the custom components to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components'))

def test_imports():
    """Test that all LLM modules can be imported without errors."""
    try:
        from crop_steering.llm.setup_helper import LLMSetupHelper, SetupResult
        from crop_steering.llm.client import LLMProvider, LLMConfig
        from crop_steering.llm.model_config import LLMModel, LLMCostCalculator
        print("✅ All LLM modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_model_config():
    """Test the updated model configuration."""
    try:
        from crop_steering.llm.model_config import LLMModel, LLMCostCalculator
        
        # Test that old GPT-5 models are gone
        available_models = list(LLMModel)
        model_names = [model.value for model in available_models]
        
        print(f"Available models: {model_names}")
        
        # Check for non-existent models
        if any("gpt-5" in name for name in model_names):
            print("❌ Still contains non-existent GPT-5 models")
            return False
        
        # Check for real models
        expected_models = ["gpt-4o-mini", "claude-3-haiku-20240307"]
        if not any(model in model_names for model in expected_models):
            print("❌ Missing expected real models")
            return False
        
        # Test cost calculation
        cost = LLMCostCalculator.calculate_cost(
            LLMModel.GPT4O_MINI, 
            input_tokens=1000, 
            output_tokens=200
        )
        
        if cost > 0:
            print(f"✅ Cost calculation works: ${cost:.6f}")
            return True
        else:
            print("❌ Cost calculation returned zero")
            return False
            
    except Exception as e:
        print(f"❌ Model config test failed: {e}")
        return False

def test_setup_helper():
    """Test the setup helper functionality."""
    try:
        from crop_steering.llm.setup_helper import LLMSetupHelper
        
        # Test recommended models
        # Note: Can't test actual API calls without HomeAssistant, but we can test structure
        class MockHass:
            pass
        
        helper = LLMSetupHelper(MockHass())
        recommendations = helper.get_recommended_models()
        
        if "beginner" in recommendations and "balanced" in recommendations:
            print("✅ Setup helper recommendations available")
            
            # Check for real models in recommendations
            beginner_model = recommendations["beginner"]["model"]
            if "gpt-5" not in beginner_model:
                print("✅ Recommendations use real models")
                return True
            else:
                print("❌ Recommendations still reference GPT-5")
                return False
        else:
            print("❌ Setup helper missing recommendations")
            return False
            
    except Exception as e:
        print(f"❌ Setup helper test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing LLM Integration Improvements...")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Model Config Test", test_model_config),
        ("Setup Helper Test", test_setup_helper),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
        
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! LLM integration improvements are working.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())