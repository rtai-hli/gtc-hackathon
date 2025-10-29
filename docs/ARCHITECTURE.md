# System Architecture

## High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                      Demo Runner                             │
│  - Initializes scenario                                      │
│  - Creates visualizer                                        │
│  - Spawns Incident Commander                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 Incident Commander                           │
│  Phase 1: Assess severity & delegate                         │
│  Phase 2: Coordinate specialists                             │
│  Phase 3: Synthesize findings                                │
│  Phase 4: Determine root cause                               │
└──────┬──────────────────────┬─────────────────┬─────────────┘
       │                      │                 │
       ▼                      ▼                 ▼
┌─────────────┐      ┌─────────────┐    ┌──────────────┐
│   System    │      │    Code     │    │  Root Cause  │
│Investigator │      │  Detective  │    │ Synthesizer  │
│             │      │             │    │              │
│ - Query     │      │ - Check     │    │ - Build      │
│   metrics   │      │   git log   │    │   causal     │
│ - Analyze   │      │ - Correlate │    │   chains     │
│   logs      │      │   deploys   │    │ - Challenge  │
│ - Propose   │      │ - Propose   │    │   theories   │
│   theory    │      │   theory    │    │              │
└──────┬──────┘      └──────┬──────┘    └──────┬───────┘
       │                    │                   │
       │                    │                   │
       └────────────────────┴───────────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │ Theory Board │
                    │              │
                    │ - Theories   │
                    │ - Evidence   │
                    │ - Challenges │
                    └──────────────┘
```

## Event Flow

```
User starts demo
       │
       ▼
Demo creates Incident Commander
       │
       ▼
Commander.run(incident_context)
       │
       ├─► assess_incident()
       │       │
       │       ├─► emit THINKING: "Assessing severity..."
       │       ├─► emit THINKING: "Latency issue detected"
       │       └─► emit DECISION: "Investigation priority: metrics > changes > logs"
       │
       ├─► delegate_investigation()
       │       │
       │       ├─► emit THINKING: "Need to investigate metrics"
       │       ├─► emit ACTION: "Delegating to System Investigator"
       │       └─► (spawn SystemInvestigator in Phase 2)
       │
       ├─► synthesize_findings()
       │       │
       │       ├─► emit THINKING: "Synthesizing findings..."
       │       └─► emit OBSERVE: "Received N theories"
       │
       └─► determine_root_cause()
               │
               ├─► emit THINKING: "Analyzing evidence..."
               ├─► emit THINKING: "Evidence pattern matches: ..."
               └─► emit DECISION: "ROOT CAUSE: ..."
```

## Component Details

### Base Agent (`agents/base.py`)

**Responsibilities**:
- Event emission framework
- Tool registration and execution
- Theory management
- Observable reasoning pattern

**Key Methods**:
- `think()` - Emit reasoning step
- `observe()` - Emit observation
- `propose_theory()` - Submit root cause hypothesis
- `challenge_theory()` - Debate another theory
- `use_tool()` - Execute registered tool

### Incident Commander (`agents/commander.py`)

**Responsibilities**:
- Orchestrate incident response
- Delegate to specialist agents
- Synthesize findings
- Make final determination

**4-Phase Workflow**:
1. **Assessment**: Evaluate severity, determine investigation priorities
2. **Delegation**: Assign tasks to specialist agents (future: actual spawning)
3. **Synthesis**: Gather theories from all agents
4. **Decision**: Determine root cause with confidence score

### Visualizer (`visualizer.py`)

**Two Modes**:

**WarRoomVisualizer**:
- Colored terminal output
- Event type icons (🤔 💡 ⚡ 👁️ ⚔️ ✅)
- Metadata display
- Summary statistics
- Timeline view

**SimpleVisualizer**:
- Minimal output
- One-line per event
- Fast iteration during development

### Scenario System (`scenarios/latency_spike.py`)

**Pre-seeded Data**:
- Incident description
- Metrics time series (latency, errors, connections)
- Log entries with timeline
- Git commit history
- Known root cause (for validation)

**Benefits**:
- Consistent demo
- No external dependencies
- Fast iteration
- Realistic data

## Extension Points

### Adding a New Agent

1. **Create agent class** extending `BaseAgent`
2. **Implement `run()` method** with investigation logic
3. **Register tools** needed by agent
4. **Emit events** showing reasoning
5. **Connect to visualizer**

### Adding a New Tool

1. **Create async function** in `tools/`
2. **Return realistic data** from scenario
3. **Add simulated delay** for realism
4. **Register with agent** via `agent.register_tool()`

### Adding a New Scenario

1. **Create scenario file** in `scenarios/`
2. **Define incident description**
3. **Pre-seed tool data** (metrics, logs, etc.)
4. **Document root cause** for validation
5. **Update demo runner** to use new scenario

## Design Decisions

### Why Event-Driven?

**Pros**:
- Easy to add visualizers
- Decoupled agents
- Observable behavior
- Asynchronous by nature

**Cons**:
- More complex than direct calls
- Event ordering matters

**Decision**: Benefits outweigh complexity for hackathon demo

### Why Async?

**Pros**:
- Concurrent agent operation
- Realistic for production
- Non-blocking tool calls
- Future-proof for LLM calls

**Cons**:
- Async/await learning curve
- Debugging harder

**Decision**: Essential for multi-agent concurrency

### Why Pre-seeded Data?

**Pros**:
- Consistent demos
- No network dependencies
- Fast iteration
- Controlled narrative

**Cons**:
- Less impressive than "real" tools
- Limited scenarios

**Decision**: Right trade-off for 2-hour hackathon

### Why Terminal UI?

**Pros**:
- Zero dependencies
- Fast to implement
- Works anywhere
- Easy to debug

**Cons**:
- Less impressive than web UI
- Limited interactivity

**Decision**: Get it working first, web UI is Phase 3 enhancement

## Performance Characteristics

**Startup**: ~50ms (pure Python, no external deps)

**Incident Response**: ~2-3 seconds (includes simulated delays)

**Memory**: ~10MB (lightweight Python objects)

**CPU**: Minimal (mostly async sleep)

**Scalability**:
- Current: 1 commander + simulated delegation
- Phase 2: 1 commander + 3 specialists running concurrently
- Future: N agents with dynamic spawning

## Data Flow

```
Scenario Data (static)
       │
       ▼
Tool Functions (simulated)
       │
       ▼
Agents (via use_tool)
       │
       ▼
Theory Board (shared state)
       │
       ▼
Commander (synthesis)
       │
       ▼
Final Decision (output)
```

## Error Handling

**Current**:
- Basic try/except in base agent
- Unhandled errors bubble up
- Demo fails fast

**Future**:
- Graceful degradation
- Agent failure recovery
- Partial results handling
- Retry logic for tools

## Testing Strategy

**Manual Testing**:
```bash
python demo.py           # Full test
python demo.py --simple  # Quick test
python demo.py --interactive  # Step-through
```

**Future**:
- Unit tests for agents
- Integration tests for workflows
- Scenario validation
- Event stream testing

## Security Considerations

**Current**: N/A (demo system, no real data)

**If Productionized**:
- Sanitize log outputs
- Validate tool inputs
- Rate limit LLM calls
- Audit agent decisions
- Secure theory board access
