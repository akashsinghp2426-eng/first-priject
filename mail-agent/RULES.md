# 📋 Mail Agent Rules & Behavior Documentation

## Overview

This document defines the complete rule base for the Mail Agent's decision-making process, including email classification, priority assignment, reminder creation, and automated actions.

---

## 1. Priority Classification System

### 1.1 Priority Levels

The agent classifies emails into four priority levels:

| Level | Score Range | Reminder? | Notification | Description |
|-------|-------------|-----------|--------------|-------------|
| 🔴 **CRITICAL** | ≥ 0.8 | ✅ Yes | Immediate | Urgent, time-sensitive emergencies |
| 🟠 **IMPORTANT** | ≥ 0.6 | ✅ Yes | Standard | Action required, deadlines, meetings |
| 🟡 **NORMAL** | ≥ 0.3 | ❌ No | Digest only | Regular business correspondence |
| 🟢 **LOW** | < 0.3 | ❌ No | None | Newsletters, promotions, bulk mail |

### 1.2 Classification Keywords

#### CRITICAL Indicators (Score: 0.8-1.0)
```
urgent, emergency, asap, immediately, critical,
deadline today, action required now, server down,
outage, incident, security breach, payment overdue,
legal notice, court, lawsuit, terminated, suspended
```

#### IMPORTANT Indicators (Score: 0.6-0.79)
```
meeting, deadline, review, approval, important,
action required, please respond, reply needed,
tomorrow, this week, schedule, appointment,
interview, presentation, milestone, deliverable,
budget, contract, agreement, sign, approve
```

#### NORMAL Indicators (Score: 0.3-0.59)
```
update, status, report, information, question,
discussion, feedback, comment, suggestion,
document, file, attachment, project, task
```

#### LOW Indicators (Score: 0.0-0.29)
```
newsletter, promotion, unsubscribe, marketing,
sale, offer, discount, bulk, automated,
notification, digest, summary, social media,
feed, update notification, advertisement
```

---

## 2. Sender-Based Rules

### 2.1 VIP Sender Escalation

Emails from VIP senders are automatically escalated one priority level:

```yaml
vip_senders:
  - boss@company.com
  - ceo@company.com
  - cto@company.com
  - hr@company.com
  - important-client@client.com
```

**Escalation Examples:**
- LOW → NORMAL
- NORMAL → IMPORTANT
- IMPORTANT → CRITICAL (capped)
- CRITICAL → CRITICAL (already max)

### 2.2 Domain-Based Rules

#### High-Priority Domains (Auto +0.2 score)
```yaml
high_priority_domains:
  - company.com          # Internal emails
  - clients.company.com  # Client communications
  - partners.company.com # Partner communications
```

#### Low-Priority Domains (Auto -0.2 score)
```yaml
low_priority_domains:
  - newsletters.*        # Newsletter services
  - notifications.*      # Automated notifications
  - marketing.*          # Marketing emails
  - no-reply.*           # No-reply addresses
```

### 2.3 Unknown Sender Handling

First-time senders:
- Start with neutral score (0.5)
- No automatic escalation
- User can manually adjust (future feature)

---

## 3. Time-Based Rules

### 3.1 Business Hours Configuration

```yaml
business_hours:
  start: "09:00"
  end: "18:00"
  timezone: "UTC"
  work_days: ["Mon", "Tue", "Wed", "Thu", "Fri"]
```

### 3.2 Time-Based Adjustments

**During Business Hours:**
- All priorities processed normally
- Reminders created immediately
- Notifications shown in real-time

**Outside Business Hours:**
- CRITICAL/IMPORTANT: Process normally (notify immediately)
- NORMAL: Hold until next business day
- LOW: Batch for weekly digest

**Weekends/Holidays:**
- CRITICAL: Process normally
- IMPORTANT: Hold until Monday 9 AM
- NORMAL/LOW: Batch for Monday morning digest

### 3.3 Urgent Time Markers

Increase priority if email contains:
```
"by EOD", "end of day", "within 2 hours", 
"in 30 minutes", "right now", "ASAP",
"today before", "by tomorrow", "this afternoon"
```

---

## 4. Content Analysis Rules

### 4.1 Subject Line Analysis

**Length-based scoring:**
- Very short (<10 chars): May indicate urgency → +0.1
- Very long (>80 chars): Often promotional → -0.1
- ALL CAPS: Potential urgency or spam → Review context

**Prefix detection:**
- "URGENT:", "CRITICAL:", "ACTION REQUIRED:" → +0.3
- "FYI:", "For Your Information:" → -0.2
- "Newsletter:", "Digest:" → Set to LOW

### 4.2 Body Content Analysis

**Urgency Detection:**
- Count urgency keywords in first 200 words
- Each keyword adds +0.05 (max +0.2)

**Action Items:**
- Detect phrases like "please do", "need you to", "can you"
- Each action item adds +0.1

**Questions:**
- Emails with questions may require response
- Question mark in subject → +0.1
- Multiple questions in body → +0.1

### 4.3 Sentiment Analysis

**Negative + Action = Higher Priority:**
- Negative sentiment + action verbs → +0.2
- Example: "Problem with server, need fix"

**Positive + Informational = Lower Priority:**
- Positive sentiment + informational → -0.1
- Example: "Great news! Project approved"

---

## 5. Thread Handling Rules

### 5.1 Thread Position

**First Message in Thread:**
- Normal classification rules apply
- Full summarization

**Reply in Active Thread:**
- Check if previous messages exist
- If user was asked a question → +0.2 priority
- If thread has >5 messages → Summarize entire conversation

**Long Threads (>10 messages):**
- Generate conversation summary
- Highlight unresolved items
- Flag for manual review if no resolution

### 5.2 Forwarded Messages

- Detect "Forwarded" or "Fwd:" in subject
- Check original sender importance
- Apply domain/sender rules to original sender

---

## 6. Attachment Handling

### 6.1 Attachment Detection

Emails with attachments:
- Automatically add +0.1 priority
- Note attachment count in summary
- Flag large attachments (>10MB) for review

### 6.2 Attachment Types

**High-Importance Types:**
- .pdf, .doc, .docx (documents) → +0.1
- .xls, .xlsx (spreadsheets) → +0.1
- .ppt, .pptx (presentations) → +0.1

**Caution Types:**
- .exe, .bat, .scr (executables) → Flag as suspicious
- .zip with password → Flag for manual review

---

## 7. Reply Generation Rules

### 7.1 Reply Style Selection

**Professional (Default):**
- Use for: External contacts, clients, management
- Tone: Formal, complete sentences
- Structure: Greeting + Body + Closing + Signature

**Casual:**
- Use for: Colleagues, team members, familiar contacts
- Tone: Friendly, can use contractions
- Structure: Brief greeting + Body + Sign-off

**Concise:**
- Use for: Quick confirmations, routine responses
- Tone: Direct, minimal pleasantries
- Structure: Get straight to point

### 7.2 Auto-Reply Safety Rules

**NEVER Auto-Reply To:**
- ❌ Unknown senders (not in contacts)
- ❌ Emails marked as spam
- ❌ Bulk/newsletter emails
- ❌ Emails with suspicious content
- ❌ Emails requesting sensitive info

**ALWAYS Require Manual Review:**
- ⚠️ Financial requests (payments, invoices)
- ⚠️ Requests for passwords/credentials
- ⚠️ Legal or HR matters
- ⚠️ Complaints or negative feedback
- ⚠️ First-time contact from new domain

### 7.3 Reply Content Guidelines

**Acknowledge Receipt:**
```
"Thank you for your email. I have received your message..."
```

**Set Expectations:**
```
"I will review this and get back to you by [timeframe]..."
```

**If Action Required:**
```
"I am looking into this matter and will update you soon..."
```

---

## 8. Reminder Management Rules

### 8.1 Reminder Creation Criteria

**Create Reminder When:**
- Priority = CRITICAL → Always create
- Priority = IMPORTANT → Always create
- Priority = NORMAL + Contains deadline → Create
- Priority = NORMAL + Asked direct question → Optional

**Do NOT Create Reminder When:**
- Priority = LOW → Never
- Priority = NORMAL + Informational only → Never
- Email is newsletter/promotional → Never

### 8.2 Reminder Prioritization

**CRITICAL Reminders:**
- Show at top of list
- Consider desktop notification (future)
- Auto-clean after 7 days

**IMPORTANT Reminders:**
- Show in main list
- Include in daily summary
- Auto-clean after 30 days

### 8.3 Reminder Lifecycle

```
Created → Pending → Reminded → Completed/Expired
```

**Auto-Cleanup:**
- Remind user of pending reminders daily (9 AM)
- Auto-archive after 30 days (configurable)
- Delete after 90 days

---

## 9. Security & Privacy Rules

### 9.1 Credential Handling

**Never:**
- Store main email password
- Log credentials
- Send credentials over unencrypted connection
- Share credentials with third parties

**Always:**
- Use app passwords only
- Encrypt connections (SSL/TLS)
- Store credentials in .env (gitignored)
- Rotate app passwords periodically

### 9.2 Data Privacy

**Local Processing:**
- All email processing happens locally
- Model runs on local machine
- Database stored locally (SQLite)
- No data sent to external APIs (except HF inference if using cloud)

**Logging:**
- Never log full email content
- Log only subject previews (first 50 chars)
- Never log passwords or tokens
- Redact sensitive information

### 9.3 Red Flag Detection

**Flag for Manual Review:**
- Requests for passwords or credentials
- Unexpected attachments from known contacts
- Links to unfamiliar domains
- Poor grammar/spelling in business context
- Urgent financial requests
- Requests to click links urgently
- Lottery/prize notifications
- Inheritance/money transfer offers

---

## 10. Error Handling Rules

### 10.1 Connection Errors

**Retry Logic:**
- Max retries: 3
- Delay between retries: 5 seconds (exponential backoff)
- After 3 failures: Log error, skip this cycle

**Common Errors:**
- Authentication failed → Check credentials
- Connection timeout → Check internet, increase timeout
- IMAP folder not found → Use default INBOX

### 10.2 Processing Errors

**Individual Email Failures:**
- Log error with email ID
- Continue processing other emails
- Don't fail entire batch for single email

**Model Loading Failures:**
- Retry model loading
- Fallback to basic text extraction (no AI)
- Log warning to user

### 10.3 Database Errors

**Reminder DB Corruption:**
- Backup existing DB
- Create new DB
- Attempt to recover data
- Notify user of issue

---

## 11. Customization Guide

### 11.1 Adding Custom Rules

Edit `config/rules.yaml`:

```yaml
custom_rules:
  - name: "Project Alpha Emails"
    condition:
      subject_contains: ["Project Alpha", "Alpha Initiative"]
      OR:
        sender_domain: "alpha-project.com"
    action:
      priority: IMPORTANT
      add_reminder: true
      reminder_note: "Follow up on Project Alpha"
  
  - name: "Invoice Emails"
    condition:
      subject_contains: ["invoice", "receipt", "payment"]
    action:
      priority: IMPORTANT
      create_reminder: true
      reminder_days: 7
```

### 11.2 Disabling Rules

```yaml
disabled_rules:
  - vip_sender_escalation
  - time_based_adjustments
  - sentiment_analysis
```

### 11.3 Threshold Adjustment

```yaml
priority_thresholds:
  critical: 0.75      # Default: 0.8
  important: 0.55     # Default: 0.6
  normal: 0.25        # Default: 0.3
```

Lower thresholds = More emails get higher priority
Higher thresholds = Stricter classification

---

## 12. Testing & Validation

### 12.1 Test Mode

Run agent in test mode to see classification:
```bash
python main.py --test-rules
```

### 12.2 Rule Validation Checklist

Before deploying new rules:
- [ ] Test on last 100 historical emails
- [ ] Review classification accuracy (>90% target)
- [ ] Check false positive rate (<5% target)
- [ ] Check false negative rate (<2% target)
- [ ] Adjust thresholds as needed
- [ ] Document changes
- [ ] Deploy to production

### 12.3 Performance Metrics

Track these metrics:
- Emails processed per day
- Average processing time per email
- Reminder creation rate
- User satisfaction (manual feedback)
- False positive/negative reports

---

## Version History

- **v1.0.0** (Current): Initial rule set with Hugging Face integration
- Rules designed for google/flan-t5-base model
- Optimized for lightweight processing

---

## Support & Updates

- Review rules monthly
- Update keywords based on emerging patterns
- Adjust thresholds based on user feedback
- Add new rules for edge cases

**Remember:** These rules are guidelines. The agent learns and adapts based on usage patterns (future ML feature).
