#!/usr/bin/env python3
"""
Enhanced Flask Web UI with Real-Time Agent Conversations
Displays commander and subagent interactions during investigation
"""

from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
import secrets
import asyncio
from datetime import datetime
from threading import Thread
from examples.nonprofit_interface import (
    IncidentReport,
    IncidentTranslator,
    StatusSimplifier,
    IncidentManager
)
from agents.commander import IncidentCommander
from agents.base import AgentEvent

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory storage for demo
incidents = {}


# Event listener to broadcast agent events to frontend
def agent_event_broadcaster(event: AgentEvent):
    """Broadcast agent events to connected WebSocket clients"""
    event_data = event.to_dict()

    # Map event types to visual styles
    icon_map = {
        "thinking": "💭",
        "action": "⚡",
        "observation": "👁️",
        "decision": "✅",
        "theory": "🔬",
        "challenge": "⚔️"
    }

    event_data['icon'] = icon_map.get(event.event_type.value, "💬")

    # Emit to all connected clients
    socketio.emit('agent_event', event_data, namespace='/investigation')


@app.route('/')
def index():
    """Landing page - start incident report"""
    return render_template('index.html')


@app.route('/step1')
def step1():
    """Step 1: What were you trying to do?"""
    return render_template('step1.html')


@app.route('/step2', methods=['POST'])
def step2():
    """Step 2: What happened instead?"""
    session['what_trying'] = request.form.get('what_trying')
    return render_template('step2.html')


@app.route('/step3', methods=['POST'])
def step3():
    """Step 3: When did this start?"""
    session['what_happened'] = request.form.get('what_happened')
    return render_template('step3.html')


@app.route('/step4', methods=['POST'])
def step4():
    """Step 4: Is this urgent?"""
    session['when_started'] = request.form.get('when_started')
    return render_template('step4.html')


@app.route('/investigating', methods=['POST'])
def investigating():
    """Show investigation in progress"""
    session['is_urgent'] = request.form.get('is_urgent') == 'yes'

    # Create incident report
    incident_report = IncidentReport(
        incident_id="",
        user_description="",
        what_trying_to_do=session.get('what_trying', ''),
        what_happened_instead=session.get('what_happened', ''),
        when_started=session.get('when_started', datetime.now().isoformat()),
        is_urgent=session.get('is_urgent', False)
    )

    # Save incident
    manager = IncidentManager()
    incident_id = manager.create_incident(incident_report)
    session['incident_id'] = incident_id

    # Translate to technical context
    translator = IncidentTranslator()
    technical_context = translator.translate_to_technical(incident_report)

    # Store initial data
    incidents[incident_id] = {
        'report': incident_report,
        'context': technical_context,
        'findings': None,
        'status': 'investigating'
    }

    # Start real investigation in background
    thread = Thread(target=run_real_investigation, args=(incident_id, technical_context))
    thread.daemon = True
    thread.start()

    return render_template('investigating_realtime.html', incident_id=incident_id)


def run_real_investigation(incident_id: str, technical_context):
    """Run the actual war room investigation with real agents"""

    # Create incident dict for commander
    # Format symptoms as a readable string
    symptoms_text = ", ".join(technical_context.symptoms) if technical_context.symptoms else "Unknown issue"

    incident = {
        'id': incident_id,
        'symptom': f"{technical_context.system_affected} issue: {symptoms_text}",
        'severity': technical_context.urgency_level,
        'service': technical_context.system_affected,
        'impact': technical_context.user_impact
    }

    # Create commander with LLM support
    try:
        from agents.llm_wrapper import LLMWrapper
        llm_client = LLMWrapper()
        commander = IncidentCommander(llm_client=llm_client)
    except Exception as e:
        print(f"⚠️  LLM unavailable: {e}. Using rule-based reasoning.")
        commander = IncidentCommander(llm_client=None)

    # Add event listener to broadcast to frontend
    commander.add_event_listener(agent_event_broadcaster)

    # Run investigation
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(commander.run({"incident": incident}))

        # Extract findings
        root_cause = result.get('root_cause', 'Investigation in progress')

        # Update incident with findings
        incidents[incident_id]['findings'] = {
            'root_cause': root_cause,
            'confidence': 0.85,
            'actions': [
                "Review recent configuration changes",
                "Check database connection pool settings",
                "Monitor system metrics for next 24 hours"
            ],
            'fix_time': "30-60 minutes"
        }
        incidents[incident_id]['status'] = 'resolved'

        # Emit completion event
        socketio.emit('investigation_complete', {
            'incident_id': incident_id,
            'root_cause': root_cause
        }, namespace='/investigation')

    except Exception as e:
        print(f"❌ Investigation error: {e}")
        incidents[incident_id]['status'] = 'error'
        incidents[incident_id]['error'] = str(e)
    finally:
        loop.close()


@app.route('/results/<incident_id>')
def results(incident_id):
    """Show results with copy-to-clipboard summary"""
    incident_data = incidents.get(incident_id)

    if not incident_data:
        return "Incident not found", 404

    findings = incident_data.get('findings')

    if not findings:
        return "Investigation still in progress", 202

    technical_context = incident_data['context']

    # Generate summaries
    simplifier = StatusSimplifier()

    user_summary = simplifier.create_user_summary(
        root_cause=findings['root_cause'],
        confidence=findings['confidence'],
        recommended_actions=findings['actions'],
        estimated_fix_time=findings['fix_time']
    )

    text_summary = generate_text_summary(
        incident_id=incident_id,
        system=technical_context.system_affected,
        urgency=technical_context.urgency_level,
        root_cause=findings['root_cause'],
        fix_time=findings['fix_time']
    )

    return render_template(
        'results.html',
        incident_id=incident_id,
        user_summary=user_summary,
        text_summary=text_summary,
        system=technical_context.system_affected,
        urgency=technical_context.urgency_level
    )


def generate_text_summary(incident_id, system, urgency, root_cause, fix_time):
    """Generate concise text message for tech on-call"""
    urgency_emoji = "🚨" if urgency == "high" or urgency == "critical" else "⚠️"

    summary = f"""{urgency_emoji} INCIDENT {incident_id}

System: {system.upper()}
Urgency: {urgency.upper()}

Issue: {root_cause}

Est. fix time: {fix_time}

Check dashboard for full details."""

    return summary


@socketio.on('connect', namespace='/investigation')
def handle_connect():
    """Handle WebSocket connection"""
    print(f"🔌 Client connected: {request.sid}")
    emit('connected', {'status': 'connected'})


@socketio.on('disconnect', namespace='/investigation')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    print(f"🔌 Client disconnected: {request.sid}")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("  🐠 NEMO AI TECH SUPPORT - REAL-TIME WAR ROOM")
    print("="*70)
    print("\n🌐 Starting server at http://localhost:5000")
    print("📡 WebSocket enabled for real-time agent conversations\n")

    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)
