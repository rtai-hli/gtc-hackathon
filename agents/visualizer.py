"""
Real-time Agent Activity Visualizer

Provides a terminal-based visualization of agent thinking and actions
"""

import asyncio
from datetime import datetime
from typing import List
from agents.base import AgentEvent, EventType


class WarRoomVisualizer:
    """
    Terminal-based visualizer for agent activity

    Shows:
    - Agent thoughts in real-time
    - Tool usage
    - Theories and debates
    - Timeline of events
    """

    def __init__(self):
        self.events: List[AgentEvent] = []
        self.theories = {}
        self.agent_colors = {
            "Commander": "\033[95m",      # Magenta
            "System Investigator": "\033[94m",  # Blue
            "Code Detective": "\033[93m",       # Yellow
            "Root Cause Synthesizer": "\033[92m",  # Green
        }
        self.reset_color = "\033[0m"

    def on_event(self, event: AgentEvent):
        """Event listener callback"""
        self.events.append(event)
        self.display_event(event)

    def display_event(self, event: AgentEvent):
        """Display a single event"""

        color = self.agent_colors.get(event.agent_name, self.reset_color)
        timestamp = datetime.fromisoformat(event.timestamp).strftime("%H:%M:%S")

        # Format based on event type
        if event.event_type == EventType.THINKING:
            icon = "🤔"
            prefix = "THINKING"
        elif event.event_type == EventType.ACTION:
            icon = "⚡"
            prefix = "ACTION"
        elif event.event_type == EventType.OBSERVATION:
            icon = "👁️"
            prefix = "OBSERVE"
        elif event.event_type == EventType.THEORY:
            icon = "💡"
            prefix = "THEORY"
        elif event.event_type == EventType.CHALLENGE:
            icon = "⚔️"
            prefix = "CHALLENGE"
        elif event.event_type == EventType.DECISION:
            icon = "⚖️"
            prefix = "DECISION"
        else:
            icon = "📝"
            prefix = "EVENT"

        # Print formatted event
        print(f"{color}[{timestamp}] {icon} [{event.agent_name}] {prefix}{self.reset_color}")
        print(f"  {event.content}")

        # Show metadata if present
        if event.metadata:
            interesting_keys = ['confidence', 'tool', 'priority', 'severity']
            metadata_str = ", ".join(
                f"{k}={v}" for k, v in event.metadata.items()
                if k in interesting_keys
            )
            if metadata_str:
                print(f"  \033[90m({metadata_str})\033[0m")

        print()  # Blank line for readability

    def display_summary(self):
        """Display summary at the end"""

        print("\n" + "="*80)
        print("WAR ROOM SUMMARY")
        print("="*80 + "\n")

        # Group events by agent
        events_by_agent = {}
        for event in self.events:
            if event.agent_name not in events_by_agent:
                events_by_agent[event.agent_name] = []
            events_by_agent[event.agent_name].append(event)

        for agent_name, agent_events in events_by_agent.items():
            color = self.agent_colors.get(agent_name, self.reset_color)
            print(f"{color}{agent_name}:{self.reset_color}")

            # Count by event type
            type_counts = {}
            for event in agent_events:
                event_type = event.event_type.value
                type_counts[event_type] = type_counts.get(event_type, 0) + 1

            for event_type, count in type_counts.items():
                print(f"  - {event_type}: {count}")

            print()

        # Timeline
        print("\nTIMELINE:")
        print("-" * 80)

        for event in self.events:
            timestamp = datetime.fromisoformat(event.timestamp).strftime("%H:%M:%S")
            if event.event_type == EventType.DECISION:
                print(f"  {timestamp} | {event.agent_name}: {event.content}")

        print()


class SimpleVisualizer:
    """Simplified visualizer for quick demos"""

    def on_event(self, event: AgentEvent):
        """Simple event display"""
        timestamp = datetime.fromisoformat(event.timestamp).strftime("%H:%M:%S")

        icons = {
            EventType.THINKING: "💭",
            EventType.ACTION: "⚡",
            EventType.OBSERVATION: "👁️",
            EventType.THEORY: "💡",
            EventType.CHALLENGE: "⚔️",
            EventType.DECISION: "✅"
        }

        icon = icons.get(event.event_type, "📝")

        print(f"{timestamp} {icon} [{event.agent_name}] {event.content}")
