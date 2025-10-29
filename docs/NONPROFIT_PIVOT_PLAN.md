# Nonprofit Pivot Implementation Plan

## Vision
Transform the incident response war room from a technical demo into a tool that nonprofit staff can use to report issues, while your AI agents handle the technical investigation behind the scenes.

## User Story
"As a nonprofit program manager with limited technical knowledge, I need to report when our donor database isn't working, so the technical team can fix it without me needing to understand logs, APIs, or system architecture."

---

## Architecture Changes

### Before (Current State)
```
Technical User → demo.py → Agents → Terminal Output
```

### After (Nonprofit-Ready)
```
Nonprofit User → Simple Web Form → Translation Layer → Agents → Status Dashboard
                                                              ↓
                                           Technical Team ← Detailed Report
```

---

## New Components to Build

### 1. Nonprofit Interface Layer (`nonprofit_interface.py`)

**Purpose**: Translate between plain language and technical system

**Key Classes**:
```python
class IncidentTranslator:
    """Converts user-friendly descriptions to technical context"""

    def translate_to_technical(self, user_input):
        # "Database isn't working" → System metrics + error patterns
        pass

    def translate_from_technical(self, agent_output):
        # Agent reasoning → "Found connection issue with database server"
        pass

class StatusSimplifier:
    """Makes agent reasoning human-readable"""

    def get_status_message(self, current_phase):
        # "PHASE_1: Initial Assessment" → "🔍 Looking into the problem..."
        pass

    def create_summary(self, root_cause, confidence):
        # Technical findings → Plain language report
        pass
```

### 2. Web Interface (`web_ui/`)

**Simple Flask/FastAPI app with 2 pages**:

#### A. Report Incident Page
```html
Form fields:
- What were you trying to do? (text)
- What happened instead? (text)
- When did this start? (datetime picker)
- Is this urgent? (Yes/No)
- Screenshot (optional file upload)

[Submit Button] → Creates incident, starts investigation
```

#### B. Status Page
```html
Shows:
- Incident ID
- Current status (with emoji)
- Simple progress indicator
- Estimated time to diagnosis
- "View technical details" (link for technical staff)
```

### 3. Notification Bridge (`notifications.py`)

**Sends updates via**:
- Email to technical team
- Slack/Teams webhook (optional)
- SMS for urgent issues (optional)

---

## Modified Existing Components

### `demo.py` → `investigation_engine.py`
**Changes**:
- Add `incident_id` parameter
- Add `notify_on_complete` callback
- Return structured results (not just terminal output)
- Add REST API endpoint or queue listener

### `agents/commander.py`
**Changes**:
- Add `simple_summary()` method
- Return confidence level with findings
- Add estimated time remaining
- Track investigation phases for status updates

---

## Data Flow Example

### User Journey:
1. **User submits**: "Our email system stopped sending receipts to donors"

2. **Translation layer converts**:
```json
{
  "incident_id": "INC-001",
  "user_description": "Email system not sending receipts",
  "technical_context": {
    "system": "email_service",
    "symptoms": ["delivery_failure", "receipt_generation"],
    "urgency": "high",
    "affected_users": "donors"
  }
}
```

3. **Agent system investigates** (existing logic)
   - Commander orchestrates
   - Agents analyze logs, metrics, code changes
   - Observable reasoning captured

4. **Status updates** (new):
```
Every 30 seconds:
- 🔍 "Looking into email system..." (PHASE_1)
- 🔎 "Checking recent changes..." (PHASE_2)
- 💡 "Found possible cause..." (PHASE_3)
- ✅ "Root cause identified" (PHASE_4)
```

5. **Results delivered**:

**To User**:
```
📧 Email System Issue - RESOLVED

What we found:
A recent update changed how email receipts are sent. The system is trying
to send to an old server address that no longer exists.

What we're doing:
Our technical team has been notified and can fix this by updating the
server address in the configuration file.

Expected fix time: 15-30 minutes
```

**To Technical Team**:
```
INCIDENT: INC-001
ROOT CAUSE: Email service configuration pointing to deprecated SMTP server
CONFIDENCE: 85%

Evidence:
- Logs show connection timeout to smtp.old-server.org
- Recent deployment changed email_config.yaml
- Git history shows SMTP_HOST was updated but not applied
- Metrics show 100% delivery failure since 2024-10-29 14:23

Recommended Action:
1. Update email_config.yaml with new SMTP_HOST
2. Restart email-service container
3. Verify with test email

Full Investigation Report: [Link to detailed view]
```

---

## Plain Language Documentation

### For Nonprofit Staff: User Guide

#### "When to Report an Incident"
Report when:
- ✅ A system isn't working as expected
- ✅ Users are seeing errors
- ✅ Something that worked before is now broken
- ✅ Performance is much slower than usual

Don't report:
- ❌ Feature requests ("I wish we could...")
- ❌ Questions about how to use something
- ❌ Minor cosmetic issues (unless urgent)

#### "How to Write a Good Report"
**Be specific**:
- ❌ Bad: "Website is broken"
- ✅ Good: "When I try to submit a donation form, I get an error message"

**Include timing**:
- ❌ Bad: "Started recently"
- ✅ Good: "Started this morning around 9:30 AM"

**Describe the impact**:
- ❌ Bad: "It's not working"
- ✅ Good: "Donors can't complete their donations - 5 people have called about it"

#### "Understanding the Status Updates"
- 🔍 **Investigating**: Our system is looking into the problem
- 🔎 **Analyzing**: Checking logs, code changes, and system health
- 💡 **Hypothesis**: Think we found the cause, verifying now
- ✅ **Identified**: Root cause confirmed, technical team notified
- 🛠️ **In Progress**: Technical team is working on the fix

---

### For Technical Team: Integration Guide

#### "How the Nonprofit Interface Works"

**1. Incident Creation**
```bash
# User submits form → Creates incident file
incidents/INC-001.json

# Triggers investigation
python investigation_engine.py --incident INC-001
```

**2. During Investigation**
```python
# Your agents run as normal
# Progress updates sent to status API every 30s
# Full reasoning logged for technical review
```

**3. Results**
```bash
# User sees: simplified summary
# You see: full technical report + all agent reasoning
# Logs: complete investigation transcript
```

#### "Accessing Technical Details"
```bash
# View full investigation
python demo.py --incident INC-001 --replay

# Export detailed report
python export_report.py INC-001 --format technical

# See agent reasoning
cat logs/INC-001-reasoning.log
```

---

## Implementation Phases

### Phase 1: Core Translation (Today - 2 hours)
**Goal**: Prove the concept works

**Build**:
1. `nonprofit_interface.py` - Translation functions
2. Simple command-line interface for testing
3. Mock incident data

**Validate**:
- Can translate user input to technical context
- Can simplify agent output to plain language
- Manual test with sample scenarios

### Phase 2: Web Interface (Tomorrow - 3 hours)
**Goal**: Make it usable by real users

**Build**:
1. Basic Flask app with 2 pages
2. Form submission → triggers investigation
3. Status page with real-time updates

**Validate**:
- End-to-end flow works
- Status updates appear within 30s
- Results shown in both user/technical formats

### Phase 3: Integration & Polish (Day 3 - 2 hours)
**Goal**: Production-ready for demo

**Build**:
1. Notification system (email/Slack)
2. Incident history/dashboard
3. Error handling and edge cases

**Validate**:
- Full user journey smooth
- Technical team gets detailed reports
- Ready for live demo

---

## Success Metrics

### For Nonprofit Users
- ✅ Can submit incident in < 2 minutes
- ✅ Understand status updates without technical knowledge
- ✅ Know when issue is resolved
- ✅ Don't need to understand logs, APIs, or system architecture

### For Technical Team
- ✅ Get high-quality incident reports with context
- ✅ Full access to agent reasoning and technical details
- ✅ Notified immediately when investigation completes
- ✅ Can replay investigations for learning

### For Demo/Hackathon
- ✅ Shows real-world applicability (not just technical demo)
- ✅ Demonstrates AI helping non-technical users
- ✅ Clear value proposition for nonprofits
- ✅ Impressive to both technical and non-technical judges

---

## Quick Start Commands (After Implementation)

### For Nonprofit Users
```bash
# Start the user interface
python web_ui/app.py

# Visit: http://localhost:5000
# Click "Report an Incident" and fill out the form
```

### For Technical Team
```bash
# View all incidents
python manage_incidents.py --list

# See full technical details
python manage_incidents.py --details INC-001

# Replay investigation
python demo.py --incident INC-001 --replay
```

---

## Example Scenarios for Testing

### Scenario 1: Database Connection Issue
**User Input**: "Our volunteer tracking system is showing 'Error 500' when I try to add new volunteers"

**Translation**:
```json
{
  "system": "volunteer_management",
  "symptom": "http_500_error",
  "action_attempted": "create_new_record",
  "urgency": "medium"
}
```

**Expected Investigation**: Agents check database connections, recent deployments, error logs

**User-Friendly Result**: "The volunteer system can't connect to the database. We found a configuration issue that happened during last night's update. The technical team can fix this in about 15 minutes."

---

### Scenario 2: Email Delivery Failure
**User Input**: "Donation receipts haven't been going out to donors since this morning. We've gotten 3 calls about it."

**Translation**:
```json
{
  "system": "email_service",
  "symptom": "delivery_failure",
  "timing": "started_morning",
  "impact": "donor_experience",
  "urgency": "high"
}
```

**Expected Investigation**: Agents check SMTP logs, email queue, recent config changes

**User-Friendly Result**: "Email receipts aren't sending because the email server address needs to be updated. This is a quick fix - the technical team can resolve it in under 30 minutes."

---

## Next Steps

1. **Review this plan** with your team
2. **Start with Phase 1** - Build translation layer
3. **Test with mock data** before building web UI
4. **Gather feedback** from a nonprofit user (if available)
5. **Iterate quickly** - hackathon timeline is tight!

---

## Questions to Answer

Before implementing, consider:

1. **Deployment**: Where will the nonprofit interface run?
   - Cloud service (Vercel, Render)?
   - On-premises server?
   - Desktop app?

2. **Authentication**: How do users log in?
   - Simple password?
   - SSO with their existing system?
   - No auth for MVP?

3. **Notifications**: What channels are realistic?
   - Email only (easiest)?
   - Slack/Teams integration?
   - SMS for emergencies?

4. **Storage**: Where do incidents live?
   - Simple JSON files?
   - SQLite database?
   - Cloud database?

---

## Resources Needed

### Technical
- Python 3.8+
- Flask or FastAPI (web framework)
- Your existing agent system
- (Optional) Email service (SendGrid, Mailgun)
- (Optional) Messaging webhooks (Slack, Teams)

### Time Estimates
- **Phase 1**: 2-3 hours
- **Phase 2**: 3-4 hours
- **Phase 3**: 2-3 hours
- **Total**: 7-10 hours (1-2 days of focused work)

### Skills Needed
- Python (you have this)
- Basic web dev (HTML forms)
- API integration (for notifications)
- User experience thinking (for plain language)

---

**Ready to start? Begin with Phase 1 - the translation layer is the key component that makes everything else possible.**
