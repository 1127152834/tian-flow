#!/usr/bin/env python3
# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Test script for Plan validation and parsing.
This tests the fix for the Pydantic validation error.
"""

import json
from src.prompts.planner_model import Plan, Step, StepType


def test_plan_validation():
    """Test Plan model validation with different input formats."""
    
    print("🧪 Testing Plan validation...")
    
    # Test 1: Valid plan dictionary
    valid_plan_dict = {
        "locale": "zh-CN",
        "has_enough_context": False,
        "thought": "需要收集关于AI最新研究趋势与方向的信息",
        "title": "最新AI研究趋势与方向",
        "steps": [
            {
                "need_search": True,
                "title": "最新AI研究趋势与方向",
                "description": "收集关于AI最新研究成果、技术突破和应用趋势的信息，涵盖自然语言处理（NLP）、计算机视觉（CV）、强化学习（RL）、生成式AI以及AI伦理等方面的最新进展。",
                "step_type": "research"
            }
        ]
    }
    
    try:
        plan = Plan.model_validate(valid_plan_dict)
        print("✅ Test 1 passed: Valid plan dictionary validation")
        print(f"   Plan title: {plan.title}")
        print(f"   Steps count: {len(plan.steps)}")
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
        return False
    
    # Test 2: Invalid format (list instead of dict) - this should fail
    invalid_plan_list = [
        [
            {
                "need_search": True,
                "title": "最新AI研究趋势与方向",
                "description": "收集关于AI最新研究成果、技术突破和应用趋势的信息",
                "step_type": "research"
            }
        ]
    ]
    
    try:
        plan = Plan.model_validate(invalid_plan_list)
        print("❌ Test 2 failed: Should have raised validation error for list input")
        return False
    except Exception as e:
        print("✅ Test 2 passed: Correctly rejected invalid list format")
        print(f"   Error: {type(e).__name__}")
    
    # Test 3: JSON string parsing
    plan_json = json.dumps(valid_plan_dict)
    
    try:
        parsed_dict = json.loads(plan_json)
        plan = Plan.model_validate(parsed_dict)
        print("✅ Test 3 passed: JSON string parsing and validation")
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
        return False
    
    # Test 4: Plan object serialization
    try:
        plan_dict = plan.model_dump()
        plan_json = plan.model_dump_json(indent=2)
        print("✅ Test 4 passed: Plan object serialization")
        print(f"   JSON length: {len(plan_json)} characters")
    except Exception as e:
        print(f"❌ Test 4 failed: {e}")
        return False
    
    # Test 5: Step validation
    try:
        step = Step(
            need_search=True,
            title="Test Step",
            description="Test description",
            step_type=StepType.RESEARCH
        )
        print("✅ Test 5 passed: Step object creation")
        print(f"   Step type: {step.step_type}")
    except Exception as e:
        print(f"❌ Test 5 failed: {e}")
        return False
    
    return True


def test_plan_edge_cases():
    """Test edge cases for Plan validation."""
    
    print("\n🔍 Testing Plan edge cases...")
    
    # Test 1: Missing required fields
    incomplete_plan = {
        "locale": "en-US",
        "has_enough_context": True,
        # Missing 'thought' and 'title'
        "steps": []
    }
    
    try:
        plan = Plan.model_validate(incomplete_plan)
        print("❌ Edge case 1 failed: Should have raised validation error for missing fields")
        return False
    except Exception as e:
        print("✅ Edge case 1 passed: Correctly rejected incomplete plan")
        print(f"   Error type: {type(e).__name__}")
    
    # Test 2: Invalid step type
    plan_with_invalid_step = {
        "locale": "en-US",
        "has_enough_context": False,
        "thought": "Test thought",
        "title": "Test title",
        "steps": [
            {
                "need_search": True,
                "title": "Test Step",
                "description": "Test description",
                "step_type": "invalid_type"  # Invalid step type
            }
        ]
    }
    
    try:
        plan = Plan.model_validate(plan_with_invalid_step)
        print("❌ Edge case 2 failed: Should have raised validation error for invalid step type")
        return False
    except Exception as e:
        print("✅ Edge case 2 passed: Correctly rejected invalid step type")
        print(f"   Error type: {type(e).__name__}")
    
    # Test 3: Empty plan with minimal required fields
    minimal_plan = {
        "locale": "en-US",
        "has_enough_context": True,
        "thought": "Minimal plan",
        "title": "Minimal Title",
        "steps": []
    }
    
    try:
        plan = Plan.model_validate(minimal_plan)
        print("✅ Edge case 3 passed: Minimal plan validation")
        print(f"   Steps count: {len(plan.steps)}")
    except Exception as e:
        print(f"❌ Edge case 3 failed: {e}")
        return False
    
    return True


def main():
    """Run all tests."""
    print("🚀 Starting Plan validation tests...\n")
    
    test1_passed = test_plan_validation()
    test2_passed = test_plan_edge_cases()
    
    print(f"\n📊 Test Results:")
    print(f"   Basic validation tests: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   Edge case tests: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Plan validation is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the Plan model implementation.")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
