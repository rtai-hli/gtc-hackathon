# NVIDIA Nemotron Integration Guide

This document describes the integration of NVIDIA's `nvidia-nemotron-nano-9b-v2` model with reasoning capabilities into the Incident Response War Room demo.

## Overview

The project now uses NVIDIA's Nemotron model with thinking/reasoning token support to provide intelligent root cause analysis for production incidents.

## Key Features

- **Reasoning Token Support**: The model can "think out loud" before responding, showing its reasoning process
- **Streaming Reasoning**: See the model's thinking process in real-time as it analyzes incidents
- **Fallback Mechanism**: Gracefully falls back to rule-based analysis if LLM is unavailable
- **Observable Events**: All LLM reasoning is emitted as observable events for visualization

## Architecture

### Components

1. **`agents/llm_wrapper.py`**: Clean async wrapper for NVIDIA Nemotron API
   - Handles reasoning token configuration
   - Supports streaming responses
   - Separates reasoning content from final response

2. **`agents/base.py`**: Enhanced BaseAgent with LLM capabilities
   - `llm_reason()` method for LLM-powered reasoning
   - Conversation history tracking
   - Event emission for reasoning steps

3. **`agents/commander.py`**: Updated IncidentCommander
   - Uses LLM for root cause analysis
   - Falls back to rule-based logic if LLM unavailable
   - Emits reasoning as observable events

4. **`demo.py`**: Updated demo runner
   - Automatically initializes LLM client
   - Graceful degradation if API key missing

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

The API key is already configured in `.env`:

```bash
# .env file
NVIDIA_API_KEY=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
NGC_API_KEY=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
```

Both `NVIDIA_API_KEY` and `NGC_API_KEY` are supported (for compatibility).

### 3. Load Environment Variables

The demo automatically loads from `.env`, but you can also export manually:

```bash
export NVIDIA_API_KEY="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"
```

## Usage

### Run the Demo

```bash
# Full demo with LLM reasoning
python demo.py

# Simple visualizer
python demo.py --simple

# Interactive mode
python demo.py --interactive
```

### Example Output

When running with LLM enabled, you'll see:

```
🧠 Initializing NVIDIA Nemotron LLM with reasoning capabilities...
✓ LLM client ready

[Commander] thinking: Analyzing all evidence to determine root cause...
[Commander] thinking: Using LLM reasoning to analyze incident...
[Commander] thinking: <reasoning content from model>
[Commander] decision: ROOT CAUSE: <LLM-determined root cause>
```

## Using the LLM Wrapper Directly

### Basic Usage

```python
from agents.llm_wrapper import create_reasoning_llm

# Create LLM client
llm = create_reasoning_llm(
    model="nvidia/nvidia-nemotron-nano-9b-v2",
    min_thinking_tokens=512,
    max_thinking_tokens=2048
)

# Simple query
response = await llm.simple_query(
    "What could cause database latency spikes?",
    system_message="You are a database expert."
)
print(response)
```

### Streaming Reasoning

```python
messages = [
    {"role": "user", "content": "Analyze this latency spike..."}
]

async for chunk in llm.think_and_respond(messages):
    if chunk["type"] == "reasoning":
        print(f"[Thinking] {chunk['text']}", end="")
    elif chunk["type"] == "content":
        print(f"[Response] {chunk['text']}", end="")
```

### Integration with Agents

```python
from agents.base import BaseAgent
from agents.llm_wrapper import create_reasoning_llm

# Create agent with LLM
llm = create_reasoning_llm()
agent = BaseAgent(name="Analyst", role="Incident Analyst", llm_client=llm)

# Use LLM reasoning
result = await agent.llm_reason(
    prompt="What's the root cause?",
    system_context="You are an SRE expert.",
    emit_reasoning=True  # Emit reasoning as events
)
```

## Model Configuration

### Reasoning Token Budgets

The model supports configurable thinking tokens:

- **`min_thinking_tokens`**: Minimum tokens for reasoning (default: 512)
- **`max_thinking_tokens`**: Maximum tokens for reasoning (default: 2048)

Higher budgets allow more detailed reasoning but increase latency and cost.

### Temperature and Sampling

```python
llm = create_reasoning_llm()

async for chunk in llm.think_and_respond(
    messages,
    temperature=0.6,  # Creativity (0.0-1.0)
    top_p=0.95,       # Nucleus sampling
    max_tokens=2048   # Max response tokens
):
    ...
```

## API Reference

### `ReasoningLLM`

Main LLM wrapper class with reasoning support.

**Methods:**

- `think_and_respond(messages, **kwargs)`: Stream reasoning + response
- `simple_query(prompt, system_message, **kwargs)`: Simple synchronous query

### `BaseAgent.llm_reason()`

Use LLM for agent reasoning.

**Parameters:**
- `prompt`: Question/problem to reason about
- `system_context`: Optional system instructions
- `emit_reasoning`: Whether to emit reasoning as events (default: True)

**Returns:** Response content string

## Example: ngc_example.py

The original example has been preserved in `ngc_example.py` showing direct API usage:

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="$API_KEY_REQUIRED_IF_EXECUTING_OUTSIDE_NGC"
)

completion = client.chat.completions.create(
    model="nvidia/nvidia-nemotron-nano-9b-v2",
    messages=[{"role":"system","content":"/think"}],
    stream=True,
    extra_body={
        "min_thinking_tokens": 1024,
        "max_thinking_tokens": 2048
    }
)
```

## Troubleshooting

### "No API key found" Error

Ensure your `.env` file has `NVIDIA_API_KEY` or `NGC_API_KEY` set:

```bash
echo $NVIDIA_API_KEY  # Should print your key
```

### LLM Initialization Failed

The demo gracefully falls back to rule-based reasoning:

```
⚠️  Failed to initialize LLM: <error>
   Falling back to rule-based reasoning
```

Common causes:
- Invalid API key
- Network connectivity issues
- NVIDIA API service unavailable

### Import Errors

Make sure dependencies are installed:

```bash
pip install -r requirements.txt
```

## Advanced Usage

### Custom System Prompts

```python
system_context = """You are a senior SRE with expertise in:
- Kubernetes troubleshooting
- Database performance
- Network debugging

Provide detailed root cause analysis."""

result = await agent.llm_reason(
    prompt="Analyze this incident...",
    system_context=system_context
)
```

### Conversation History

Agents track conversation history:

```python
# After using llm_reason()
for exchange in agent.conversation_history:
    print(f"Prompt: {exchange['prompt']}")
    print(f"Reasoning: {exchange['reasoning'][:100]}...")
    print(f"Response: {exchange['response']}")
```

## Performance Considerations

- **Streaming**: Recommended for better UX (shows reasoning in real-time)
- **Token Budgets**: Balance detail vs. latency
- **Caching**: Consider caching responses for identical queries
- **Fallback**: Always implement fallback logic for reliability

## Next Steps

1. **Add more specialized agents** (System Investigator, Code Detective)
2. **Implement theory management** (compare LLM theories from multiple agents)
3. **Add vector search** for incident knowledge base
4. **Enhance prompts** with real metrics and logs

## Resources

- [NVIDIA Nemotron Documentation](https://integrate.api.nvidia.com/)
- [Original Example](./ngc_example.py)
- [Agent Framework](./agents/)
- [Demo Runner](./demo.py)
