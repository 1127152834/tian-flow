#!/usr/bin/env python3
# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Test script for planner fallback functionality.
This tests the create_fallback_plan function.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.graph.nodes import create_fallback_plan
from src.prompts.planner_model import Plan


def test_fallback_plan_creation():
    """Test the create_fallback_plan function with various inputs."""
    
    print("🧪 Testing fallback plan creation...")
    
    # Test 1: Basic state with research topic
    state1 = {
        "research_topic": "AI研究趋势",
        "locale": "zh-CN"
    }
    
    response1 = "Some invalid response that can't be parsed"
    
    try:
        fallback_plan = create_fallback_plan(state1, response1)
        plan = Plan.model_validate(fallback_plan)
        print("✅ Test 1 passed: Basic fallback plan creation")
        print(f"   Title: {plan.title}")
        print(f"   Locale: {plan.locale}")
        print(f"   Steps count: {len(plan.steps)}")
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
        return False
    
    # Test 2: State with research-related content
    state2 = {
        "research_topic": "Machine Learning Trends",
        "locale": "en-US"
    }
    
    response2 = "Need to research and search for information about machine learning"
    
    try:
        fallback_plan = create_fallback_plan(state2, response2)
        plan = Plan.model_validate(fallback_plan)
        print("✅ Test 2 passed: Research-related content detection")
        print(f"   Title: {plan.title}")
        print(f"   First step: {plan.steps[0].title}")
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
        return False
    
    # Test 3: Empty state
    state3 = {}
    response3 = ""
    
    try:
        fallback_plan = create_fallback_plan(state3, response3)
        plan = Plan.model_validate(fallback_plan)
        print("✅ Test 3 passed: Empty state handling")
        print(f"   Title: {plan.title}")
        print(f"   Locale: {plan.locale}")
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
        return False
    
    # Test 4: Complex invalid response (like the error case)
    state4 = {
        "research_topic": "最近AI研究的热点",
        "locale": "zh-CN"
    }
    
    response4 = """[[true], "最近AI研究的热点", "最近的AI研究动态", "最近AI研究的热点事件", 
    [["http://ainews.com/latest", "http://ai研究动态.com"]], "url", "search", "web search"]"""
    
    try:
        fallback_plan = create_fallback_plan(state4, response4)
        plan = Plan.model_validate(fallback_plan)
        print("✅ Test 4 passed: Complex invalid response handling")
        print(f"   Title: {plan.title}")
        print(f"   Has enough context: {plan.has_enough_context}")
    except Exception as e:
        print(f"❌ Test 4 failed: {e}")
        return False
    
    return True


def test_plan_validation_edge_cases():
    """Test edge cases for plan validation."""
    
    print("\n🔍 Testing plan validation edge cases...")
    
    # Test 1: Plan with Chinese content
    chinese_plan = {
        "locale": "zh-CN",
        "has_enough_context": False,
        "thought": "需要研究AI的最新发展",
        "title": "AI研究趋势分析",
        "steps": [
            {
                "need_search": True,
                "title": "AI技术发展调研",
                "description": "收集AI领域的最新技术发展信息",
                "step_type": "research"
            }
        ]
    }
    
    try:
        plan = Plan.model_validate(chinese_plan)
        print("✅ Edge case 1 passed: Chinese content validation")
        print(f"   Title: {plan.title}")
    except Exception as e:
        print(f"❌ Edge case 1 failed: {e}")
        return False
    
    # Test 2: Plan with multiple steps
    multi_step_plan = {
        "locale": "en-US",
        "has_enough_context": False,
        "thought": "Need comprehensive research on AI trends",
        "title": "AI Trends Research",
        "steps": [
            {
                "need_search": True,
                "title": "Current AI Research",
                "description": "Research current AI developments",
                "step_type": "research"
            },
            {
                "need_search": True,
                "title": "Future AI Trends",
                "description": "Analyze future AI trends",
                "step_type": "research"
            },
            {
                "need_search": False,
                "title": "Data Processing",
                "description": "Process collected data",
                "step_type": "processing"
            }
        ]
    }
    
    try:
        plan = Plan.model_validate(multi_step_plan)
        print("✅ Edge case 2 passed: Multi-step plan validation")
        print(f"   Steps count: {len(plan.steps)}")
        print(f"   Step types: {[step.step_type for step in plan.steps]}")
    except Exception as e:
        print(f"❌ Edge case 2 failed: {e}")
        return False
    
    return True


def main():
    """Run all tests."""
    print("🚀 Starting planner fallback tests...\n")
    
    test1_passed = test_fallback_plan_creation()
    test2_passed = test_plan_validation_edge_cases()
    
    print(f"\n📊 Test Results:")
    print(f"   Fallback plan tests: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   Edge case tests: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Planner fallback is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
