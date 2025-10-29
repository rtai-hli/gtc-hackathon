#!/usr/bin/env python3
"""
Simple CLI for nonprofit users to report incidents
This demonstrates the translation layer before building a web UI
"""

import sys
from datetime import datetime
from nonprofit_interface import (
    IncidentReport,
    IncidentTranslator,
    StatusSimplifier,
    IncidentManager
)


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def collect_incident_info():
    """Interactive form to collect incident information"""
    print_header("🆘 Helping Nemo")

    print("\nPlease answer these questions about the issue you're experiencing:\n")

    # Simple, plain-language questions
    what_trying = input("1. What were you trying to do?\n   → ")
    what_happened = input("\n2. What happened instead?\n   → ")

    print("\n3. When did this start?")
    print("   (Just describe in your own words, like 'this morning' or '2 hours ago')")
    when_started = input("   → ")

    # Convert relative time to timestamp (simplified for demo)
    # In production, use NLP or datetime picker
    timestamp = datetime.now().isoformat()

    is_urgent_input = input("\n4. Is this urgent? Users are affected right now? (yes/no)\n   → ")
    is_urgent = is_urgent_input.lower().startswith('y')

    additional = input("\n5. Anything else we should know? (optional)\n   → ")

    print("\n✅ Thank you! Submitting your report...\n")

    return IncidentReport(
        incident_id="",  # Will be auto-generated
        user_description=additional,
        what_trying_to_do=what_trying,
        what_happened_instead=what_happened,
        when_started=timestamp,
        is_urgent=is_urgent,
        additional_notes=additional if additional else None
    )


def show_investigation_progress():
    """Simulate showing progress to user"""
    import time

    phases = [
        ("PHASE_1", "🔍 Looking into the problem...", 2),
        ("PHASE_2", "🔎 Checking system logs and recent changes...", 3),
        ("PHASE_3", "💡 Analyzing potential causes...", 2),
        ("PHASE_4", "✅ Root cause identified!", 1),
    ]

    simplifier = StatusSimplifier()

    for phase_id, message, duration in phases:
        print(f"\n{message}")
        time.sleep(duration)

    print("\n")


def simulate_investigation(technical_context):
    """
    Simulate agent investigation
    In production, this would call your real agent system
    """
    # This is where you'd integrate with your existing demo.py agents
    # For now, simulate results based on the system

    system = technical_context.system_affected

    # Mock findings based on system type
    mock_findings = {
        "database": {
            "root_cause": "Database connection pool exhaustion due to configuration change",
            "confidence": 0.85,
            "actions": [
                "Update database connection pool configuration",
                "Restart database service",
                "Monitor connection usage for 24 hours"
            ],
            "fix_time": "15-30 minutes"
        },
        "email": {
            "root_cause": "Email service configuration pointing to deprecated SMTP server",
            "confidence": 0.90,
            "actions": [
                "Update SMTP server configuration",
                "Restart email service",
                "Send test emails to verify"
            ],
            "fix_time": "10-20 minutes"
        },
        "website": {
            "root_cause": "Recent deployment introduced broken CSS link",
            "confidence": 0.75,
            "actions": [
                "Rollback to previous deployment",
                "Fix CSS link in code",
                "Redeploy with fix"
            ],
            "fix_time": "30-45 minutes"
        }
    }

    # Return mock finding or generic one
    return mock_findings.get(system, {
        "root_cause": f"Issue detected in {system} component",
        "confidence": 0.70,
        "actions": [
            "Technical team will investigate the logs",
            "Identify specific component failure",
            "Implement appropriate fix"
        ],
        "fix_time": "1-2 hours"
    })


def main():
    """Main CLI flow"""
    print("\n" + "🏥 " * 20)
    print("     INCIDENT RESPONSE SYSTEM - Nonprofit Interface")
    print("🏥 " * 20)

    # Step 1: Collect incident information
    incident_report = collect_incident_info()

    # Step 2: Save incident
    manager = IncidentManager()
    incident_id = manager.create_incident(incident_report)

    print(f"📋 Incident created: {incident_id}")

    # Step 3: Translate to technical context
    translator = IncidentTranslator()
    technical_context = translator.translate_to_technical(incident_report)

    print_header("🤖 Starting AI Investigation")
    print(f"\nDetected System: {technical_context.system_affected}")
    print(f"Urgency Level: {technical_context.urgency_level}")
    print(f"Estimated User Impact: {technical_context.user_impact}")

    # Step 4: Show progress (in real app, this would be async status updates)
    show_investigation_progress()

    # Step 5: Run investigation (this is where your agents would run)
    print("🔬 AI agents analyzing the issue...")
    findings = simulate_investigation(technical_context)

    # Step 6: Show results to user
    print_header("📊 Investigation Complete")

    simplifier = StatusSimplifier()
    user_summary = simplifier.create_user_summary(
        root_cause=findings["root_cause"],
        confidence=findings["confidence"],
        recommended_actions=findings["actions"],
        estimated_fix_time=findings["fix_time"]
    )

    print(user_summary)

    # Step 7: Mention technical team notification
    print_header("📧 Technical Team Notified")
    print("\nThe technical team has received a detailed report with:")
    print("  ✓ Full investigation transcript")
    print("  ✓ All AI agent reasoning")
    print("  ✓ System logs and metrics analyzed")
    print("  ✓ Recommended fix steps")
    print(f"\nYour incident ID: {incident_id}")
    print("You can use this to check status or follow up.\n")

    # Optional: Show what technical team sees
    show_tech = input("Would you like to see the technical details? (yes/no): ")
    if show_tech.lower().startswith('y'):
        print_header("🔧 Technical Team View")
        print(f"\nIncident ID: {incident_id}")
        print(f"System: {technical_context.system_affected}")
        print(f"Symptoms: {', '.join(technical_context.symptoms)}")
        print(f"Timing: {technical_context.timing_info}")
        print(f"\nRoot Cause (Technical): {findings['root_cause']}")
        print(f"Confidence: {findings['confidence'] * 100}%")
        print("\nRecommended Actions:")
        for i, action in enumerate(findings['actions'], 1):
            print(f"  {i}. {action}")
        print(f"\nRaw User Input: {technical_context.raw_user_input}")
        print("\n(In production, tech team would also see full agent reasoning logs)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(0)
