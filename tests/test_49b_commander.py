#!/usr/bin/env python3
"""
Test the 49B Nemotron Super Commander

Verifies that the Incident Commander uses the larger nvidia/llama-3.3-nemotron-super-49b-v1.5 model
for enhanced reasoning capabilities.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

from agents.commander import IncidentCommander
from agents.llm_wrapper import create_reasoning_llm
from scenarios.latency_spike import INCIDENT
from visualizer import WarRoomVisualizer


async def test_49b_model():
    """Test that the 49B model is properly configured and working"""

    print("\n" + "="*80)
    print("🧪 Testing NVIDIA Nemotron Super 49B Commander")
    print("="*80 + "\n")

    # Verify API key
    api_key = os.getenv("NVIDIA_API_KEY") or os.getenv("NGC_API_KEY")
    if not api_key:
        print("❌ ERROR: No NVIDIA API key found")
        print("   Set NVIDIA_API_KEY or NGC_API_KEY in .env file")
        return False

    print(f"✓ API key found: {api_key[:20]}...\n")

    # Create LLM client
    print("🧠 Initializing 49B Commander Model...")
    print("   Model: nvidia/llama-3.3-nemotron-super-49b-v1.5")
    print("   Reasoning tokens: 512-2048\n")

    try:
        llm_client = create_reasoning_llm(
            model="nvidia/llama-3.3-nemotron-super-49b-v1.5",
            min_thinking_tokens=512,
            max_thinking_tokens=2048
        )
        print("✓ LLM client initialized successfully")
        print(f"✓ Model: {llm_client.model}\n")
    except Exception as e:
        print(f"❌ Failed to initialize LLM: {e}")
        return False

    # Create commander with LLM
    print("🎖️  Creating Incident Commander with 49B model...\n")
    commander = IncidentCommander(llm_client=llm_client)

    # Verify commander has LLM
    if not commander.llm_client:
        print("❌ Commander does not have LLM client attached")
        return False

    print("✓ Commander configured with LLM client")
    print(f"✓ Commander will use: {commander.llm_client.model}\n")

    # Create visualizer
    visualizer = WarRoomVisualizer()
    commander.add_event_listener(visualizer.on_event)

    # Run incident response with 49B model
    print("="*80)
    print("🚨 Running Incident Response with 49B Commander")
    print("="*80 + "\n")

    print("INCIDENT:")
    print(f"  ID: {INCIDENT['id']}")
    print(f"  Symptom: {INCIDENT['symptom']}")
    print(f"  Severity: {INCIDENT['severity'].upper()}\n")

    print("-"*80 + "\n")

    try:
        context = {"incident": INCIDENT}
        result = await commander.run(context)

        print("\n" + "="*80)
        print("✅ INCIDENT RESPONSE COMPLETE")
        print("="*80 + "\n")

        print(f"Status: {result['status']}")
        print(f"Root Cause: {result['root_cause']}\n")

        # Display summary
        if hasattr(visualizer, 'display_summary'):
            visualizer.display_summary()

        print("\n" + "="*80)
        print("✅ TEST PASSED: 49B Commander working correctly")
        print("="*80 + "\n")

        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_simple_query():
    """Test a simple query to verify the 49B model is responding"""

    print("\n" + "="*80)
    print("🧪 Simple Query Test - 49B Model")
    print("="*80 + "\n")

    try:
        llm_client = create_reasoning_llm(
            model="nvidia/llama-3.3-nemotron-super-49b-v1.5"
        )

        print("Asking 49B model a simple question...\n")

        response = await llm_client.simple_query(
            "What are the top 3 causes of database connection pool exhaustion?",
            system_message="You are a database performance expert."
        )

        print("Response from 49B model:")
        print("-"*80)
        print(response)
        print("-"*80 + "\n")

        print("✅ Simple query test passed\n")
        return True

    except Exception as e:
        print(f"❌ Simple query failed: {e}")
        return False


def main():
    """Run all tests"""

    print("\n" + "🚀 Starting 49B Commander Test Suite" + "\n")

    # Test 1: Simple query
    result1 = asyncio.run(test_simple_query())

    # Test 2: Full incident response
    result2 = asyncio.run(test_49b_model())

    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    print(f"Simple Query Test: {'✅ PASSED' if result1 else '❌ FAILED'}")
    print(f"Full Incident Response Test: {'✅ PASSED' if result2 else '❌ FAILED'}")
    print("="*80 + "\n")

    if result1 and result2:
        print("🎉 All tests passed! The 49B Commander is ready for action.\n")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.\n")
        return 1


if __name__ == "__main__":
    exit(main())
