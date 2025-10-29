#!/usr/bin/env python3
"""
Lightweight Flask Web UI for Nonprofit Incident Reporting
Button-based interface with copy-to-clipboard summary
"""

from flask import Flask, render_template, request, jsonify, session
import secrets
from datetime import datetime
from examples.nonprofit_interface import (
    IncidentReport,
    IncidentTranslator,
    StatusSimplifier,
    IncidentManager
)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# In-memory storage for demo (use database in production)
incidents = {}


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
    # Store step 1 answer in session
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
        incident_id="",  # Will be auto-generated
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

    # Simulate investigation (in production, call your real agents)
    findings = simulate_investigation(technical_context)

    # Store results
    incidents[incident_id] = {
        'report': incident_report,
        'context': technical_context,
        'findings': findings
    }

    return render_template('investigating.html', incident_id=incident_id)


@app.route('/results/<incident_id>')
def results(incident_id):
    """Show results with copy-to-clipboard summary"""
    incident_data = incidents.get(incident_id)

    if not incident_data:
        return "Incident not found", 404

    findings = incident_data['findings']
    technical_context = incident_data['context']

    # Generate summaries
    simplifier = StatusSimplifier()

    # User-friendly summary
    user_summary = simplifier.create_user_summary(
        root_cause=findings['root_cause'],
        confidence=findings['confidence'],
        recommended_actions=findings['actions'],
        estimated_fix_time=findings['fix_time']
    )

    # Text message for tech team (concise, copy-paste ready)
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


def simulate_investigation(technical_context):
    """
    Simulate agent investigation (replace with real agent integration)
    """
    system = technical_context.system_affected

    # Mock findings based on system type
    mock_findings = {
        "database": {
            "root_cause": "Database connection pool exhaustion due to configuration change",
            "confidence": 0.85,
            "actions": [
                "Update database connection pool configuration",
                "Restart database service",
                "Monitor connection usage for 24 hours"
            ],
            "fix_time": "15-30 minutes"
        },
        "email": {
            "root_cause": "Email service configuration pointing to deprecated SMTP server",
            "confidence": 0.90,
            "actions": [
                "Update SMTP server configuration",
                "Restart email service",
                "Send test emails to verify"
            ],
            "fix_time": "10-20 minutes"
        },
        "website": {
            "root_cause": "Recent deployment introduced broken CSS link",
            "confidence": 0.75,
            "actions": [
                "Rollback to previous deployment",
                "Fix CSS link in code",
                "Redeploy with fix"
            ],
            "fix_time": "30-45 minutes"
        }
    }

    return mock_findings.get(system, {
        "root_cause": f"Issue detected in {system} component",
        "confidence": 0.70,
        "actions": [
            "Technical team will investigate the logs",
            "Identify specific component failure",
            "Implement appropriate fix"
        ],
        "fix_time": "1-2 hours"
    })


def generate_text_summary(incident_id, system, urgency, root_cause, fix_time):
    """
    Generate concise text message for tech on-call
    Ready to copy and send via SMS/text
    """
    urgency_emoji = "🚨" if urgency == "high" or urgency == "critical" else "⚠️"

    summary = f"""{urgency_emoji} INCIDENT {incident_id}

System: {system.upper()}
Urgency: {urgency.upper()}

Issue: {root_cause}

Est. fix time: {fix_time}

Check dashboard for full details."""

    return summary


if __name__ == '__main__':
    print("\n" + "="*70)
    print("  NONPROFIT INCIDENT REPORTING WEB UI")
    print("="*70)
    print("\n🌐 Starting server at http://localhost:5000")
    print("📱 Open in your browser to test the button-based interface\n")

    app.run(debug=True, port=5000)
