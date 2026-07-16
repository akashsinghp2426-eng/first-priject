# 🚀 Quick Start Guide - Mail Agent

Get your email agent running in **5 minutes**!

## Step 1: Install Python (if not installed)

Download Python 3.8+ from https://www.python.org/downloads/

Verify installation:
```bash
python --version
```

## Step 2: Install Dependencies

Open Command Prompt (Windows) or Terminal (Mac/Linux):

```bash
cd D:/Mail_agent
pip install -r requirements.txt
```

**Note:** First-time installation may take 5-10 minutes to download the Hugging Face model (~300MB).

## Step 3: Get Your Email Credentials

### For Gmail Users:

1. **Enable 2-Factor Authentication:**
   - Go to https://myaccount.google.com/security
   - Click "2-Step Verification" → Enable it

2. **Create App Password:**
   - Go to https://myaccount.google.com/apppasswords
   - Select app: "Mail"
   - Select device: "Other (Custom name)"
   - Enter name: "MailAgent"
   - Click "Generate"
   - **Copy the 16-character password** (save it securely!)

3. **Enable IMAP:**
   - Go to Gmail Settings → See all settings
   - Click "Forwarding and POP/IMAP" tab
   - Select "Enable IMAP"
   - Click "Save Changes"

### For Outlook Users:

1. **Enable 2-Factor Authentication:**
   - Go to https://account.microsoft.com/security
   - Click "Advanced security options"
   - Enable two-step verification

2. **Create App Password:**
   - In same security page, find "App passwords"
   - Click "Create a new app password"
   - **Copy the generated password** (save it securely!)

3. **Enable IMAP:**
   - Go to Outlook Settings → Mail → Sync email
   - Ensure IMAP is enabled

## Step 4: Get Hugging Face Token

1. Go to https://huggingface.co/settings/tokens
2. Click "Create new token"
3. Name it: "MailAgent"
4. Type: "Read"
5. Click "Generate token"
6. **Copy the token** (starts with `hf_...`)

## Step 5: Configure Your Agent

### Create .env file:

**Windows (Command Prompt):**
```cmd
copy .env.example .env
```

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**Mac/Linux:**
```bash
cp .env.example .env
```

### Edit .env file:

Open `.env` in any text editor and fill in:

```env
EMAIL_ADDRESS=your.email@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop
HF_API_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx
```

**Important Notes:**
- Use the **app password** (16 chars for Gmail), NOT your regular email password
- For Gmail app password, you can include or omit spaces (both work)
- Hugging Face token starts with `hf_`

### Edit config.yaml (Optional):

Open `config/config.yaml` and verify:

```yaml
email:
  provider: gmail  # Change to 'outlook' if using Outlook
  
llm:
  model_name: google/flan-t5-base  # Lightweight model - perfect!
```

## Step 6: Run Your Agent!

### Test Run (Recommended First):
```bash
python main.py --test
```

This will:
- Connect to your email
- Fetch unread emails
- Generate summaries
- Create reminders for important emails
- Exit after one run

**Expected Output:**
```
2024-01-15 10:00:00 - MailAgent - INFO - ============================================================
2024-01-15 10:00:00 - MailAgent - INFO - Mail Agent Starting...
2024-01-15 10:00:00 - MailAgent - INFO - Mode: TEST
2024-01-15 10:00:00 - MailAgent - INFO - ============================================================
2024-01-15 10:00:01 - MailAgent - INFO - Configuration loaded successfully
2024-01-15 10:00:02 - MailAgent - INFO - Initializing gmail connector...
2024-01-15 10:00:03 - MailAgent - INFO - Connected to gmail
Loading model: google/flan-t5-base on cpu...
Model loaded successfully!
2024-01-15 10:00:15 - MailAgent - INFO - Initializing summarizer with model: google/flan-t5-base
2024-01-15 10:00:15 - MailAgent - INFO - Initializing reply generator...
Reply generator loaded!
2024-01-15 10:00:15 - MailAgent - INFO - Initializing reminder manager (DB: reminders.db)
2024-01-15 10:00:15 - MailAgent - INFO - All components initialized successfully
2024-01-15 10:00:15 - MailAgent - INFO - Fetching emails from INBOX...
2024-01-15 10:00:17 - MailAgent - INFO - Found 5 new email(s)

Processing email: Project Update - Weekly Status...
Summary: Weekly project status update including completed tasks, 
         upcoming milestones, and team availability.
✓ Created IMPORTANT reminder

Processing email: Newsletter - Tech News...
Summary: Latest technology news and industry updates.

📌 You have 1 pending reminder(s):
  [IMPORTANT] Project Update - Weekly Status - From: manager@company.com

✅ Processing complete: 5 emails processed, 1 reminders created
2024-01-15 10:00:25 - MailAgent - INFO - Single check completed
2024-01-15 10:00:25 - MailAgent - INFO - Mail Agent stopped
```

### Continuous Mode (Background Operation):
```bash
python main.py --continuous
```

This will:
- Check email every 15 minutes
- Run indefinitely until you press Ctrl+C
- Perfect for keeping running in background

### Custom Interval:
```bash
python main.py --continuous --interval 30
```
Check every 30 minutes instead of default 15.

## Step 7: Verify It's Working

### Check Logs:
```bash
# View log file
type logs\mail_agent.log  # Windows
cat logs/mail_agent.log   # Mac/Linux
```

### Check Reminders Database:
```bash
# Open Python interactive
python

>>> from src.reminders import ReminderManager
>>> rm = ReminderManager()
>>> rm.get_pending_reminders()
[Reminder(id=1, email_id='123', subject='Meeting Tomorrow', ...)]

>>> rm.get_stats()
{'total': 5, 'pending': 3, 'critical': 1, 'important': 2, 'reminded': 2}
```

## Troubleshooting

### ❌ "Authentication failed"
**Solution:** 
- Make sure you're using **app password**, not regular password
- For Gmail: Must enable 2FA first, then create app password
- Check for typos in .env file

### ❌ "Connection timeout"
**Solution:**
- Check internet connection
- Verify IMAP is enabled in email settings
- Try increasing timeout in config.yaml

### ❌ "Model loading failed"
**Solution:**
- First run downloads model (~300MB) - be patient
- Check internet connection
- Ensure enough disk space (at least 500MB free)

### ❌ "No module named 'src'"
**Solution:**
- Run from correct directory: `cd D:/Mail_agent`
- Or run as: `python -m main --test`

### ❌ Gmail "Less secure apps" error
**Solution:**
- You MUST use app password (not regular password)
- Regular passwords don't work anymore for Gmail
- Follow Step 3 above exactly

## What Happens Next?

Once running, your agent will:

1. ✅ **Connect** to your email every 15 minutes
2. ✅ **Fetch** new unread emails
3. ✅ **Summarize** each email using AI
4. ✅ **Classify** priority (CRITICAL/IMPORTANT/NORMAL/LOW)
5. ✅ **Create reminders** ONLY for important emails
6. ✅ **Mark emails as read** (configurable)
7. ✅ **Show you** pending reminders

## Daily Workflow Example

**Morning:**
```bash
# Start agent
python main.py --continuous
```

**Throughout day:**
- Agent checks email every 15 minutes
- Creates reminders for important emails only
- You see notifications in console

**Evening:**
- Press `Ctrl+C` to stop
- Or let it keep running 24/7

**Next day:**
```bash
# Check what reminders you have
python -c "from src.reminders import ReminderManager; rm = ReminderManager(); print(rm.get_pending_reminders())"
```

## Pro Tips

1. **Run in separate window:** Keep agent running in dedicated terminal window
2. **Check logs regularly:** `logs/mail_agent.log` has detailed info
3. **Customize rules:** Edit `config/rules.yaml` for your needs
4. **Backup reminders:** Copy `reminders.db` periodically
5. **Test first:** Always use `--test` before `--continuous`

## Need Help?

- Read full documentation: `README.md`
- Understand rules: `RULES.md`
- Check FAQ in README.md
- Review logs in `logs/` folder

---

**You're all set! 🎉**

Your lightweight, privacy-focused email agent is ready to help you manage emails efficiently!
