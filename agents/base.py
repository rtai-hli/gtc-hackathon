"""
Base Agent Framework - Observable Reasoning Pattern

Each agent can:
- Think out loud (emit reasoning steps)
- Use tools (simulated or real)
- Propose theories
- Challenge other theories
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


class EventType(Enum):
    THINKING = "thinking"
    ACTION = "action"
    OBSERVATION = "observation"
    THEORY = "theory"
    CHALLENGE = "challenge"
    DECISION = "decision"


class AgentEvent:
    """Observable event emitted by agents"""

    def __init__(
        self,
        agent_name: str,
        event_type: EventType,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.agent_name = agent_name
        self.event_type = event_type
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent": self.agent_name,
            "type": self.event_type.value,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }

    def __str__(self) -> str:
        return f"[{self.agent_name}] {self.event_type.value}: {self.content}"


class BaseAgent:
    """
    Base class for all war room agents

    Provides:
    - Observable thinking pattern
    - Tool execution framework
    - Theory management
    """

    def __init__(self, name: str, role: str, llm_client=None):
        self.name = name
        self.role = role
        self.llm_client = llm_client
        self.event_listeners = []
        self.tools = {}
        self.context = {}
        self.conversation_history = []

    def register_tool(self, tool_name: str, tool_callable):
        """Register a tool this agent can use"""
        self.tools[tool_name] = tool_callable

    def add_event_listener(self, listener):
        """Add callback for agent events"""
        self.event_listeners.append(listener)

    def emit_event(self, event_type: EventType, content: str, metadata: Optional[Dict] = None):
        """Emit an observable event"""
        event = AgentEvent(self.name, event_type, content, metadata)

        # Notify all listeners
        for listener in self.event_listeners:
            listener(event)

        return event

    def think(self, thought: str, **metadata):
        """Emit a thinking step"""
        return self.emit_event(EventType.THINKING, thought, metadata)

    def observe(self, observation: str, **metadata):
        """Emit an observation"""
        return self.emit_event(EventType.OBSERVATION, observation, metadata)

    def propose_theory(self, theory: str, confidence: float = 0.5, **metadata):
        """Propose a root cause theory"""
        metadata['confidence'] = confidence
        return self.emit_event(EventType.THEORY, theory, metadata)

    def challenge_theory(self, theory_id: str, challenge: str, **metadata):
        """Challenge another agent's theory"""
        metadata['theory_id'] = theory_id
        return self.emit_event(EventType.CHALLENGE, challenge, metadata)

    def decide(self, decision: str, **metadata):
        """Make a decision"""
        return self.emit_event(EventType.DECISION, decision, metadata)

    async def use_tool(self, tool_name: str, **kwargs) -> Any:
        """Use a registered tool"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not registered")

        self.emit_event(
            EventType.ACTION,
            f"Using tool: {tool_name}",
            {"tool": tool_name, "args": kwargs}
        )

        # Execute tool (async)
        result = await self.tools[tool_name](**kwargs)

        self.observe(
            f"Tool '{tool_name}' returned results",
            {"tool": tool_name, "result_summary": str(result)[:100]}
        )

        return result

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main agent execution loop

        Override this in subclasses to implement agent-specific logic
        """
        raise NotImplementedError("Subclasses must implement run()")

    def update_context(self, **kwargs):
        """Update agent's working context"""
        self.context.update(kwargs)

    async def llm_reason(
        self,
        prompt: str,
        system_context: Optional[str] = None,
        emit_reasoning: bool = True
    ) -> str:
        """
        Use LLM to reason about a problem

        Args:
            prompt: The question or problem to reason about
            system_context: Optional system context/instructions
            emit_reasoning: Whether to emit reasoning steps as events

        Returns:
            The LLM's response content
        """
        if not self.llm_client:
            raise ValueError(f"Agent {self.name} has no LLM client configured")

        # Build messages
        messages = []
        if system_context:
            messages.append({"role": "system", "content": system_context})
        messages.append({"role": "user", "content": prompt})

        # Track response
        reasoning_parts = []
        content_parts = []

        # Stream response and emit events
        async for chunk in self.llm_client.think_and_respond(messages):
            if chunk["type"] == "reasoning":
                reasoning_parts.append(chunk["text"])
                if emit_reasoning:
                    # Emit reasoning as thinking events
                    self.think(chunk["text"], llm_reasoning=True)
            elif chunk["type"] == "content":
                content_parts.append(chunk["text"])

        # Store in conversation history
        full_content = "".join(content_parts)
        self.conversation_history.append({
            "prompt": prompt,
            "reasoning": "".join(reasoning_parts),
            "response": full_content
        })

        return full_content
