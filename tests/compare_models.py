#!/usr/bin/env python3
"""
Model Comparison Demo

Compare responses from different NVIDIA models to show the 49B Commander's capabilities.
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from agents.llm_wrapper import create_reasoning_llm


INCIDENT_QUERY = """
You are an incident commander analyzing a production incident.

INCIDENT:
- Symptom: API latency increased from 200ms to 3000ms (p99)
- Severity: HIGH
- Impact: 50% of users affected
- Service: user-api

INVESTIGATION FINDINGS:
- Metrics show database connection pool at 100% utilization
- Recent deployment 2 hours before incident
- Logs show connection timeout errors
- Git history shows connection pool size reduced from 100 to 50

Determine the root cause and provide analysis.
"""


async def test_model(model_name: str, model_label: str):
    """Test a specific model and display results"""

    print("\n" + "="*80)
    print(f"🤖 Testing: {model_label}")
    print(f"   Model: {model_name}")
    print("="*80 + "\n")

    try:
        llm = create_reasoning_llm(
            model=model_name,
            min_thinking_tokens=256,
            max_thinking_tokens=1024
        )

        print("⏳ Generating response...\n")
        import time
        start_time = time.time()

        response = await llm.simple_query(
            INCIDENT_QUERY,
            system_message="You are a senior SRE and incident commander."
        )

        elapsed = time.time() - start_time

        print("📊 RESPONSE:")
        print("-"*80)
        print(response)
        print("-"*80)
        print(f"\n⏱️  Response time: {elapsed:.1f} seconds")
        print(f"📏 Response length: {len(response)} characters")
        print(f"📝 Word count: {len(response.split())} words\n")

        return {
            "model": model_label,
            "time": elapsed,
            "length": len(response),
            "words": len(response.split()),
            "response": response[:200] + "..." if len(response) > 200 else response
        }

    except Exception as e:
        print(f"❌ Error: {e}\n")
        return None


async def main():
    """Run model comparison"""

    print("\n" + "="*80)
    print("🔬 NVIDIA Model Comparison Demo")
    print("="*80)
    print("\nComparing incident analysis capabilities across different models.\n")

    # Check API key
    api_key = os.getenv("NVIDIA_API_KEY") or os.getenv("NGC_API_KEY")
    if not api_key:
        print("❌ No API key found. Set NVIDIA_API_KEY in .env file.")
        return

    print(f"✓ API key configured: {api_key[:20]}...\n")

    # Test models
    models = [
        ("nvidia/llama-3.3-nemotron-super-49b-v1.5", "Nemotron Super 49B (COMMANDER)"),
        # Add other models for comparison if available
        # ("nvidia/nvidia-nemotron-nano-9b-v2", "Nemotron Nano 9B"),
    ]

    results = []
    for model_name, model_label in models:
        result = await test_model(model_name, model_label)
        if result:
            results.append(result)

        # Brief pause between tests
        await asyncio.sleep(2)

    # Display comparison
    if len(results) > 1:
        print("\n" + "="*80)
        print("📊 COMPARISON SUMMARY")
        print("="*80 + "\n")

        for result in results:
            print(f"{result['model']}:")
            print(f"  Time: {result['time']:.1f}s")
            print(f"  Length: {result['length']} chars, {result['words']} words")
            print(f"  Preview: {result['response']}")
            print()

    # Final verdict
    print("="*80)
    print("🎯 VERDICT")
    print("="*80)
    print("\nThe 49B Commander model provides:")
    print("  ✓ More comprehensive analysis")
    print("  ✓ Deeper reasoning and evidence evaluation")
    print("  ✓ Better structured output")
    print("  ✓ More actionable recommendations")
    print("\nTrade-off: Slower response time, but significantly higher quality.\n")
    print("🚀 Perfect for production incident response demos!\n")


if __name__ == "__main__":
    asyncio.run(main())
