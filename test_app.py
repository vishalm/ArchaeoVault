#!/usr/bin/env python3
"""
Simple test script to verify ArchaeoVault application structure.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path (not the app directory)
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_structure():
    """Test that the basic directory structure exists."""
    print("🔍 Checking directory structure...")
    
    required_dirs = [
        "app",
        "app/models",
        "app/services",
        "app/services/ai_agents",
        "app/utils",
        "app/components",
    ]
    
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ❌ {dir_path} - NOT FOUND")
            return False
    
    return True

def test_imports():
    """Test that key modules can be imported."""
    print("\n🔍 Testing imports...")
    
    modules_to_test = [
        "app.config",
        "app.models.artifact",
        "app.models.civilization",
        "app.models.user",
        "app.services.database",
        "app.utils.logging",
    ]
    
    failed = []
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name}")
        except ImportError as e:
            print(f"  ❌ {module_name} - {str(e)[:50]}")
            failed.append(module_name)
        except Exception as e:
            print(f"  ⚠️  {module_name} - {str(e)[:50]}")
            failed.append(module_name)
    
    return len(failed) == 0

def test_config():
    """Test configuration loading."""
    print("\n🔍 Testing configuration...")
    
    try:
        from app.config import get_settings
        settings = get_settings()
        print(f"  ✅ Settings loaded")
        
        # Try to print app name if it exists
        if hasattr(settings, 'APP_NAME'):
            print(f"  ℹ️  App name: {settings.APP_NAME}")
        elif hasattr(settings, 'app_name'):
            print(f"  ℹ️  App name: {settings.app_name}")
        
        return True
    except Exception as e:
        print(f"  ❌ Config error: {e}")
        return False

def test_models():
    """Test that models can be instantiated."""
    print("\n🔍 Testing models...")
    
    try:
        from app.models.artifact import Artifact
        
        # Use valid enum values based on model requirements
        test_data = {
            "name": "Test Artifact",
            "period": "bronze_age",
            "culture": "Minoan",
            "material": "ceramic",
            "condition": "good"
        }
        
        try:
            artifact = Artifact(data=test_data)
            print(f"  ✅ Created artifact successfully")
            
            # artifact.data is an object, not a dict
            if hasattr(artifact, 'data') and hasattr(artifact.data, 'name'):
                print(f"  ℹ️  Artifact: {artifact.data.name}")
            elif hasattr(artifact, 'name'):
                print(f"  ℹ️  Artifact: {artifact.name}")
            else:
                print(f"  ℹ️  Artifact created (structure: {type(artifact.data)})")
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            print(f"  ⚠️  Validation error: {error_msg[:300]}")
            print(f"  💡 Check model field requirements")
            return False
        
    except Exception as e:
        print(f"  ❌ Model import/test error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing ArchaeoVault Application")
    print("=" * 60)
    
    tests = [
        ("Structure Check", test_structure),
        ("Import Test", test_imports),
        ("Config Test", test_config),
        ("Model Test", test_models),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed!")
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())