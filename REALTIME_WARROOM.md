# 🐠 Real-Time War Room - Agent Conversation Display

## Overview

This enhancement adds **real-time agent conversation display** to the frontend during the investigation stage. Users can now watch the Commander and subagents collaborate in real-time to diagnose issues.

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Frontend (investigating_realtime.html)         │
│  - WebSocket client                             │
│  - Real-time message display                    │
│  - Animated conversation log                    │
└──────────────┬──────────────────────────────────┘
               │ WebSocket (Socket.IO)
┌──────────────▼──────────────────────────────────┐
│  Backend (web_app_realtime.py)                  │
│  - Flask + SocketIO server                      │
│  - Event broadcaster                            │
│  - Async investigation runner                   │
└──────────────┬──────────────────────────────────┘
               │ Event Listener
┌──────────────▼──────────────────────────────────┐
│  War Room Agents (commander.py, base.py)        │
│  - Commander agent                              │
│  - Specialist subagents                         │
│  - Event emission system                        │
└─────────────────────────────────────────────────┘
```

## Features

### 1. Real-Time Agent Events
- **Commander thinking**: See strategic decisions as they happen
- **Task delegation**: Watch Commander assign tasks to specialists
- **Agent observations**: View findings from System Investigator, Code Detective
- **Root cause determination**: See the final analysis with confidence score

### 2. Visual Design
- **Color-coded agents**: Each agent has unique styling
  - 🧠 Commander: Green (#76ff03)
  - 🔍 System Investigator: Purple (#b388ff)
  - 🔎 Code Detective: Yellow (#ffeb3b)
- **Event type indicators**:
  - 💭 Thinking
  - ⚡ Action
  - 👁️ Observation
  - ✅ Decision
  - 🔬 Theory
  - ⚔️ Challenge

### 3. Interactive Elements
- Live connection status indicator
- Auto-scrolling conversation log
- Smooth animations for new messages
- Automatic redirect when investigation completes

## Files Structure

### New Files
```
web_app_realtime.py                  # Enhanced Flask app with WebSocket
templates/investigating_realtime.html # Real-time conversation UI
REALTIME_WARROOM.md                  # This file
```

### Modified Files
None - the original `web_app.py` remains unchanged for backward compatibility.

## Installation

### 1. Install Dependencies
```bash
pip install flask-socketio
```

### 2. Verify Agent System
Ensure the following files exist:
- `agents/base.py` - Base agent with event system
- `agents/commander.py` - Incident Commander
- `agents/llm_wrapper.py` - LLM client (optional)

## Usage

### Start the Real-Time Server
```bash
python web_app_realtime.py
```

### Access the Web UI
Open your browser to:
```
http://localhost:5000
```

### Flow
1. **Report incident** - Follow the 4-step wizard
2. **Investigation starts** - War room activates
3. **Watch real-time** - See agents collaborate
4. **Results delivered** - Automatic redirect to solution

## Technical Details

### WebSocket Events

#### `agent_event` (server → client)
Emitted whenever an agent thinks, acts, or observes.

```javascript
{
  "agent": "Commander",
  "type": "thinking",
  "content": "Beginning incident assessment...",
  "icon": "💭",
  "timestamp": "2024-10-29T20:10:15.123Z",
  "metadata": {
    "severity": "high",
    "phase": "assessment"
  }
}
```

#### `investigation_complete` (server → client)
Emitted when investigation finishes.

```javascript
{
  "incident_id": "INC-2024-1029-001",
  "root_cause": "Database connection pool exhaustion..."
}
```

#### `connected` (server → client)
Connection confirmation.

```javascript
{
  "status": "connected"
}
```

### Event Broadcasting Flow

```python
# 1. Agent emits event
commander.think("Beginning incident assessment...")

# 2. BaseAgent emits AgentEvent
event = AgentEvent(
    agent_name="Commander",
    event_type=EventType.THINKING,
    content="Beginning incident assessment...",
    metadata={}
)

# 3. Event listener broadcasts to frontend
def agent_event_broadcaster(event: AgentEvent):
    socketio.emit('agent_event', event.to_dict(), namespace='/investigation')

# 4. Frontend receives and displays
socket.on('agent_event', (event) => {
    addAgentMessage(event);
});
```

### Async Investigation Runner

The investigation runs in a background thread to avoid blocking the web server:

```python
def run_real_investigation(incident_id, technical_context):
    # Create commander with event listener
    commander = IncidentCommander(llm_client=llm_client)
    commander.add_event_listener(agent_event_broadcaster)

    # Run async investigation
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(commander.run({"incident": incident}))

    # Broadcast completion
    socketio.emit('investigation_complete', {...})
```

## Customization

### Add New Agent Types

1. **Create agent class**:
```python
from agents.base import BaseAgent

class DatabaseExpert(BaseAgent):
    def __init__(self, llm_client=None):
        super().__init__(name="DB Expert", role="Database Specialist", llm_client)

    async def analyze(self, context):
        self.think("Analyzing database metrics...")
        self.observe("Found connection pool exhaustion")
        return {"finding": "pool_exhausted"}
```

2. **Register event listener**:
```python
db_expert = DatabaseExpert()
db_expert.add_event_listener(agent_event_broadcaster)
```

3. **Add color mapping** in `investigating_realtime.html`:
```javascript
const agentColors = {
    'db expert': 'text-cyan-400',  // Add new color
    // ... existing colors
};
```

### Customize Event Icons

Edit the `icon_map` in `web_app_realtime.py`:

```python
icon_map = {
    "thinking": "💭",
    "action": "⚡",
    "observation": "👁️",
    "decision": "✅",
    "theory": "🔬",
    "challenge": "⚔️",
    "alert": "🚨",      # Add custom event
    "success": "🎉"     # Add custom event
}
```

## Debugging

### Enable Debug Logging
```python
# In web_app_realtime.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check WebSocket Connection
Open browser console:
```javascript
// Should see:
✅ Connected to war room
📡 Agent event: {...}
```

### Test Event Broadcasting
```python
# In Python console
from agents.base import BaseAgent, EventType

agent = BaseAgent("Test", "Tester")
agent.add_event_listener(print)  # Print events
agent.think("Hello World")
```

## Performance Considerations

### Scalability
- Current implementation uses in-memory storage
- For production, use Redis for pub/sub
- Consider rate limiting for event broadcasting

### Resource Usage
- Each WebSocket connection is lightweight (~10KB)
- Events are JSON-serialized (typically <1KB each)
- Background thread per investigation (minimal overhead)

### Production Recommendations
```python
# Use Redis for pub/sub
socketio = SocketIO(app, message_queue='redis://localhost:6379')

# Add authentication
@socketio.on('connect', namespace='/investigation')
def handle_connect(auth):
    if not verify_token(auth['token']):
        return False  # Reject connection
```

## Troubleshooting

### Issue: WebSocket not connecting
**Solution**: Check CORS settings
```python
socketio = SocketIO(app, cors_allowed_origins="*")  # For dev
# For production:
socketio = SocketIO(app, cors_allowed_origins="https://yourdomain.com")
```

### Issue: Events not appearing
**Solution**: Verify event listener is registered
```python
commander.add_event_listener(agent_event_broadcaster)  # Must be before run()
```

### Issue: Investigation hangs
**Solution**: Check async loop
```python
# Add timeout
result = loop.run_until_complete(
    asyncio.wait_for(commander.run(context), timeout=60)
)
```

## Demo Comparison

### Original Demo (CLI)
```
20:10:15 💭 [Commander] Beginning incident assessment...
20:10:15 ✅ [Commander] Investigation priority: metrics > recent_changes > logs
20:10:15 ⚡ [Commander] Delegating metrics investigation to System Investigator
```

### New Web UI
Visual representation with:
- Color-coded agent cards
- Smooth animations
- Timestamp display
- Metadata tooltips
- Auto-scrolling conversation log

## Future Enhancements

- [ ] Agent avatars/profiles
- [ ] Conversation export (PDF/JSON)
- [ ] Replay mode for past investigations
- [ ] Multi-incident support
- [ ] Voice synthesis for agent messages
- [ ] Collaborative mode (multiple users watching)
- [ ] Agent performance metrics dashboard

## License

Same as main project.

## Support

For questions or issues, please refer to the main project documentation or open an issue on GitHub.
