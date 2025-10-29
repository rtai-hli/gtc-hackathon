# 🔧 Technical Integration Guide - Connecting Nonprofit Interface to Agents

This guide shows your technical team how to integrate the nonprofit-friendly interface with your existing multi-agent system.

---

## 🎯 Integration Overview

### What We Built

**Nonprofit Interface Layer** (`nonprofit_interface.py`):
- `IncidentTranslator` - Converts plain language → technical context
- `StatusSimplifier` - Converts agent output → plain language
- `IncidentManager` - Stores and retrieves incidents

**CLI Demo** (`simple_nonprofit_cli.py`):
- Interactive form for testing
- Shows both user and technical views
- Demonstrates translation in action

### What You Need to Connect

Your existing agent system from `demo.py` and `agents/commander.py` needs to:
1. Accept incident context as input (instead of pre-seeded scenarios)
2. Emit progress events during investigation
3. Return structured results (root cause, confidence, actions)

---

## 📊 Data Flow Architecture

```
┌─────────────────────┐
│  Nonprofit User     │
│  (Simple Form)      │
└──────────┬──────────┘
           │ Plain language description
           ↓
┌─────────────────────┐
│ IncidentTranslator  │
│  - Parse keywords   │
│  - Identify system  │
│  - Extract symptoms │
└──────────┬──────────┘
           │ TechnicalContext object
           ↓
┌─────────────────────┐
│  Your Agent System  │
│  - Commander        │
│  - Investigator     │
│  - Detective        │
└──────────┬──────────┘
           │ Investigation results
           ↓
┌─────────────────────┐
│ StatusSimplifier    │
│  - Plain language   │
│  - User summary     │
└──────────┬──────────┘
           │
           ├─────────────────────┐
           │                     │
           ↓                     ↓
┌──────────────────┐  ┌────────────────┐
│  Nonprofit User  │  │ Technical Team │
│  Simple summary  │  │  Full details  │
└──────────────────┘  └────────────────┘
```

---

## 🔌 Integration Points

### Point 1: Modify `demo.py` to Accept External Incidents

**Current** (from `demo.py`):
```python
# Hardcoded scenario
scenario = LatencySpikeScenario()
result = await commander.run(scenario)
```

**Modified** (to accept incident context):
```python
async def investigate_incident(incident_context: TechnicalContext):
    """
    Run investigation based on incident context from nonprofit user
    """
    # Convert TechnicalContext to your scenario format
    dynamic_scenario = create_scenario_from_context(incident_context)

    # Run existing agent system
    commander = IncidentCommander()
    result = await commander.run(dynamic_scenario)

    return result
```

### Point 2: Create Scenario Adapter

**New file**: `scenario_adapter.py`

```python
from scenarios.latency_spike import LatencySpikeScenario
from nonprofit_interface import TechnicalContext


def create_scenario_from_context(context: TechnicalContext):
    """
    Converts TechnicalContext to your existing scenario format
    """

    # Map symptoms to pre-seeded data
    scenario_data = {
        "incident_id": context.incident_id,
        "description": f"Issue with {context.system_affected}: {', '.join(context.symptoms)}",
        "severity": context.urgency_level,
        "reported_at": context.timing_info["reported_time"],
    }

    # Generate appropriate data based on system
    if context.system_affected == "database":
        return create_database_scenario(scenario_data, context)
    elif context.system_affected == "email":
        return create_email_scenario(scenario_data, context)
    elif context.system_affected == "website":
        return create_website_scenario(scenario_data, context)
    else:
        return create_generic_scenario(scenario_data, context)


def create_database_scenario(data, context):
    """Create database-specific scenario with appropriate simulated data"""
    return {
        **data,
        "metrics": simulate_database_metrics(context),
        "logs": simulate_database_logs(context),
        "recent_changes": simulate_git_history(context),
    }


def simulate_database_metrics(context):
    """Generate realistic metrics based on symptoms"""
    if "performance_degradation" in context.symptoms:
        return {
            "query_latency_ms": [450, 520, 680, 890, 1200],  # Increasing
            "connection_pool_usage": [85, 92, 98, 100, 100],  # Exhausted
            "active_connections": [95, 98, 100, 100, 100],
        }
    elif "error_message" in context.symptoms:
        return {
            "error_rate": [0.1, 0.5, 2.3, 5.1, 8.7],  # Increasing errors
            "timeout_count": [2, 5, 12, 18, 24],
        }
    else:
        return {}  # Generic metrics


def simulate_database_logs(context):
    """Generate realistic log entries based on symptoms"""
    logs = []

    if "functionality_broken" in context.symptoms:
        logs.extend([
            {"timestamp": "2024-10-29T14:23:45", "level": "ERROR",
             "message": "Connection timeout waiting for pool"},
            {"timestamp": "2024-10-29T14:24:12", "level": "ERROR",
             "message": "Failed to acquire connection from pool"},
        ])

    return logs


def simulate_git_history(context):
    """Generate relevant git history based on timing"""
    # If incident is recent, show recent deployments
    return [
        {"commit": "abc123", "author": "dev@team.org",
         "date": context.timing_info["reported_time"],
         "message": "Update database pool configuration"},
    ]
```

### Point 3: Add Progress Callbacks

**Modify `agents/commander.py`**:

Add callback support for status updates:

```python
class IncidentCommander(BaseAgent):
    def __init__(self, progress_callback=None):
        super().__init__(name="Commander", role="Incident Commander")
        self.progress_callback = progress_callback

    async def run(self, context):
        # Notify start of phase
        if self.progress_callback:
            await self.progress_callback("PHASE_1", "Initial assessment")

        # Phase 1: Initial Assessment
        self.think("Assessing incident severity...")
        # ... existing logic ...

        if self.progress_callback:
            await self.progress_callback("PHASE_2", "Deep analysis")

        # Phase 2: Deep Analysis
        # ... existing logic ...

        if self.progress_callback:
            await self.progress_callback("PHASE_3", "Root cause analysis")

        # Phase 3: Root Cause Analysis
        # ... existing logic ...

        if self.progress_callback:
            await self.progress_callback("PHASE_4", "Complete")

        return results
```

### Point 4: Structure Results for Translation

**Modify agent return values**:

```python
def format_results_for_translation(agent_results):
    """
    Convert your agent's internal results to format expected by StatusSimplifier
    """
    return {
        "root_cause": agent_results["determination"],  # Plain technical description
        "confidence": agent_results["confidence"],      # Float 0.0-1.0
        "recommended_actions": [
            # List of action strings
            "Update database connection pool configuration",
            "Restart affected services",
            "Monitor for 24 hours"
        ],
        "estimated_fix_time": estimate_fix_time(agent_results),
        "evidence": agent_results.get("evidence", []),  # For technical team
        "reasoning_trace": agent_results.get("reasoning", []),  # Full agent thinking
    }


def estimate_fix_time(results):
    """Estimate fix time based on root cause and complexity"""
    # Simple heuristic - improve with ML later
    if "configuration" in results["determination"].lower():
        return "15-30 minutes"
    elif "code change" in results["determination"].lower():
        return "1-2 hours"
    elif "infrastructure" in results["determination"].lower():
        return "2-4 hours"
    else:
        return "1-3 hours"
```

---

## 🚀 Complete Integration Example

**New file**: `integrated_demo.py`

```python
#!/usr/bin/env python3
"""
Integrated demo showing nonprofit interface → agent system → results
"""

import asyncio
from nonprofit_interface import (
    IncidentReport,
    IncidentTranslator,
    StatusSimplifier,
    IncidentManager
)
from scenario_adapter import create_scenario_from_context
from agents.commander import IncidentCommander
from datetime import datetime


async def progress_callback(phase: str, message: str):
    """Called by agents to report progress"""
    simplifier = StatusSimplifier()
    user_message = simplifier.get_status_message(phase)
    print(f"\n{user_message}")


async def run_integrated_investigation(incident_report: IncidentReport):
    """
    Full pipeline: User report → Translation → Investigation → Results
    """

    print("\n" + "="*70)
    print("  INTEGRATED INCIDENT RESPONSE SYSTEM")
    print("="*70)

    # Step 1: Translate user input to technical context
    print("\n[1/5] Translating user input...")
    translator = IncidentTranslator()
    technical_context = translator.translate_to_technical(incident_report)

    print(f"     Detected system: {technical_context.system_affected}")
    print(f"     Urgency: {technical_context.urgency_level}")

    # Step 2: Create scenario for your agents
    print("\n[2/5] Preparing investigation scenario...")
    scenario = create_scenario_from_context(technical_context)

    # Step 3: Run your agent system with progress callbacks
    print("\n[3/5] Starting AI investigation...")
    commander = IncidentCommander(progress_callback=progress_callback)
    agent_results = await commander.run(scenario)

    # Step 4: Format results
    print("\n[4/5] Analyzing results...")
    formatted_results = format_results_for_translation(agent_results)

    # Step 5: Create summaries for both audiences
    print("\n[5/5] Generating summaries...")
    simplifier = StatusSimplifier()

    # User-friendly summary
    user_summary = simplifier.create_user_summary(
        root_cause=formatted_results["root_cause"],
        confidence=formatted_results["confidence"],
        recommended_actions=formatted_results["recommended_actions"],
        estimated_fix_time=formatted_results["estimated_fix_time"]
    )

    # Technical summary
    technical_summary = simplifier.create_technical_summary(formatted_results)

    # Display results
    print("\n" + "="*70)
    print("  RESULTS FOR NONPROFIT USER")
    print("="*70)
    print(user_summary)

    print("\n" + "="*70)
    print("  RESULTS FOR TECHNICAL TEAM")
    print("="*70)
    print(technical_summary)

    return {
        "user_summary": user_summary,
        "technical_summary": technical_summary,
        "incident_id": incident_report.incident_id,
    }


def format_results_for_translation(agent_results):
    """Your implementation here - see Point 4 above"""
    # This is where you extract and structure your agent's findings
    return {
        "root_cause": agent_results.get("determination", "Unknown issue"),
        "confidence": agent_results.get("confidence", 0.7),
        "recommended_actions": [
            "Action 1 from your agents",
            "Action 2 from your agents",
        ],
        "estimated_fix_time": "30-60 minutes",
        "evidence": agent_results.get("evidence", []),
        "reasoning_trace": agent_results.get("reasoning", []),
    }


async def main():
    """Test the integrated system"""

    # Simulate nonprofit user submitting report
    test_report = IncidentReport(
        incident_id="TEST-001",
        user_description="Database not working",
        what_trying_to_do="Add a new donor to the database",
        what_happened_instead="Got error message 'Error 500'",
        when_started=datetime.now().isoformat(),
        is_urgent=True
    )

    # Run full pipeline
    results = await run_integrated_investigation(test_report)

    print("\n✅ Integration test complete!")
    print(f"   Incident ID: {results['incident_id']}")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🧪 Testing the Integration

### Test 1: Translation Accuracy

```bash
# Test that translator correctly identifies systems
python -c "
from nonprofit_interface import IncidentReport, IncidentTranslator
from datetime import datetime

test_cases = [
    ('email not working', 'email'),
    ('database error 500', 'database'),
    ('website loading slow', 'website'),
]

translator = IncidentTranslator()

for description, expected_system in test_cases:
    report = IncidentReport(
        incident_id='TEST',
        user_description=description,
        what_trying_to_do=description,
        what_happened_instead='error',
        when_started=datetime.now().isoformat(),
        is_urgent=False
    )
    context = translator.translate_to_technical(report)
    assert context.system_affected == expected_system, f'Expected {expected_system}, got {context.system_affected}'
    print(f'✅ {description} → {context.system_affected}')
"
```

### Test 2: End-to-End Flow

```bash
# Run the simple CLI to test full flow
python simple_nonprofit_cli.py

# Follow prompts and verify:
# 1. Translation makes sense
# 2. Progress updates appear
# 3. User summary is plain language
# 4. Technical summary has details
```

### Test 3: Integration with Real Agents

```bash
# Run integrated demo with your actual agent system
python integrated_demo.py

# Verify:
# 1. Agents receive correct scenario
# 2. Progress callbacks work
# 3. Results are properly formatted
# 4. Both summaries are generated
```

---

## 📈 Performance Considerations

### Caching Translation Results

```python
# Add caching to translator for common patterns
from functools import lru_cache

class IncidentTranslator:
    @lru_cache(maxsize=100)
    def _identify_system(self, text: str) -> str:
        # Cached for repeated similar descriptions
        pass
```

### Async Progress Updates

```python
# For web UI, use websockets for real-time updates
import asyncio
from typing import Callable

class ProgressStreamer:
    def __init__(self, websocket_callback: Callable):
        self.callback = websocket_callback

    async def update(self, phase: str, message: str):
        await self.callback({"phase": phase, "message": message})
```

### Result Caching

```python
# Cache investigation results for similar incidents
# (Useful when multiple users report the same issue)

class ResultCache:
    def get_similar_incident(self, technical_context):
        # Check if we've seen this issue recently
        # Return cached results if confidence is high
        pass
```

---

## 🔒 Security Considerations

### Input Sanitization

```python
def sanitize_user_input(text: str) -> str:
    """Remove potentially malicious content"""
    # Remove script tags, SQL injection attempts, etc.
    import html
    return html.escape(text)
```

### Rate Limiting

```python
# Prevent abuse of investigation system
from functools import wraps
import time

def rate_limit(max_per_hour=10):
    calls = {}

    def decorator(func):
        @wraps(func)
        def wrapper(user_id, *args, **kwargs):
            now = time.time()
            hour_ago = now - 3600

            # Clean old entries
            calls[user_id] = [t for t in calls.get(user_id, []) if t > hour_ago]

            if len(calls.get(user_id, [])) >= max_per_hour:
                raise Exception("Rate limit exceeded")

            calls.setdefault(user_id, []).append(now)
            return func(user_id, *args, **kwargs)
        return wrapper
    return decorator
```

---

## 📦 Deployment Checklist

Before deploying to production:

- [ ] Test translation with 20+ real user descriptions
- [ ] Verify agent integration works end-to-end
- [ ] Set up proper error handling and logging
- [ ] Implement rate limiting
- [ ] Add input sanitization
- [ ] Configure notification system (email/Slack)
- [ ] Set up incident storage (database vs files)
- [ ] Create monitoring dashboard
- [ ] Write runbook for technical team
- [ ] Train nonprofit staff on the system

---

## 🆘 Troubleshooting

### Issue: Translation identifies wrong system

**Solution**: Enhance keyword dictionary in `SYSTEM_KEYWORDS`

```python
SYSTEM_KEYWORDS = {
    "email": ["email", "receipt", "send", "smtp", "mail", "message",
              "inbox", "outbox", "delivery"],  # Add more keywords
    # ...
}
```

### Issue: Agent results don't match expected format

**Solution**: Add adapter in `format_results_for_translation()`

```python
def format_results_for_translation(agent_results):
    # Handle different result formats
    if "root_cause" in agent_results:
        root_cause = agent_results["root_cause"]
    elif "determination" in agent_results:
        root_cause = agent_results["determination"]
    else:
        root_cause = "Unknown - check logs"
    # ...
```

### Issue: Progress updates not appearing

**Solution**: Verify async callback is awaited

```python
# Wrong
if self.progress_callback:
    self.progress_callback("PHASE_1", "Starting")  # Missing await

# Right
if self.progress_callback:
    await self.progress_callback("PHASE_1", "Starting")
```

---

## 🎓 Next Steps

1. **Week 1**: Test integration with existing agent system
2. **Week 2**: Build web UI (Flask/FastAPI)
3. **Week 3**: Add notifications (email/Slack)
4. **Week 4**: Deploy and train users

---

**Questions? Issues? Check the main [NONPROFIT_PIVOT_PLAN.md](NONPROFIT_PIVOT_PLAN.md) for architecture details.**
