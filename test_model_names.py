#!/usr/bin/env python3
"""Test script for model-names functionality."""

import sys
sys.path.append('.')

from workbench.comparison import ComparisonConfig

def test_model_names():
    """Test the new model names functionality."""
    
    print("🧪 Testing model-names functionality...")
    
    # Test 1: Legacy model_name (should apply to all models)
    config1 = ComparisonConfig.from_csv_params(
        models_csv="claude,claude-tools",
        task_sets_csv="tasks/v3-tasks-with-ledger",
        model_name="claude-3-5-sonnet-20241022"
    )
    
    print("\n📝 Test 1: Legacy model_name")
    for model in config1.models:
        model_name = config1.get_model_name(model)
        print(f"   {model} → {model_name}")
    
    # Test 2: Per-model model_names
    config2 = ComparisonConfig.from_csv_params(
        models_csv="claude,claude-tools",
        task_sets_csv="tasks/v3-tasks-with-ledger",
        model_names={
            "claude": "claude-3-5-sonnet-20241022",
            "claude-tools": "claude-3-5-haiku-20241022"
        }
    )
    
    print("\n📝 Test 2: Per-model model_names")
    for model in config2.models:
        model_name = config2.get_model_name(model)
        print(f"   {model} → {model_name}")
    
    # Test 3: Mixed - some models have specific names, others use fallback
    config3 = ComparisonConfig.from_csv_params(
        models_csv="claude,claude-tools,stub",
        task_sets_csv="tasks/v3-tasks-with-ledger",
        model_name="claude-3-5-sonnet-20241022",  # fallback
        model_names={
            "claude-tools": "claude-3-5-haiku-20241022"  # specific override
        }
    )
    
    print("\n📝 Test 3: Mixed model names with fallback")
    for model in config3.models:
        model_name = config3.get_model_name(model)
        print(f"   {model} → {model_name or '(default)'}")
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    test_model_names()