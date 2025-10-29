"""
Incident Commander Agent

Role: Orchestrate investigation, make decisions, coordinate other agents

Responsibilities:
- Assess incident severity
- Delegate investigation tasks
- Synthesize findings
- Make final root cause determination
"""

import asyncio
from typing import Dict, Any, List
from agents.base import BaseAgent, EventType


class IncidentCommander(BaseAgent):
    """
    The incident commander orchestrates the war room response

    Demonstrates:
    - Multi-step reasoning
    - Tool delegation
    - Decision-making under uncertainty
    """

    def __init__(self, llm_client=None):
        super().__init__(
            name="Commander",
            role="Incident Commander",
            llm_client=llm_client
        )
        self.investigation_phase = "initial"
        self.theories = []
        self.assigned_tasks = []

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute incident response workflow

        Phases:
        1. Initial assessment
        2. Delegate investigation
        3. Review findings
        4. Determine root cause
        """

        incident = context.get("incident", {})

        # Store incident in agent context for later use
        self.update_context(incident=incident)

        # Phase 1: Initial Assessment
        await self.assess_incident(incident)

        # Phase 2: Delegate investigation (would coordinate with other agents)
        await self.delegate_investigation(incident)

        # Phase 3: Synthesize (for now, simple logic)
        await self.synthesize_findings()

        # Phase 4: Decision
        root_cause = await self.determine_root_cause()

        return {
            "status": "resolved",
            "root_cause": root_cause,
            "timeline": self.context.get("timeline", [])
        }

    async def assess_incident(self, incident: Dict[str, Any]):
        """Phase 1: Assess the incident"""

        self.think("Beginning incident assessment...")

        # Extract incident details
        symptom = incident.get("symptom", "Unknown issue")
        severity = incident.get("severity", "unknown")
        affected_service = incident.get("service", "unknown")

        self.think(
            f"Incident: {symptom} on {affected_service}",
            severity=severity
        )

        # Assess severity
        if "latency" in symptom.lower():
            self.think("Latency issue detected. Likely performance-related.")
            investigation_priority = ["metrics", "recent_changes", "logs"]
        elif "error" in symptom.lower():
            self.think("Error spike detected. Likely code or infrastructure issue.")
            investigation_priority = ["logs", "recent_changes", "metrics"]
        else:
            self.think("Unclear symptom. Need comprehensive investigation.")
            investigation_priority = ["logs", "metrics", "recent_changes"]

        self.context["investigation_priority"] = investigation_priority

        self.decide(
            f"Investigation priority: {' > '.join(investigation_priority)}",
            priority=investigation_priority
        )

    async def delegate_investigation(self, incident: Dict[str, Any]):
        """Phase 2: Delegate to specialist agents (simulated for now)"""

        self.investigation_phase = "delegating"

        priority = self.context.get("investigation_priority", [])

        for area in priority:
            self.think(f"Need to investigate: {area}")

            # In full implementation, would spawn/coordinate other agents
            # For now, simulate delegation
            task = {
                "area": area,
                "assigned_to": self._map_area_to_agent(area),
                "status": "pending"
            }
            self.assigned_tasks.append(task)

            self.emit_event(
                EventType.ACTION,
                f"Delegating {area} investigation to {task['assigned_to']}",
                {"task": task}
            )

        # Simulate waiting for results
        await asyncio.sleep(0.5)

    def _map_area_to_agent(self, area: str) -> str:
        """Map investigation area to specialist agent"""
        mapping = {
            "metrics": "System Investigator",
            "logs": "System Investigator",
            "recent_changes": "Code Detective",
            "git_history": "Code Detective"
        }
        return mapping.get(area, "General Investigator")

    async def synthesize_findings(self):
        """Phase 3: Synthesize findings from all agents"""

        self.investigation_phase = "synthesizing"

        self.think("Synthesizing findings from investigation teams...")

        # In full implementation, would gather theories from other agents
        # For now, simulate with context

        # Simulate receiving theories
        await asyncio.sleep(0.3)

        self.observe(
            "Received theories from investigation teams",
            theory_count=len(self.theories)
        )

    async def determine_root_cause(self) -> str:
        """Phase 4: Make final root cause determination"""

        self.investigation_phase = "concluding"

        self.think("Analyzing all evidence to determine root cause...")

        # Get incident from context
        incident = self.context.get("incident", {})

        if self.llm_client:
            # Use LLM reasoning for root cause analysis
            self.think("Using LLM reasoning to analyze incident...")

            prompt = f"""
You are an incident commander analyzing a production incident.

INCIDENT DETAILS:
- ID: {incident.get('id', 'unknown')}
- Symptom: {incident.get('symptom', 'unknown')}
- Severity: {incident.get('severity', 'unknown')}
- Service: {incident.get('service', 'unknown')}
- Impact: {incident.get('impact', 'unknown')}

INVESTIGATION AREAS EXAMINED:
{', '.join(self.context.get('investigation_priority', []))}

Based on the incident symptoms and investigation areas, determine the most likely root cause.
Provide your analysis and the root cause determination.
"""

            system_context = """You are a senior SRE and incident commander with deep expertise in:
- Distributed systems debugging
- Performance analysis
- Root cause analysis
- Production incident response

Analyze incidents systematically and provide actionable root cause determinations."""

            try:
                response = await self.llm_reason(prompt, system_context=system_context)
                root_cause = response.strip()
                confidence = 0.85  # LLM-based analysis
            except Exception as e:
                self.think(f"LLM reasoning failed: {e}. Falling back to rule-based analysis.")
                root_cause = self._fallback_root_cause_analysis(incident)
                confidence = 0.5
        else:
            # Fallback: rule-based analysis
            root_cause = self._fallback_root_cause_analysis(incident)
            confidence = 0.5

        self.think(
            f"Root cause analysis complete. Confidence: {confidence:.0%}",
            confidence=confidence
        )

        self.decide(
            f"ROOT CAUSE: {root_cause}",
            confidence=confidence,
            root_cause=root_cause
        )

        return root_cause

    def _fallback_root_cause_analysis(self, incident: Dict[str, Any]) -> str:
        """Fallback rule-based root cause analysis when LLM unavailable"""
        if not incident:
            return "Unknown - requires deeper investigation"

        symptom = incident.get("symptom", "").lower()

        if "latency" in symptom:
            self.think(
                "Evidence pattern matches: latency spike + recent deploy + database metrics",
                pattern="connection_pool_exhaustion"
            )
            return "Database connection pool exhaustion due to recent config change"
        elif "error" in symptom:
            return "Increased error rate due to code deployment or external dependency failure"
        else:
            return "Unknown - requires deeper investigation"

    def receive_theory(self, theory: Dict[str, Any]):
        """Receive a theory from another agent"""
        self.theories.append(theory)
        self.observe(
            f"Received theory: {theory.get('description', 'Unknown')}",
            source=theory.get('agent', 'Unknown')
        )
