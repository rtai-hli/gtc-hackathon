# Hackathon Development Guide

## 🎯 Current Status: Phase 1 Complete ✅

You have a working foundation with:
- ✅ Observable reasoning framework
- ✅ Event-driven agent architecture
- ✅ Incident Commander implementation
- ✅ Visual terminal output
- ✅ Sample incident scenario

**Demo-ready in**: ~5 minutes
**Full system complete in**: ~90 minutes

---

## 🚀 Quick Demo (Right Now!)

```bash
# Simple output
python demo.py --simple

# Full colored output with summary
python demo.py

# Interactive step-through
python demo.py --interactive
```

---

## 📋 Next 90 Minutes - Implementation Roadmap

### Phase 2: Multi-Agent System (30-45 min)

**Priority 1: System Investigator Agent** (15 min)

```python
# Create agents/investigator.py
class SystemInvestigator(BaseAgent):
    async def run(self, context):
        # Query metrics from scenarios/latency_spike.py
        # Analyze log patterns
        # Propose theory based on data
```

**Files to create**:
1. `agents/investigator.py` - Agent implementation
2. `tools/logs.py` - Log query simulator
3. `tools/metrics.py` - Metrics API simulator

**Integration**:
- Modify `agents/commander.py` to spawn System Investigator
- Pass investigation results back via theory board

**Priority 2: Code Detective Agent** (15 min)

```python
# Create agents/detective.py
class CodeDetective(BaseAgent):
    async def run(self, context):
        # Query git history from scenarios/latency_spike.py
        # Correlate deploys with incident timeline
        # Propose theory based on recent changes
```

**Files to create**:
1. `agents/detective.py` - Agent implementation
2. `tools/git.py` - Git history simulator

**Priority 3: Agent Coordination** (10 min)
- Implement theory board (shared state)
- Commander spawns specialist agents
- Agents submit theories
- Commander synthesizes

---

### Phase 3: Debates & Polish (30 min)

**Priority 1: Root Cause Synthesizer** (15 min)

```python
# Create agents/synthesizer.py
class RootCauseSynthesizer(BaseAgent):
    async def run(self, context):
        # Review all theories
        # Build causal chains
        # Challenge weak theories
        # Rank by evidence strength
```

**Priority 2: Agent Debates** (15 min)
- Agents can challenge each other's theories
- Visual indication of debates
- Commander resolves conflicts
- Show reasoning for final decision

---

### Optional Enhancements (If Time Permits)

**LLM Integration** (20 min)
```python
# Add to base.py
class BaseAgent:
    async def llm_reason(self, prompt):
        # Call Nemotron or Claude
        # Stream thinking tokens
        # Return structured decision
```

**Web UI** (30 min)
```python
# Create web_demo.py with FastAPI
# WebSocket for real-time event streaming
# Simple HTML frontend with event log
```

---

## 🎬 Demo Script (2 min presentation)

**Setup** (10 sec):
```bash
python demo.py
```

**Narration**:

> "This is an autonomous incident response system. We have a production API latency spike..."

> "Watch as the Incident Commander assesses severity, delegates to specialist agents..."

> "The System Investigator finds database connection pool exhaustion in metrics..."

> "The Code Detective correlates this with a recent config change..."

> "The agents debate theories, and the Commander synthesizes evidence..."

> "Root cause identified: pool size reduced from 100 to 50, causing exhaustion."

**Key Points**:
- ✨ Agents show their reasoning (not a black box)
- 🤝 Multi-agent collaboration
- 🔧 Tool integration (logs, metrics, git)
- 🎯 Autonomous problem-solving

---

## 🛠️ Implementation Patterns

### Creating a New Agent

```python
from agents.base import BaseAgent, EventType

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="MyAgent", role="Specialist")

    async def run(self, context):
        # 1. Think about the problem
        self.think("Starting analysis...")

        # 2. Use tools
        result = await self.use_tool("my_tool", param="value")

        # 3. Observe results
        self.observe(f"Found: {result}")

        # 4. Propose theory
        self.propose_theory(
            "Theory description",
            confidence=0.8,
            evidence=["point1", "point2"]
        )

        return {"findings": result}
```

### Adding a Simulated Tool

```python
# In tools/my_tool.py
async def query_my_data(**kwargs):
    """Simulated tool - returns pre-seeded data"""

    # Simulate network delay for realism
    import asyncio
    await asyncio.sleep(0.2)

    # Return realistic data from scenario
    return {
        "data": [...],
        "timestamp": "...",
    }

# Register with agent
agent.register_tool("my_tool", query_my_data)
```

### Theory Board Pattern

```python
# In orchestrator.py or commander.py
class TheoryBoard:
    def __init__(self):
        self.theories = []

    def submit(self, agent_name, theory, confidence, evidence):
        self.theories.append({
            "agent": agent_name,
            "theory": theory,
            "confidence": confidence,
            "evidence": evidence,
            "challenges": []
        })

    def challenge(self, theory_id, agent_name, challenge):
        self.theories[theory_id]["challenges"].append({
            "agent": agent_name,
            "challenge": challenge
        })

    def get_best_theory(self):
        # Sort by confidence and evidence strength
        return max(self.theories, key=lambda t: t["confidence"])
```

---

## 📊 What Makes This Impressive

**For Technical Judges**:
- Clean architecture (event-driven, async)
- Observable AI (shows reasoning)
- Extensible design (easy to add agents)
- Tool integration framework

**For Non-Technical Judges**:
- Visual real-time updates
- Colored output with emojis
- Clear narrative flow
- Realistic incident scenario

**Bonus Points**:
- No complex dependencies (pure Python)
- Fast iteration (modify and see results immediately)
- Demo-ready at any time
- Scales from simple to complex

---

## 🐛 Common Issues

**Import errors**: Make sure you're in the project root directory

**Events not showing**: Check that `add_event_listener` is called before `run()`

**Wrong root cause**: Verify `INCIDENT["symptom"]` contains expected keywords

**Async errors**: All agent methods must be `async def` and called with `await`

---

## 💡 Expansion Ideas

**More Scenarios**:
- Memory leak detection
- Security breach investigation
- Service degradation
- Cascading failure

**More Agents**:
- Security Analyst (threat hunting)
- Database Expert (query optimization)
- Network Specialist (connectivity issues)

**More Tools**:
- APM traces
- Cloud metrics
- Container logs
- Deployment pipelines

**Enhanced Debates**:
- Multi-round discussions
- Vote-based consensus
- Confidence scoring
- Evidence weighting

---

## ✅ Pre-Demo Checklist

- [ ] Test all three demo modes
- [ ] Verify output is readable on projector
- [ ] Have backup scenario ready
- [ ] Prepare 1-sentence explanation
- [ ] Know how to kill/restart demo quickly
- [ ] Have architecture diagram ready (optional)

**Emergency Reset**:
```bash
# Kill hung process
Ctrl+C

# Quick restart
python demo.py
```

---

## 🎯 Success Metrics

**Minimum Viable Demo**:
- ✅ One agent shows reasoning
- ✅ Visual output works
- ✅ Identifies root cause

**Good Demo**:
- ✅ 2+ agents collaborate
- ✅ Tools return realistic data
- ✅ Clear reasoning chain

**Great Demo**:
- ✅ 4 agents with distinct roles
- ✅ Agents debate theories
- ✅ LLM integration
- ✅ Web UI (optional)

---

Good luck! You've got a solid foundation. Focus on making it work first, impressive second. 🚀
