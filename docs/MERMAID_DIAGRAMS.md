# Mermaid Diagrams - Quick Reference

Quick access to all Mermaid diagrams for presentations and documentation.

---

## 🎯 System Overview

High-level architecture showing all components and their relationships.

```mermaid
graph TB
    subgraph "Demo Layer"
        Demo[demo.py<br/>Demo Runner]
        Visualizer[visualizer.py<br/>War Room Visualizer]
    end

    subgraph "Agent Layer"
        Commander[IncidentCommander<br/>49B Nemotron Super]
        BaseAgent[BaseAgent<br/>Observable Framework]
        Commander -->|inherits| BaseAgent
    end

    subgraph "LLM Layer"
        LLMWrapper[ReasoningLLM<br/>NVIDIA API Wrapper]
        NVIDIA[NVIDIA API<br/>llama-3.3-nemotron-super-49b-v1.5]
        LLMWrapper -->|calls| NVIDIA
    end

    subgraph "Data Layer"
        Scenario[Scenario Data<br/>latency_spike.py]
        Context[Agent Context<br/>Runtime State]
    end

    Demo -->|creates| Commander
    Demo -->|creates| Visualizer
    Demo -->|loads| Scenario
    Commander -->|uses| LLMWrapper
    Commander -->|emits events| Visualizer
    BaseAgent -->|stores| Context
    Commander -->|reads| Scenario

    style Commander fill:#4a90e2,stroke:#2e5c8a,color:#fff
    style LLMWrapper fill:#e27d60,stroke:#a84f3d,color:#fff
    style BaseAgent fill:#6fba82,stroke:#4a7c59,color:#fff
    style NVIDIA fill:#f39c12,stroke:#d68910,color:#fff
```

**Use for**: High-level system explanation, architecture overview presentations

---

## 🔄 Commander Workflow

Complete 4-phase incident response workflow with decision trees.

```mermaid
flowchart TD
    Start([Demo starts Commander]) --> Init[Initialize Commander<br/>with 49B LLM]
    Init --> Run[run context]

    Run --> Phase1{Phase 1:<br/>Assess Incident}

    Phase1 --> ExtractDetails[Extract incident details<br/>symptom, severity, service]
    ExtractDetails --> ThinkAssess[🤔 THINKING:<br/>Beginning assessment]
    ThinkAssess --> AnalyzeSymptom{Analyze<br/>symptom type}

    AnalyzeSymptom -->|Latency| LatencyPriority[Priority:<br/>metrics > changes > logs]
    AnalyzeSymptom -->|Error| ErrorPriority[Priority:<br/>logs > changes > metrics]
    AnalyzeSymptom -->|Other| DefaultPriority[Priority:<br/>logs > metrics > changes]

    LatencyPriority --> DecidePriority[⚖️ DECISION:<br/>Investigation priority]
    ErrorPriority --> DecidePriority
    DefaultPriority --> DecidePriority

    DecidePriority --> Phase2{Phase 2:<br/>Delegate Investigation}

    Phase2 --> LoopAreas[For each investigation area]
    LoopAreas --> ThinkArea[🤔 THINKING:<br/>Need to investigate area]
    ThinkArea --> MapAgent[Map area to specialist agent]
    MapAgent --> ActionDelegate[⚡ ACTION:<br/>Delegating to agent]
    ActionDelegate --> CreateTask[Create task record]
    CreateTask --> MoreAreas{More areas?}
    MoreAreas -->|Yes| LoopAreas
    MoreAreas -->|No| SimulateWait[Simulate wait 0.5s]

    SimulateWait --> Phase3{Phase 3:<br/>Synthesize Findings}

    Phase3 --> ThinkSynth[🤔 THINKING:<br/>Synthesizing findings]
    ThinkSynth --> SimulateGather[Simulate gathering theories<br/>wait 0.3s]
    SimulateGather --> ObserveTheories[👁️ OBSERVE:<br/>Received theories]

    ObserveTheories --> Phase4{Phase 4:<br/>Determine Root Cause}

    Phase4 --> ThinkAnalyze[🤔 THINKING:<br/>Analyzing all evidence]
    ThinkAnalyze --> CheckLLM{LLM client<br/>available?}

    CheckLLM -->|Yes| ThinkLLM[🤔 THINKING:<br/>Using LLM reasoning]
    CheckLLM -->|No| FallbackRules[Use fallback<br/>rule-based analysis]

    ThinkLLM --> BuildPrompt[Build incident prompt<br/>with context]
    BuildPrompt --> CallLLM[Call llm_reason]
    CallLLM --> StreamReasoning[Stream reasoning tokens<br/>emit THINKING events]
    StreamReasoning --> GetResponse[Get full response]
    GetResponse --> SetConfidence[Set confidence: 85%]

    FallbackRules --> RuleAnalysis[Pattern matching<br/>on symptom]
    RuleAnalysis --> SetLowConfidence[Set confidence: 50%]

    SetConfidence --> ThinkComplete[🤔 THINKING:<br/>Analysis complete]
    SetLowConfidence --> ThinkComplete

    ThinkComplete --> DecideRoot[⚖️ DECISION:<br/>ROOT CAUSE with confidence]

    DecideRoot --> Return[Return result dict:<br/>status, root_cause, timeline]
    Return --> End([Demo displays result])

    style Phase1 fill:#e3f2fd
    style Phase2 fill:#fff3e0
    style Phase3 fill:#f3e5f5
    style Phase4 fill:#e8f5e9
    style CallLLM fill:#4a90e2,stroke:#2e5c8a,color:#fff
    style StreamReasoning fill:#4a90e2,stroke:#2e5c8a,color:#fff
```

**Use for**: Detailed workflow explanation, demo walkthrough, technical deep-dive

---

## 📡 Event Flow Sequence

Real-time event communication between components.

```mermaid
sequenceDiagram
    participant Demo as Demo Runner
    participant Viz as Visualizer
    participant Cmd as Commander
    participant LLM as ReasoningLLM
    participant API as NVIDIA API

    Demo->>Cmd: create(llm_client)
    Demo->>Cmd: add_event_listener(visualizer)
    Demo->>Cmd: run(incident_context)

    activate Cmd

    rect rgb(200, 220, 255)
        Note over Cmd: Phase 1: Assessment
        Cmd->>Cmd: assess_incident()
        Cmd->>Viz: emit_event(THINKING)
        Viz-->>Demo: display("Beginning assessment...")
        Cmd->>Viz: emit_event(DECISION)
        Viz-->>Demo: display("Priority: metrics > changes > logs")
    end

    rect rgb(255, 220, 200)
        Note over Cmd: Phase 2: Delegation
        Cmd->>Cmd: delegate_investigation()
        loop for each investigation area
            Cmd->>Viz: emit_event(THINKING)
            Cmd->>Viz: emit_event(ACTION)
            Viz-->>Demo: display("Delegating to System Investigator")
        end
    end

    rect rgb(220, 255, 200)
        Note over Cmd: Phase 3: Synthesis
        Cmd->>Cmd: synthesize_findings()
        Cmd->>Viz: emit_event(THINKING)
        Cmd->>Viz: emit_event(OBSERVATION)
        Viz-->>Demo: display("Received theories...")
    end

    rect rgb(255, 255, 200)
        Note over Cmd: Phase 4: Root Cause
        Cmd->>Cmd: determine_root_cause()
        Cmd->>Viz: emit_event(THINKING)

        Cmd->>LLM: llm_reason(prompt, system_context)
        activate LLM
        LLM->>API: chat.completions.create(stream=True)
        activate API

        loop streaming response
            API-->>LLM: chunk(type="reasoning")
            LLM-->>Cmd: reasoning chunk
            Cmd->>Viz: emit_event(THINKING, llm_reasoning=True)
            Viz-->>Demo: display(reasoning)
        end

        loop streaming response
            API-->>LLM: chunk(type="content")
            LLM-->>Cmd: content chunk
        end

        deactivate API
        LLM-->>Cmd: full response
        deactivate LLM

        Cmd->>Viz: emit_event(DECISION)
        Viz-->>Demo: display("ROOT CAUSE: ...")
    end

    Cmd-->>Demo: return result
    deactivate Cmd
```

**Use for**: Understanding event-driven architecture, debugging, timing analysis

---

## 🏗️ Class Structure

Object-oriented design with inheritance and relationships.

```mermaid
classDiagram
    class EventType {
        <<enumeration>>
        +THINKING
        +ACTION
        +OBSERVATION
        +THEORY
        +CHALLENGE
        +DECISION
    }

    class AgentEvent {
        +string agent_name
        +EventType event_type
        +string content
        +dict metadata
        +datetime timestamp
        +to_dict() dict
        +__str__() string
    }

    class BaseAgent {
        +string name
        +string role
        +ReasoningLLM llm_client
        +list event_listeners
        +dict tools
        +dict context
        +list conversation_history
        +register_tool(name, callable)
        +add_event_listener(listener)
        +emit_event(type, content, metadata) AgentEvent
        +think(thought, **metadata) AgentEvent
        +observe(observation, **metadata) AgentEvent
        +propose_theory(theory, confidence, **metadata) AgentEvent
        +challenge_theory(id, challenge, **metadata) AgentEvent
        +decide(decision, **metadata) AgentEvent
        +use_tool(name, **kwargs) Any
        +run(context) dict
        +update_context(**kwargs)
        +llm_reason(prompt, system_context, emit) string
    }

    class IncidentCommander {
        +string investigation_phase
        +list theories
        +list assigned_tasks
        +run(context) dict
        +assess_incident(incident)
        +delegate_investigation(incident)
        +synthesize_findings()
        +determine_root_cause() string
        +receive_theory(theory)
        -_map_area_to_agent(area) string
        -_fallback_root_cause_analysis(incident) string
    }

    class ReasoningLLM {
        +string model
        +int min_thinking_tokens
        +int max_thinking_tokens
        +AsyncOpenAI client
        +think_and_respond(messages, temperature, top_p, max_tokens, stream) AsyncIterator
        +simple_query(prompt, system_message, **kwargs) string
    }

    BaseAgent --> EventType : uses
    BaseAgent --> AgentEvent : creates
    IncidentCommander --|> BaseAgent : inherits
    IncidentCommander --> ReasoningLLM : uses
    BaseAgent --> ReasoningLLM : uses

    note for BaseAgent "Observable reasoning pattern\nTool execution framework\nEvent-driven architecture"
    note for IncidentCommander "4-phase incident response\nLLM-powered analysis\n49B Nemotron Super model"
    note for ReasoningLLM "Streaming reasoning tokens\nNVIDIA API integration\nAsync/await support"
```

**Use for**: Code structure explanation, OOP concepts, API design

---

## 🔄 State Machine

Commander state transitions throughout incident response.

```mermaid
stateDiagram-v2
    [*] --> Initial: Commander created

    Initial --> Assessing: run() called

    state Assessing {
        [*] --> ExtractingDetails
        ExtractingDetails --> AnalyzingSymptom
        AnalyzingSymptom --> SettingPriority
        SettingPriority --> [*]
    }

    Assessing --> Delegating: assessment complete

    state Delegating {
        [*] --> IdentifyingAreas
        IdentifyingAreas --> MappingAgents
        MappingAgents --> CreatingTasks
        CreatingTasks --> WaitingResults
        WaitingResults --> [*]
    }

    Delegating --> Synthesizing: delegation complete

    state Synthesizing {
        [*] --> GatheringTheories
        GatheringTheories --> ReviewingEvidence
        ReviewingEvidence --> [*]
    }

    Synthesizing --> Concluding: synthesis complete

    state Concluding {
        [*] --> CheckingLLM
        CheckingLLM --> LLMAnalysis: LLM available
        CheckingLLM --> RuleBasedAnalysis: LLM unavailable

        state LLMAnalysis {
            [*] --> BuildingPrompt
            BuildingPrompt --> StreamingReasoning
            StreamingReasoning --> CollectingResponse
            CollectingResponse --> [*]
        }

        RuleBasedAnalysis --> [*]
        LLMAnalysis --> CalculatingConfidence
        CalculatingConfidence --> [*]
    }

    Concluding --> Resolved: root cause determined
    Resolved --> [*]

    note right of Assessing
        investigation_phase = "initial"
        Emits: THINKING, DECISION
    end note

    note right of Delegating
        investigation_phase = "delegating"
        Emits: THINKING, ACTION
    end note

    note right of Synthesizing
        investigation_phase = "synthesizing"
        Emits: THINKING, OBSERVATION
    end note

    note right of Concluding
        investigation_phase = "concluding"
        Emits: THINKING, DECISION
        Uses: 49B LLM model
    end note
```

**Use for**: State management explanation, phase transitions, status tracking

---

## 🔌 LLM Integration Flow

Detailed streaming communication with NVIDIA API.

```mermaid
sequenceDiagram
    participant Agent as BaseAgent/Commander
    participant LLM as ReasoningLLM
    participant Client as AsyncOpenAI
    participant API as NVIDIA API

    Agent->>Agent: llm_reason(prompt, system_context)

    Note over Agent: Build message list
    Agent->>Agent: messages = [system, user]

    Agent->>LLM: think_and_respond(messages)
    activate LLM

    Note over LLM: Add /think system message if needed
    LLM->>LLM: messages = [/think] + messages

    Note over LLM: Configure reasoning tokens
    LLM->>LLM: extra_body = {<br/>min: 512, max: 2048<br/>}

    LLM->>Client: chat.completions.create(<br/>model=49B,<br/>stream=True,<br/>extra_body<br/>)
    activate Client

    Client->>API: POST /v1/chat/completions
    activate API

    Note over API: Model: nvidia/llama-3.3-nemotron-super-49b-v1.5

    loop Streaming chunks
        API-->>Client: chunk with reasoning_content
        Client-->>LLM: delta.reasoning_content

        alt reasoning chunk
            LLM-->>Agent: {"type": "reasoning", "text": ...}
            Agent->>Agent: emit_event(THINKING, llm_reasoning=True)
            Note over Agent: Reasoning displayed in terminal
        else content chunk
            API-->>Client: chunk with content
            Client-->>LLM: delta.content
            LLM-->>Agent: {"type": "content", "text": ...}
            Agent->>Agent: content_parts.append(text)
        end
    end

    deactivate API
    deactivate Client

    LLM-->>Agent: full content
    deactivate LLM

    Agent->>Agent: Store in conversation_history
    Agent->>Agent: return full_content
```

**Use for**: LLM integration explanation, streaming architecture, API usage

---

## 📊 Event Types Reference

Quick visual reference for all event types and their usage.

```mermaid
graph LR
    subgraph "Event Types"
        Thinking[🤔 THINKING<br/>Internal reasoning]
        Action[⚡ ACTION<br/>Tool usage/delegation]
        Observation[👁️ OBSERVE<br/>Evidence gathering]
        Theory[💡 THEORY<br/>Root cause hypothesis]
        Challenge[⚔️ CHALLENGE<br/>Theory debate]
        Decision[⚖️ DECISION<br/>Final determination]
    end

    subgraph "Metadata Examples"
        M1[severity: 'high'<br/>priority: list]
        M2[tool: 'name'<br/>args: dict]
        M3[theory_count: int<br/>source: 'agent']
        M4[confidence: 0.85<br/>pattern: 'string']
        M5[theory_id: 'id'<br/>challenge: 'text']
        M6[confidence: float<br/>root_cause: 'string']
    end

    Thinking -.-> M1
    Action -.-> M2
    Observation -.-> M3
    Theory -.-> M4
    Challenge -.-> M5
    Decision -.-> M6

    style Thinking fill:#e1bee7
    style Action fill:#fff9c4
    style Observation fill:#b2ebf2
    style Theory fill:#c5e1a5
    style Challenge fill:#ffccbc
    style Decision fill:#f8bbd0
```

**Use for**: Event system explanation, metadata reference, debugging guide

---

## 🔧 Component Interaction

Data flow and component relationships during runtime.

```mermaid
graph TB
    subgraph "Demo Initialization"
        LoadEnv[Load .env<br/>API Keys]
        CreateViz[Create Visualizer<br/>WarRoomVisualizer]
        CreateLLM[Create LLM Client<br/>49B model]
        CreateCmd[Create Commander<br/>with LLM]
        AttachListener[Attach visualizer<br/>as event listener]
    end

    subgraph "Runtime Execution"
        RunCmd[Commander.run<br/>incident context]
        EmitEvents[Emit events<br/>THINKING, ACTION,<br/>OBSERVATION, DECISION]
        VisDisplay[Visualizer displays<br/>colored terminal output]
        LLMCall[LLM reasoning<br/>stream tokens]
    end

    subgraph "Data Flow"
        IncidentData[Incident Data<br/>from scenario]
        ContextStore[Context Storage<br/>investigation_priority,<br/>assigned_tasks, theories]
        ConvHistory[Conversation History<br/>prompt, reasoning, response]
        ResultDict[Result Dictionary<br/>status, root_cause, timeline]
    end

    LoadEnv --> CreateLLM
    CreateLLM --> CreateCmd
    CreateViz --> AttachListener
    CreateCmd --> AttachListener
    AttachListener --> RunCmd

    IncidentData --> RunCmd
    RunCmd --> EmitEvents
    EmitEvents --> VisDisplay
    RunCmd --> LLMCall
    LLMCall --> EmitEvents

    RunCmd --> ContextStore
    LLMCall --> ConvHistory
    RunCmd --> ResultDict

    style CreateLLM fill:#4a90e2,stroke:#2e5c8a,color:#fff
    style LLMCall fill:#4a90e2,stroke:#2e5c8a,color:#fff
    style EmitEvents fill:#6fba82,stroke:#4a7c59,color:#fff
    style VisDisplay fill:#e27d60,stroke:#a84f3d,color:#fff
```

**Use for**: Runtime behavior explanation, data flow tracking, initialization sequence

---

## 📝 Usage Tips

### For Presentations
1. **Start with System Overview** - Show high-level architecture
2. **Walk through Workflow** - Use Commander Workflow diagram
3. **Show Real-time Events** - Event Flow Sequence diagram
4. **Explain LLM Integration** - LLM Integration Flow diagram

### For Documentation
- Embed diagrams in README or wiki pages
- Use as reference for new developers
- Include in architecture decision records

### For Development
- Use State Machine for debugging phase transitions
- Reference Class Structure for API design
- Consult Event Types for proper event usage

### Rendering Diagrams
```bash
# Install Mermaid CLI (optional)
npm install -g @mermaid-js/mermaid-cli

# Generate images from diagrams
mmdc -i MERMAID_DIAGRAMS.md -o diagrams/

# Or use online editor
# https://mermaid.live/
```

### GitHub Support
GitHub natively renders Mermaid in markdown files. Simply push this file and diagrams will display automatically.

---

## 🎯 Quick Links

- Full Documentation: `AGENT_ARCHITECTURE.md`
- Code Implementation: `agents/` directory
- Quick Start: `QUICK_START_49B.md`
- Hackathon Guide: `HACKATHON_GUIDE.md`

---

**All diagrams maintained for GTC Hackathon 2024**
