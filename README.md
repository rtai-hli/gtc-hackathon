# Incident Response War Room - Multi-Agent LLM Demo

A hackathon-ready multi-agent system powered by **NVIDIA Nemotron Super 49B** that simulates autonomous incident response with observable reasoning, tool integration, and agent collaboration.

## 🎯 Demo Highlights

- **49B LLM Commander**: Powered by nvidia/llama-3.3-nemotron-super-49b-v1.5 for enterprise-grade analysis
- **Observable Reasoning**: See agents think out loud in real-time with streaming reasoning tokens
- **Multi-Step Workflows**: Autonomous investigation with 4 distinct phases
- **Tool Integration**: Simulated logs, metrics, and git history analysis
- **Agent Collaboration**: Multiple specialized agents (future: debate and consensus)
- **Visual Impact**: Color-coded terminal output with emoji indicators
- **85% Confidence**: LLM-powered root cause determination with evidence-based analysis

## 🏗️ Project Structure

```
gtc-hackathon/
├── agents/              # Core agent framework
│   ├── base.py         # Base agent with observable thinking
│   ├── commander.py    # Incident Commander (orchestrator)
│   ├── llm_wrapper.py  # NVIDIA LLM integration
│   └── visualizer.py   # Real-time visualization
├── scenarios/          # Pre-seeded incident scenarios
│   └── latency_spike.py
├── templates/          # Web UI templates (nonprofit demo)
├── examples/           # Example scripts and utilities
├── tests/              # Test suites
├── docs/               # Documentation
├── incidents/          # Generated incident reports
├── demo.py            # Main CLI demo
└── web_app.py         # Web UI demo
```

## 🚀 Quick Start

### Run the basic demo:
```bash
python demo.py
```

### Run interactive mode (step through phases):
```bash
python demo.py --interactive
```

### Run simple mode (minimal output):
```bash
python demo.py --simple
```

## 🎭 Agent Roles

### ✅ Implemented

**Incident Commander** (`agents/commander.py`)
- Orchestrates incident response
- Assesses severity and delegates tasks
- Synthesizes findings from all agents
- Makes final root cause determination

### 🚧 Coming Soon

**System Investigator**
- Queries infrastructure metrics
- Analyzes system logs
- Identifies performance anomalies

**Code Detective**
- Analyzes recent deployments
- Reviews git history
- Correlates code changes with incidents

**Root Cause Synthesizer**
- Builds causal chains from evidence
- Challenges theories with counter-evidence
- Proposes alternative explanations

## 📊 Event Types

Each agent emits observable events:

- 🤔 **THINKING**: Internal reasoning steps
- ⚡ **ACTION**: Tool usage and operations
- 👁️ **OBSERVE**: Observations from tool results
- 💡 **THEORY**: Root cause hypotheses
- ⚔️ **CHALLENGE**: Debates and counter-arguments
- ✅ **DECISION**: Final determinations

## 🎬 Demo Scenario

**Incident**: API latency spike from 200ms to 3000ms

**Pre-seeded Evidence**:
- Metrics showing database connection pool exhaustion
- Logs with connection timeout errors
- Git history with recent pool size reduction
- Recent code change adding eager loading

**Root Cause**: Database connection pool exhaustion due to config change reducing pool from 100 to 50 connections, combined with code change increasing connection hold time.

## 🔧 Extending the System

### Add a new agent:

```python
from agents.base import BaseAgent, EventType

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="MyAgent", role="Specialist")

    async def run(self, context):
        self.think("Starting analysis...")
        result = await self.use_tool("my_tool", param="value")
        self.observe(f"Found: {result}")
        return {"findings": result}
```

### Register a tool:

```python
async def my_tool(**kwargs):
    # Tool implementation
    return "result"

agent.register_tool("my_tool", my_tool)
```

### Add event listener:

```python
def my_listener(event):
    print(f"Event: {event}")

agent.add_event_listener(my_listener)
```

## 🎯 Next Steps for Hackathon

### Phase 1 (Completed ✅)
- [x] Base agent framework
- [x] Incident Commander implementation
- [x] Observable thinking pattern
- [x] Event system
- [x] Basic visualization
- [x] Demo scenario

### Phase 2 (Next 30-45 min)
- [ ] Implement System Investigator agent
- [ ] Add simulated tools (logs, metrics)
- [ ] Multi-agent coordination
- [ ] Theory board for debates

### Phase 3 (Final 30 min)
- [ ] Add Code Detective agent
- [ ] Implement agent debates
- [ ] Enhanced visualization
- [ ] Polish demo flow

### Optional Enhancements
- [x] LLM integration - **49B Nemotron Super Commander** ✅
- [ ] Web UI with real-time updates
- [ ] More complex scenarios
- [ ] Performance metrics

## 📚 Documentation

### Quick Start
- **[Quick Start Guide](docs/QUICK_START_49B.md)** - Get running in 30 seconds
- **[49B Commander Upgrade](docs/COMMANDER_49B_UPGRADE.md)** - What changed and how to use it
- **[Hackathon Guide](docs/HACKATHON_GUIDE.md)** - Original development roadmap

### Architecture & Design
- **[Agent Architecture](docs/AGENT_ARCHITECTURE.md)** - Comprehensive Mermaid diagrams
- **[Mermaid Diagrams](docs/MERMAID_DIAGRAMS.md)** - Quick reference for presentations
- **[System Architecture](docs/ARCHITECTURE.md)** - Original design document
- **[NVIDIA Integration](docs/NVIDIA_INTEGRATION.md)** - LLM integration details

### Testing
- **[Test 49B Commander](tests/test_49b_commander.py)** - Comprehensive test suite
- **[Compare Models](tests/compare_models.py)** - Model comparison utility

## 💡 Design Decisions

**Observable Reasoning Pattern**: Every agent emits structured events showing their thinking process. This makes the demo visually impressive and helps debug agent behavior.

**Event-Driven Architecture**: Agents communicate through events rather than direct calls. This enables easy addition of new agents and flexible coordination.

**Simulated Tools**: Pre-seeded data ensures consistent, impressive demos without network dependencies or complex infrastructure.

**Async by Default**: All agent operations are async, enabling future parallel investigation and real concurrent agent debates.

**Hackathon-Optimized**: Fast to iterate, impressive to demo, easy to extend.

## 📝 License

MIT - Built for NVIDIA GTC DC Hackathon 2025
