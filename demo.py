"""
Demo Runner - Incident Response War Room

Quick start demo showing:
- Incident Commander reasoning
- Multi-step investigation
- Observable agent thinking
- LLM-powered root cause analysis with nvidia/llama-3.3-nemotron-super-49b-v1.5
"""

import asyncio
import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Run: pip install python-dotenv")

from agents.commander import IncidentCommander
from agents.llm_wrapper import create_reasoning_llm
from scenarios.latency_spike import INCIDENT
from agents.visualizer import WarRoomVisualizer, SimpleVisualizer


async def run_demo(use_simple_viz=False):
    """
    Run the incident response demo

    Args:
        use_simple_viz: Use simple visualizer (True) or full visualizer (False)
    """

    print("\n" + "="*80)
    print("🚨 INCIDENT RESPONSE WAR ROOM - DEMO")
    print("="*80 + "\n")

    print("INCIDENT DETECTED:")
    print(f"  ID: {INCIDENT['id']}")
    print(f"  Symptom: {INCIDENT['symptom']}")
    print(f"  Severity: {INCIDENT['severity'].upper()}")
    print(f"  Service: {INCIDENT['service']}")
    print(f"  Impact: {INCIDENT['impact']}")
    print("\n" + "-"*80 + "\n")

    print("Initializing war room agents...\n")

    # Create visualizer
    if use_simple_viz:
        visualizer = SimpleVisualizer()
    else:
        visualizer = WarRoomVisualizer()

    # Create LLM client if API key is available
    llm_client = None
    try:
        if os.getenv("NVIDIA_API_KEY") or os.getenv("NGC_API_KEY"):
            print("🧠 Initializing NVIDIA Nemotron Super 49B LLM as Commander...")
            print("   Model: nvidia/llama-3.3-nemotron-super-49b-v1.5")
            llm_client = create_reasoning_llm(
                model="nvidia/llama-3.3-nemotron-super-49b-v1.5",
                min_thinking_tokens=512,
                max_thinking_tokens=2048
            )
            print("✓ Commander LLM ready with enhanced reasoning capabilities\n")
        else:
            print("⚠️  No NVIDIA API key found - using rule-based reasoning\n")
    except Exception as e:
        print(f"⚠️  Failed to initialize LLM: {e}")
        print("   Falling back to rule-based reasoning\n")

    # Create incident commander with optional LLM
    commander = IncidentCommander(llm_client=llm_client)

    # Attach visualizer to commander
    commander.add_event_listener(visualizer.on_event)

    print("Starting incident response...\n")
    print("="*80 + "\n")

    # Run incident response
    context = {"incident": INCIDENT}
    result = await commander.run(context)

    print("\n" + "="*80)
    print("INCIDENT RESPONSE COMPLETE")
    print("="*80 + "\n")

    print(f"Status: {result['status']}")
    print(f"Root Cause: {result['root_cause']}\n")

    # Show summary if using full visualizer
    if hasattr(visualizer, 'display_summary'):
        visualizer.display_summary()


async def run_interactive_demo():
    """Interactive demo with step-by-step progression"""

    print("\n" + "="*80)
    print("🚨 INCIDENT RESPONSE WAR ROOM - INTERACTIVE DEMO")
    print("="*80 + "\n")

    visualizer = WarRoomVisualizer()

    # Create LLM client
    llm_client = None
    try:
        if os.getenv("NVIDIA_API_KEY") or os.getenv("NGC_API_KEY"):
            print("🧠 Initializing NVIDIA Nemotron Super 49B LLM as Commander...")
            llm_client = create_reasoning_llm(
                model="nvidia/llama-3.3-nemotron-super-49b-v1.5"
            )
            print("✓ Commander LLM ready\n")
    except Exception as e:
        print(f"⚠️  LLM initialization failed: {e}\n")

    commander = IncidentCommander(llm_client=llm_client)
    commander.add_event_listener(visualizer.on_event)

    print("INCIDENT:")
    print(f"  {INCIDENT['symptom']}")
    print(f"  Severity: {INCIDENT['severity'].upper()}\n")

    input("Press Enter to start incident response...")
    print()

    # Phase 1
    print("Phase 1: Initial Assessment")
    print("-" * 80)
    await commander.assess_incident(INCIDENT)

    input("\nPress Enter to continue to delegation...")
    print()

    # Phase 2
    print("Phase 2: Delegate Investigation")
    print("-" * 80)
    await commander.delegate_investigation(INCIDENT)

    input("\nPress Enter to continue to synthesis...")
    print()

    # Phase 3
    print("Phase 3: Synthesize Findings")
    print("-" * 80)
    await commander.synthesize_findings()

    input("\nPress Enter to determine root cause...")
    print()

    # Phase 4
    print("Phase 4: Root Cause Determination")
    print("-" * 80)
    root_cause = await commander.determine_root_cause()

    print("\n" + "="*80)
    print(f"ROOT CAUSE: {root_cause}")
    print("="*80 + "\n")


def main():
    """Main entry point"""

    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        asyncio.run(run_interactive_demo())
    elif len(sys.argv) > 1 and sys.argv[1] == "--simple":
        asyncio.run(run_demo(use_simple_viz=True))
    else:
        asyncio.run(run_demo(use_simple_viz=False))


if __name__ == "__main__":
    main()
