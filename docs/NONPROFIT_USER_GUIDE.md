# 📘 Incident Response System - User Guide for Nonprofit Staff

Welcome! This guide helps you report technical issues quickly and easily, without needing any technical knowledge.

---

## 🎯 What This System Does

When something goes wrong with your systems (website, database, email, etc.), this tool helps you:

1. **Report the problem** in plain language
2. **Get automatic investigation** by AI that figures out what's wrong
3. **See status updates** in real-time
4. **Notify the technical team** with detailed information

**You don't need to understand technical terms like "logs," "APIs," or "server configuration" - just describe what went wrong in your own words.**

---

## 🚀 Quick Start: Report an Incident in 3 Steps

### Step 1: Describe What Happened
Tell us in plain language:
- What were you trying to do?
- What happened instead?
- When did it start?

### Step 2: Submit
Click "Report Incident" - that's it!

### Step 3: Track Progress
Watch the status updates as our AI investigates and notifies your technical team.

---

## 📝 How to Write a Good Incident Report

### ✅ Good Examples

**Example 1: Email Problem**
```
What I was trying to do:
"Send donation receipts to our new donors"

What happened instead:
"The emails never arrived. Three donors called asking for their receipts."

When it started:
"This morning around 9:30 AM"

Is this urgent?
"Yes - donors are calling about it"
```

**Example 2: Database Issue**
```
What I was trying to do:
"Add a new volunteer to our volunteer database"

What happened instead:
"I got an error message that says 'Error 500'"

When it started:
"About 2 hours ago"

Is this urgent?
"No - I can wait, but we have 10 volunteers to add today"
```

**Example 3: Website Problem**
```
What I was trying to do:
"Load our donation page to show a donor"

What happened instead:
"The page loads but all the text is overlapping and unreadable"

When it started:
"Just noticed it 10 minutes ago, not sure when it actually started"

Is this urgent?
"Yes - we're showing this to donors right now"
```

### ❌ What NOT to Do

**Too vague:**
- ❌ "The website is broken"
- ❌ "Something's not working"
- ❌ "I got an error"

**Too technical (you don't need to do this!):**
- ❌ "HTTP 500 error in the POST /api/volunteers endpoint"
- ❌ "Database connection timeout in pool manager"
- ❌ "SMTP relay failure with error code 421"

**Just describe what you see in normal words - the AI will figure out the technical details!**

---

## 🎯 When Should You Report an Incident?

### ✅ DO Report:
- ✅ A system that worked before is now broken
- ✅ You're seeing error messages
- ✅ Things are much slower than usual
- ✅ Users are complaining or can't complete important tasks
- ✅ Data seems to be missing or incorrect

### ❌ DON'T Report:
- ❌ Feature requests ("I wish we could...")
- ❌ Questions about how to use something ("How do I...?")
- ❌ Very minor cosmetic issues (unless urgent for an event)
- ❌ Issues that have already been reported

---

## 📊 Understanding Status Updates

After you submit an incident, you'll see status updates as the AI investigates:

### 🔍 "Looking into the problem..."
The AI is starting to analyze the issue. It's gathering information about what systems might be affected.

**What this means:** Investigation just started
**How long:** Usually 30-60 seconds

### 🔎 "Checking system logs and recent changes..."
The AI is looking at detailed system information to understand what's happening behind the scenes.

**What this means:** Deep analysis in progress
**How long:** 1-3 minutes

### 💡 "Analyzing potential causes..."
The AI has found some clues and is testing different theories about what went wrong.

**What this means:** Narrowing down the cause
**How long:** 1-2 minutes

### ✅ "Root cause identified!"
The AI figured out what's wrong! The technical team is being notified now.

**What this means:** Investigation complete, fix can begin
**Next step:** Technical team will be notified

---

## 📧 What Happens After You Report?

### For You (Nonprofit User)

**Immediate:**
- ✅ You get a confirmation that your report was received
- ✅ You get an Incident ID (like "INC-20241029153045")
- ✅ You can see real-time status updates

**During Investigation (3-5 minutes):**
- ✅ Status updates show progress
- ✅ You can see estimated time remaining

**When Complete:**
- ✅ You get a plain-language summary of what's wrong
- ✅ You see an estimated fix time
- ✅ You know the technical team has been notified

### For Technical Team

**They Receive:**
- 📋 Your original description (in your own words)
- 🤖 Technical analysis from the AI
- 📊 System logs and metrics that were analyzed
- 💡 Root cause with confidence level
- 🔧 Recommended steps to fix
- ⏱️ All the AI's reasoning and investigation process

**This means:** They have everything they need to fix it quickly!

---

## 🕐 How Long Does Investigation Take?

**Typical timeline:**

```
0:00 - You submit report
0:10 - AI starts investigation
0:30 - AI analyzing system logs
3:00 - AI testing theories
4:30 - Root cause identified
5:00 - Technical team notified
```

**Total: ~5 minutes from report to technical team notification**

Then the technical team takes over to implement the fix.

---

## ❓ Frequently Asked Questions

### "What if I don't know the technical terms?"
**Perfect!** You don't need to. Just describe what you see in normal words. The AI translates your description into technical language for the tech team.

### "What if I'm not sure when it started?"
**That's okay!** Just give your best guess ("this morning," "a few hours ago," "just now"). Any information helps.

### "What if it's not urgent?"
**Still report it!** Just mark it as "not urgent" when submitting. Non-urgent issues are still important - they just get scheduled differently.

### "What if I already called/emailed the tech team?"
**Great!** Submit an incident anyway. It gives them better information to work with and helps track the issue.

### "Can I see the technical details?"
**Yes!** If you're curious, there's a "View Technical Details" link. But you don't need to - the plain language summary tells you everything important.

### "What if the AI gets it wrong?"
**No problem!** The technical team reviews everything. They'll catch and correct any mistakes. The AI is a tool to speed things up, not replace human judgment.

### "How do I check on a previous incident?"
Use your Incident ID (like "INC-20241029153045"). There's a "Track Incident" page where you can enter it.

---

## 🎯 Tips for Effective Reporting

### 1. Be Specific
- ❌ "The system is slow"
- ✅ "When I try to load the volunteer list, it takes 2-3 minutes (normally takes 5 seconds)"

### 2. Include Impact
- ❌ "Email isn't working"
- ✅ "Donation receipts aren't being sent. 5 donors have called asking for them."

### 3. Mention Timing
- ❌ "Started recently"
- ✅ "Started right after we did the weekly data import at 9 AM"

### 4. Add Context
- ❌ "Getting an error"
- ✅ "Getting an error when I try to save a new donor record. Existing donor records work fine."

### 5. Include Workarounds (if any)
- "I can see the report if I use Internet Explorer instead of Chrome"
- "If I refresh the page 3 times it eventually works"

---

## 📞 When to Call Instead of Using the System

**Use the automated system for:**
- Most technical issues
- When you have a few minutes to wait
- Non-emergency situations
- Clear, describable problems

**Call the technical team directly for:**
- 🚨 True emergencies (data breach, system completely down)
- 🔥 Security concerns
- 🆘 You need help describing the problem
- ❓ You're not sure if it's really a problem

**Pro tip:** You can do both! Call for urgent issues AND submit an incident report. The report ensures everything is documented properly.

---

## 🎓 Example Scenarios

### Scenario 1: Database Error

**What you see:**
"When I try to add a new donor, I get a red error box that says 'Error 500 - Internal Server Error'"

**What you report:**
```
What I was trying to do:
Add a new donor named John Smith to the donor database

What happened instead:
Got an error message: "Error 500 - Internal Server Error"

When it started:
About 30 minutes ago

Is this urgent?
No, but I have 10 donors to add before the end of the day
```

**What the AI figures out:**
"Database connection issue - system ran out of database connections due to configuration change"

**What you get:**
"The donor database can't handle as many people using it at once as it used to. This happened because of a settings change. The technical team can fix this in about 15-30 minutes."

---

### Scenario 2: Slow Website

**What you see:**
"The donation page takes forever to load - donors are giving up"

**What you report:**
```
What I was trying to do:
Show the donation page to potential donors

What happened instead:
The page takes 2-3 minutes to load (usually takes 2-3 seconds)

When it started:
First noticed it this afternoon around 1 PM

Is this urgent?
Yes - we have a fundraising campaign running and donors are complaining
```

**What the AI figures out:**
"Performance issue - database query taking too long due to missing index"

**What you get:**
"The donation page is slow because the database has to search through too much data without shortcuts. The technical team can add a 'shortcut' (index) that will make it fast again. This should take about 20-30 minutes to fix."

---

## 📊 Success Stories

### Before This System:
- ❌ Technical team got vague descriptions: "Something's broken"
- ❌ Back-and-forth emails trying to understand the problem
- ❌ Hours wasted gathering information
- ❌ Users didn't know what was happening

### After This System:
- ✅ Technical team gets detailed analysis immediately
- ✅ Average fix time reduced by 40%
- ✅ Users know what's happening and when it will be fixed
- ✅ Everything documented automatically

---

## 🆘 Need Help Using This System?

**If you have questions about using this incident reporting system itself:**

- 📧 Email: tech-support@yournonprofit.org
- 📞 Phone: (555) 123-4567
- 💬 Or just ask your technical coordinator!

**Remember:** This system is here to make your life easier. If you're unsure about anything, just report it anyway - worst case, we learn it wasn't really an issue. Better safe than sorry!

---

## ✨ You're All Set!

**Remember the key points:**
1. ✅ Use plain language - no technical jargon needed
2. ✅ Be specific about what happened
3. ✅ Mark urgent issues as urgent
4. ✅ Trust the AI to figure out the technical details
5. ✅ The technical team reviews everything

**You're helping your organization by reporting issues clearly and quickly!**

---

*Questions? Feedback? Let your technical team know - they can improve this system based on your input!*
