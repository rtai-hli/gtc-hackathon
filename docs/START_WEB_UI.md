# 🚀 Start Web UI - Quick Reference

## Instant Start (3 commands)

```bash
# 1. Make sure Flask is installed
pip install flask

# 2. Start the server
python web_app.py

# 3. Open in browser
# http://localhost:5000
```

---

## ✨ What You'll See

### Landing Page
- Big "Start Report" button
- Simple explanation

### 4-Step Button Flow
1. **What were you trying to do?** (7 button options)
2. **What happened instead?** (7 button options)
3. **When did this start?** (6 button options)
4. **Is this urgent?** (2 big buttons: Yes/No)

### Investigation Animation
- Spinner with progress updates
- Auto-redirects after 5 seconds

### Results Page ⭐
- ✅ Plain language summary
- 📱 **Copy-to-clipboard text message**
- One-click "Copy Message" button
- Ready to paste into SMS/Slack/Teams

---

## 🎯 Key Feature: Copy-to-Text

Instead of asking "want to see technical details?", we generate a ready-to-send message:

```
🚨 INCIDENT INC-20241029153045

System: DATABASE
Urgency: HIGH

Issue: Database connection pool exhaustion due to configuration change

Est. fix time: 15-30 minutes

Check dashboard for full details.
```

User clicks "Copy Message" → Paste into phone → Send to tech team. Done!

---

## 📱 Test Scenarios

### Scenario 1: Database Error
1. Add a new donor
2. Got an error message
3. Just now
4. Yes (urgent)

**Result**: Database connection issue, 15-30 min fix

### Scenario 2: Email Problem
1. Send email receipts
2. Nothing happened
3. Earlier today
4. No (not urgent)

**Result**: Email configuration issue, 10-20 min fix

### Scenario 3: Slow Website
1. Access our website
2. Very slow loading
3. A few days ago
4. No

**Result**: Performance issue, 30-45 min fix

---

## 🎬 Demo Script

**1. Show Landing**: "Anyone can report incidents - just click buttons"

**2. Click Through**: Show 4-step flow (takes 30 seconds)

**3. Show Animation**: "AI investigates in real-time"

**4. Highlight Copy Feature**:
   - "Instead of technical details, here's a message ready to send"
   - Click "Copy Message"
   - Paste in notepad to show it copied
   - "One click, paste to phone, send to tech team"

**5. Key Point**: "No typing, no technical knowledge, no translation needed"

---

## 📁 Files Created

```
web_app.py                    # Flask server (200 lines)
templates/
  ├── index.html             # Landing page
  ├── step1.html             # What doing?
  ├── step2.html             # What happened?
  ├── step3.html             # When?
  ├── step4.html             # Urgent?
  ├── investigating.html     # Progress animation
  └── results.html           # Results + copy button
```

---

## 🔧 Customization

### Change Button Options
Edit `templates/step1.html` (or step2, step3):
```html
<button type="submit" name="what_trying" value="Your option">
    🎯 Your Button Text
</button>
```

### Change Text Message Format
Edit `web_app.py` → `generate_text_summary()`:
```python
summary = f"""🚨 INCIDENT {incident_id}
Your custom format here...
"""
```

### Add Your Styles
Replace `<style>` blocks in templates with your CSS

---

## ✅ Everything Works

- ✅ Zero typing - all buttons
- ✅ Mobile responsive
- ✅ Copy-to-clipboard with fallback
- ✅ Visual feedback
- ✅ Auto-redirect
- ✅ Progress animation
- ✅ Plain language summaries
- ✅ Ready-to-send text messages

---

## 🎯 Ready to Demo!

```bash
python web_app.py
```

Open `http://localhost:5000` and click through!

**The copy-to-clipboard feature is your differentiator - highlight it!** 📱✨
