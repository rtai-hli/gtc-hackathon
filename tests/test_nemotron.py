#!/usr/bin/env python3
"""
Quick test script for NVIDIA Nemotron integration

Tests:
1. LLM wrapper initialization
2. Simple query with reasoning
3. Streaming response
4. Agent integration
"""

import asyncio
import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Run: pip install python-dotenv")

from agents.llm_wrapper import create_reasoning_llm
from agents.base import BaseAgent, EventType


async def test_llm_initialization():
    """Test 1: LLM wrapper initialization"""
    print("\n" + "="*80)
    print("TEST 1: LLM Wrapper Initialization")
    print("="*80 + "\n")

    try:
        llm = create_reasoning_llm(
            model="nvidia/nvidia-nemotron-nano-9b-v2",
            min_thinking_tokens=256,
            max_thinking_tokens=512
        )
        print("✓ LLM client created successfully")
        print(f"  Model: {llm.model}")
        print(f"  Thinking tokens: {llm.min_thinking_tokens}-{llm.max_thinking_tokens}")
        return llm
    except Exception as e:
        print(f"✗ Failed to create LLM client: {e}")
        return None


async def test_simple_query(llm):
    """Test 2: Simple query"""
    print("\n" + "="*80)
    print("TEST 2: Simple Query (Non-streaming)")
    print("="*80 + "\n")

    if not llm:
        print("⊘ Skipped (no LLM client)")
        return

    try:
        prompt = "What are the top 3 causes of database latency spikes in production?"
        print(f"Query: {prompt}\n")
        print("Response:")
        print("-" * 80)

        response = await llm.simple_query(
            prompt,
            system_message="You are a database performance expert. Be concise."
        )
        print(response)
        print("-" * 80)
        print("\n✓ Simple query completed")
    except Exception as e:
        print(f"✗ Simple query failed: {e}")


async def test_streaming_reasoning(llm):
    """Test 3: Streaming with reasoning display"""
    print("\n" + "="*80)
    print("TEST 3: Streaming with Reasoning Display")
    print("="*80 + "\n")

    if not llm:
        print("⊘ Skipped (no LLM client)")
        return

    try:
        messages = [
            {
                "role": "system",
                "content": "You are an incident response expert. Analyze problems systematically."
            },
            {
                "role": "user",
                "content": "A service is experiencing 500ms latency spikes every 5 minutes. What could be the cause?"
            }
        ]

        print("Query: Service experiencing 500ms latency spikes every 5 minutes\n")
        print("="*80)
        print("REASONING PROCESS:")
        print("="*80)

        reasoning_parts = []
        content_parts = []

        async for chunk in llm.think_and_respond(messages):
            if chunk["type"] == "reasoning":
                print(chunk["text"], end="", flush=True)
                reasoning_parts.append(chunk["text"])
            elif chunk["type"] == "content":
                if reasoning_parts:  # First content chunk after reasoning
                    print("\n\n" + "="*80)
                    print("FINAL RESPONSE:")
                    print("="*80)
                print(chunk["text"], end="", flush=True)
                content_parts.append(chunk["text"])

        print("\n" + "="*80)
        print(f"\n✓ Streaming completed")
        print(f"  Reasoning tokens: ~{len(''.join(reasoning_parts).split())}")
        print(f"  Response tokens: ~{len(''.join(content_parts).split())}")

    except Exception as e:
        print(f"✗ Streaming failed: {e}")


async def test_agent_integration(llm):
    """Test 4: Agent integration"""
    print("\n" + "="*80)
    print("TEST 4: Agent Integration")
    print("="*80 + "\n")

    if not llm:
        print("⊘ Skipped (no LLM client)")
        return

    try:
        # Create test agent
        agent = BaseAgent(
            name="TestAnalyst",
            role="Incident Analyst",
            llm_client=llm
        )

        # Add event listener to capture events
        events = []
        def capture_event(event):
            events.append(event)
            if event.event_type == EventType.THINKING:
                metadata = event.metadata.get("llm_reasoning", False)
                prefix = "[LLM Thinking]" if metadata else "[Agent Thinking]"
                # Only show first 100 chars of LLM reasoning to avoid spam
                content = event.content[:100] + "..." if len(event.content) > 100 else event.content
                print(f"{prefix} {content}")

        agent.add_event_listener(capture_event)

        print("Agent created. Testing llm_reason() method...\n")

        # Use agent's LLM reasoning
        result = await agent.llm_reason(
            prompt="What are common causes of memory leaks in Python microservices?",
            system_context="You are a Python expert. Provide a brief analysis.",
            emit_reasoning=True
        )

        print("\n" + "-"*80)
        print("Final Response:")
        print("-"*80)
        print(result)
        print("-"*80)

        print(f"\n✓ Agent integration successful")
        print(f"  Events emitted: {len(events)}")
        print(f"  Conversation history: {len(agent.conversation_history)} exchanges")

    except Exception as e:
        print(f"✗ Agent integration failed: {e}")


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧠 NVIDIA NEMOTRON INTEGRATION TEST SUITE")
    print("="*80)

    # Check for API key
    api_key = os.getenv("NVIDIA_API_KEY") or os.getenv("NGC_API_KEY")
    if not api_key:
        print("\n⚠️  WARNING: No API key found!")
        print("   Set NVIDIA_API_KEY or NGC_API_KEY environment variable")
        print("   Tests will fail without valid API key\n")
    else:
        print(f"\n✓ API key found: {api_key[:20]}...")

    # Run tests
    llm = await test_llm_initialization()
    await test_simple_query(llm)
    await test_streaming_reasoning(llm)
    await test_agent_integration(llm)

    print("\n" + "="*80)
    print("TEST SUITE COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
