"""
Nonprofit Interface Layer
Translates between plain-language user input and technical agent system
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class IncidentReport:
    """Plain-language incident report from nonprofit user"""
    incident_id: str
    user_description: str
    what_trying_to_do: str
    what_happened_instead: str
    when_started: str
    is_urgent: bool
    screenshot_path: Optional[str] = None
    additional_notes: Optional[str] = None
    submitted_at: str = None

    def __post_init__(self):
        if self.submitted_at is None:
            self.submitted_at = datetime.now().isoformat()


@dataclass
class TechnicalContext:
    """Technical context extracted from user report"""
    incident_id: str
    system_affected: str
    symptoms: List[str]
    urgency_level: str  # "low", "medium", "high", "critical"
    timing_info: Dict[str, str]
    user_impact: str
    raw_user_input: str


class IncidentTranslator:
    """Converts between plain language and technical format"""

    # Keywords mapping user language to technical systems
    SYSTEM_KEYWORDS = {
        "email": ["email", "receipt", "send", "smtp", "mail", "message"],
        "database": ["database", "save", "record", "data", "storage", "query"],
        "website": ["website", "page", "load", "browser", "link", "url"],
        "api": ["connect", "integration", "sync", "api", "external"],
        "authentication": ["login", "password", "sign in", "access", "authenticate"],
        "payment": ["donation", "payment", "transaction", "charge", "billing"],
        "reporting": ["report", "export", "download", "analytics", "dashboard"],
    }

    URGENCY_KEYWORDS = {
        "critical": ["can't", "broken", "down", "emergency", "urgent", "stopped completely"],
        "high": ["not working", "failing", "error", "users affected", "multiple"],
        "medium": ["slow", "sometimes", "intermittent", "occasionally"],
        "low": ["minor", "cosmetic", "small issue", "when I have time"],
    }

    def translate_to_technical(self, incident: IncidentReport) -> TechnicalContext:
        """Convert user report to technical context for agents"""

        # Combine all user text for analysis
        full_description = f"{incident.what_trying_to_do} {incident.what_happened_instead} {incident.user_description or ''}"
        full_description = full_description.lower()

        # Identify affected system
        system = self._identify_system(full_description)

        # Extract symptoms
        symptoms = self._extract_symptoms(full_description)

        # Determine urgency
        urgency = self._determine_urgency(incident, full_description)

        # Parse timing
        timing_info = {
            "reported_time": incident.submitted_at,
            "incident_start": incident.when_started,
            "duration": self._calculate_duration(incident.when_started),
        }

        # Assess user impact
        user_impact = self._assess_impact(full_description, urgency)

        return TechnicalContext(
            incident_id=incident.incident_id,
            system_affected=system,
            symptoms=symptoms,
            urgency_level=urgency,
            timing_info=timing_info,
            user_impact=user_impact,
            raw_user_input=full_description,
        )

    def _identify_system(self, text: str) -> str:
        """Identify which system is affected based on keywords"""
        scores = {}
        for system, keywords in self.SYSTEM_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                scores[system] = score

        if not scores:
            return "unknown_system"

        # Return system with highest keyword match
        return max(scores, key=scores.get)

    def _extract_symptoms(self, text: str) -> List[str]:
        """Extract technical symptoms from user description"""
        symptoms = []

        symptom_patterns = {
            "error_message": ["error", "message", "warning", "alert"],
            "performance_degradation": ["slow", "loading", "timeout", "lag"],
            "functionality_broken": ["not working", "can't", "unable", "broken", "won't"],
            "data_issue": ["missing", "wrong", "incorrect", "lost", "disappeared"],
            "access_issue": ["can't login", "access denied", "permission", "locked out"],
        }

        for symptom, keywords in symptom_patterns.items():
            if any(keyword in text for keyword in keywords):
                symptoms.append(symptom)

        return symptoms if symptoms else ["unspecified_issue"]

    def _determine_urgency(self, incident: IncidentReport, text: str) -> str:
        """Determine urgency level from context"""
        if incident.is_urgent:
            return "high"

        # Check for urgency keywords
        for level, keywords in self.URGENCY_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                return level

        return "medium"

    def _calculate_duration(self, when_started: str) -> str:
        """Calculate how long the incident has been occurring"""
        try:
            start_time = datetime.fromisoformat(when_started)
            duration = datetime.now() - start_time
            hours = duration.total_seconds() / 3600

            if hours < 1:
                return f"{int(duration.total_seconds() / 60)} minutes"
            elif hours < 24:
                return f"{int(hours)} hours"
            else:
                return f"{int(hours / 24)} days"
        except:
            return "unknown"

    def _assess_impact(self, text: str, urgency: str) -> str:
        """Assess user impact from description"""
        impact_indicators = {
            "users_affected": ["users", "people", "everyone", "all", "multiple"],
            "business_critical": ["donation", "payment", "registration", "critical"],
            "data_loss_risk": ["lost", "missing", "delete", "disappeared"],
        }

        impacts = []
        for impact, keywords in impact_indicators.items():
            if any(keyword in text for keyword in keywords):
                impacts.append(impact)

        if not impacts:
            return "single_user"

        return " + ".join(impacts)


class StatusSimplifier:
    """Convert technical agent output to user-friendly status messages with Nemo personality"""

    PHASE_MESSAGES = {
        "PHASE_1": "🐠 Nemo is reading what you told me...",
        "PHASE_2": "🔎 Nemo is diving into system logs...",
        "PHASE_3": "💡 Nemo found something!",
        "PHASE_4": "🐠 Nemo has your solution ready!",
    }

    def get_status_message(self, current_phase: str) -> str:
        """Get user-friendly status message for current phase"""
        return self.PHASE_MESSAGES.get(current_phase, "🔄 Investigating...")

    def simplify_root_cause(self, technical_finding: str, confidence: float) -> str:
        """Convert technical root cause to plain language with Nemo's friendly voice"""
        # This would use more sophisticated NLP in production
        # For now, extract key concepts

        simplified = technical_finding

        # Replace technical jargon with plain language
        replacements = {
            "connection pool exhaustion": "system ran out of database connections",
            "timeout": "taking too long to respond",
            "configuration": "settings",
            "deployment": "update",
            "query": "database request",
            "latency": "slowness",
            "throughput": "processing speed",
            "memory leak": "slowly using more memory than it should",
            "race condition": "timing issue between processes",
        }

        for technical, plain in replacements.items():
            simplified = simplified.replace(technical, plain)

        confidence_phrase = self._confidence_to_phrase(confidence)

        return f"🐠 {confidence_phrase}, here's what I discovered: {simplified}"

    def _confidence_to_phrase(self, confidence: float) -> str:
        """Convert confidence percentage to plain language with Nemo's friendly voice"""
        if confidence >= 0.9:
            return "I'm very confident"
        elif confidence >= 0.75:
            return "I'm fairly confident"
        elif confidence >= 0.6:
            return "I think"
        else:
            return "I have a good hypothesis"

    def create_user_summary(self, root_cause: str, confidence: float,
                           recommended_actions: List[str],
                           estimated_fix_time: str) -> str:
        """Create complete summary for nonprofit user with Nemo's personality"""

        simplified_cause = self.simplify_root_cause(root_cause, confidence)

        summary = f"""
🐠 We did it! Here's what I found:

{simplified_cause}

What happens next:
"""

        for i, action in enumerate(recommended_actions, 1):
            # Simplify action descriptions
            plain_action = self._simplify_action(action)
            summary += f"{i}. {plain_action}\n"

        summary += f"\n⏱️ Expected fix time: {estimated_fix_time}"
        summary += f"\n\n💚 Thanks for helping me help you!"

        return summary

    def _simplify_action(self, technical_action: str) -> str:
        """Simplify recommended action for user"""
        # Extract intent and simplify
        if "restart" in technical_action.lower():
            return "The technical team will restart the affected service"
        elif "update" in technical_action.lower() or "change" in technical_action.lower():
            return "The technical team will update the configuration"
        elif "deploy" in technical_action.lower():
            return "The technical team will deploy a fix"
        elif "investigate" in technical_action.lower():
            return "The technical team will investigate further"
        else:
            return f"The technical team will {technical_action.lower()}"

    def create_technical_summary(self, investigation_results: Dict) -> str:
        """Create detailed technical summary for tech team"""
        return json.dumps(investigation_results, indent=2)


class IncidentManager:
    """Manages incident lifecycle and storage"""

    def __init__(self, storage_path: str = "./incidents"):
        self.storage_path = storage_path
        import os
        os.makedirs(storage_path, exist_ok=True)

    def create_incident(self, report: IncidentReport) -> str:
        """Store incident report and return incident ID"""
        # Generate incident ID if not provided
        if not report.incident_id:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            report.incident_id = f"INC-{timestamp}"

        # Save to file
        filepath = f"{self.storage_path}/{report.incident_id}.json"
        with open(filepath, 'w') as f:
            json.dump(asdict(report), f, indent=2)

        return report.incident_id

    def get_incident(self, incident_id: str) -> Optional[IncidentReport]:
        """Retrieve incident by ID"""
        filepath = f"{self.storage_path}/{incident_id}.json"
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                return IncidentReport(**data)
        except FileNotFoundError:
            return None

    def list_incidents(self, status: Optional[str] = None) -> List[IncidentReport]:
        """List all incidents, optionally filtered by status"""
        import os
        incidents = []

        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                filepath = f"{self.storage_path}/{filename}"
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    incidents.append(IncidentReport(**data))

        return incidents


# Example usage
if __name__ == "__main__":
    # Simulate nonprofit user submitting incident
    user_report = IncidentReport(
        incident_id="",  # Will be auto-generated
        user_description="Our donor database isn't working",
        what_trying_to_do="I was trying to add a new donor to our database",
        what_happened_instead="I got an error message saying 'Error 500 - Internal Server Error'",
        when_started=datetime.now().isoformat(),
        is_urgent=True,
    )

    # Translate to technical context
    translator = IncidentTranslator()
    technical_context = translator.translate_to_technical(user_report)

    print("=" * 60)
    print("USER REPORT (Plain Language)")
    print("=" * 60)
    print(f"What they were doing: {user_report.what_trying_to_do}")
    print(f"What happened: {user_report.what_happened_instead}")
    print(f"Urgent: {'Yes' if user_report.is_urgent else 'No'}")
    print()

    print("=" * 60)
    print("TECHNICAL CONTEXT (For Agents)")
    print("=" * 60)
    print(f"System: {technical_context.system_affected}")
    print(f"Symptoms: {', '.join(technical_context.symptoms)}")
    print(f"Urgency: {technical_context.urgency_level}")
    print(f"Impact: {technical_context.user_impact}")
    print()

    # Simulate agent findings
    print("=" * 60)
    print("AGENT INVESTIGATION RESULTS")
    print("=" * 60)
    technical_finding = "Database connection pool exhaustion due to configuration change reducing pool from 100 to 50 connections"
    confidence = 0.85

    # Simplify for user
    simplifier = StatusSimplifier()
    user_summary = simplifier.create_user_summary(
        root_cause=technical_finding,
        confidence=confidence,
        recommended_actions=[
            "Update database connection pool configuration",
            "Restart database service",
            "Monitor connection usage"
        ],
        estimated_fix_time="15-30 minutes"
    )

    print("\n" + "=" * 60)
    print("USER-FRIENDLY SUMMARY")
    print("=" * 60)
    print(user_summary)

    print("\n" + "=" * 60)
    print("TECHNICAL SUMMARY (For Tech Team)")
    print("=" * 60)
    print(f"Root Cause: {technical_finding}")
    print(f"Confidence: {confidence * 100}%")
    print("Recommended Actions: Update pool config, restart service, monitor")
