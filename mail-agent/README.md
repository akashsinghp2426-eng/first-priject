# 📧 Mail Agent - Intelligent Email Assistant

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intelligent email agent that connects to your Gmail or Outlook account, automatically summarizes emails, generates replies, and creates reminders for important messages only. **Uses lightweight Hugging Face models** - no large downloads required!

## ✨ Features

- 🔗 **Connect to Gmail & Outlook** via IMAP/SMTP (no desktop app needed)
- 🤖 **AI-Powered Summarization** using lightweight Hugging Face models (~300MB)
- ✍️ **Smart Reply Generation** with customizable tones (professional, casual, concise)
- 📌 **Intelligent Reminders** - Only for CRITICAL and IMPORTANT emails
- 🎯 **Priority Classification** - Automatic detection of urgent vs. low-priority emails
- ⚙️ **Highly Configurable** - Customize rules, thresholds, and behavior
- 🔒 **Secure** - Uses app passwords, never stores your main password
- 📊 **Daily Summaries** - Get digest of all processed emails

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd D:/Mail_agent
pip install -r requirements.txt
```

### 2. Get Your Credentials

#### For Gmail:
1. Go to https://myaccount.google.com/security
2. Enable 2-Factor Authentication
3. Go to https://myaccount.google.com/apppasswords
4. Create an app password for "Mail"
5. Save the 16-character password

#### For Outlook:
1. Go to https://account.microsoft.com/security
2. Enable 2-Factor Authentication  
3. Create an app password
4. Save the password

#### Get Hugging Face Token:
1. Go to https://huggingface.co/settings/tokens
2. Click "Create new token"
3. Give it a name (e.g., "MailAgent")
4. Copy the token (starts with `hf_`)

### 3. Configure
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
# EMAIL_ADDRESS=your.email@gmail.com
# EMAIL_PASSWORD=your-16-char-app-password
# HF_API_TOKEN=hf_your-huggingface-token
```

Edit `config/config.yaml`:
```yaml
email:
  provider: gmail  # or outlook
```

### 4. Run!
```bash
# Test run (process once)
python main.py --test

# Continuous mode (check every 15 minutes)
python main.py --continuous
```

## 📁 Project Structure

```
D:/Mail_agent/
├── main.py                      # Entry point
├── requirements.txt             # Dependencies
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── README.md                    # This file
├── QUICKSTART.md               # Quick start guide
├── RULES.md                     # Agent rule base
├── config/
│   ├── config.yaml             # Main configuration
│   └── rules.yaml              # Priority & behavior rules
├── templates/
│   └── email_templates.yaml    # Reply templates
├── src/
│   ├── agents/
│   │   └── mail_agent.py       # Main orchestrator
│   ├── connectors/
│   │   ├── base_connector.py   # Abstract base
│   │   ├── gmail_connector.py  # Gmail implementation
│   │   └── outlook_connector.py # Outlook implementation
│   ├── summarizers/
│   │   └── llm_summarizer.py   # Hugging Face summarization
│   ├── repliers/
│   │   └── llm_replier.py      # Reply generation
│   ├── reminders/
│   │   └── reminder_manager.py # Reminder system
│   └── utils/
│       ├── logger.py           # Logging
│       └── config_loader.py    # Configuration
├── tests/                       # Test files
└── logs/                        # Log files
```

## 🎯 How It Works

### Email Processing Flow
1. **Connect** to your email provider (Gmail/Outlook) via IMAP
2. **Fetch** unread emails from inbox
3. **Summarize** each email using Hugging Face AI
4. **Classify** priority (CRITICAL, IMPORTANT, NORMAL, LOW)
5. **Create Reminders** only for CRITICAL and IMPORTANT emails
6. **Mark as Read** processed emails
7. **Display** summaries and pending reminders

### Priority Classification

| Priority | When | Action |
|----------|------|--------|
| 🔴 CRITICAL | Urgent, emergency, ASAP, deadline today | Immediate reminder + notification |
| 🟠 IMPORTANT | Meeting, deadline, action required | Create reminder |
| 🟡 NORMAL | Regular business emails | Summary only |
| 🟢 LOW | Newsletters, promotions | Brief summary, no reminder |

### Example Output
```
2024-01-15 10:30:00 - MailAgent - INFO - Fetching emails from INBOX...
2024-01-15 10:30:02 - MailAgent - INFO - Found 3 new email(s)

Processing email: URGENT: Server Down - Immediate Action...
Summary: Server outage reported in production environment. 
         DevOps team investigating. ETA for resolution: 2 hours.
✓ Created CRITICAL reminder

Processing email: Meeting Request: Q4 Planning...
Summary: Quarterly planning meeting scheduled for next Tuesday.
         Agenda includes budget review and goal setting.
✓ Created IMPORTANT reminder

Processing email: Weekly Newsletter - Tech Updates...
Summary: Latest tech news including AI advancements and startup funding.

📌 You have 2 pending reminder(s):
  [CRITICAL] URGENT: Server Down - From: ops@company.com
  [IMPORTANT] Meeting Request: Q4 Planning - From: manager@company.com

✅ Processing complete: 3 emails processed, 2 reminders created
```

## ⚙️ Configuration

### Email Settings (`config/config.yaml`)
```yaml
email:
  provider: gmail  # gmail or outlook
  check_interval: 15  # minutes
  max_emails_per_check: 50
  mark_as_read: true
```

### AI Settings
```yaml
llm:
  provider: huggingface
  model_name: google/flan-t5-base  # Lightweight model
  summary_max_length: 150
  reply_style: professional
```

### Reminder Settings
```yaml
reminders:
  enabled: true
  db_path: reminders.db
  auto_clean_days: 30
```

## 🔐 Security

- ✅ Uses **app passwords** (not your main password)
- ✅ **IMAP/SSL** encryption for all connections
- ✅ Credentials stored in `.env` (gitignored)
- ✅ No data sent to third-party services (if using local HF model)
- ✅ SQLite database for local reminder storage

## 🛠️ Advanced Usage

### Generate Reply Without Sending
```python
from src.agents.mail_agent import MailAgent
from src.utils.config_loader import ConfigLoader

config = ConfigLoader('config/config.yaml')
agent = MailAgent(config)

# After processing emails, generate reply
reply = agent.generate_reply(email, style='professional')
print(reply)
```

### Check Reminders
```bash
# View pending reminders
python -c "from src.reminders import ReminderManager; rm = ReminderManager(); print(rm.get_pending_reminders())"
```

### Custom Rules
Edit `config/rules.yaml` to add custom classification rules:
```yaml
custom_rules:
  - name: "VIP Client Emails"
    condition:
      sender_domain: "vip-client.com"
    action:
      priority: IMPORTANT
```

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Test mode (single run, verbose)
python main.py --test

# Test with specific config
python main.py --config config/test_config.yaml
```

## 📦 Dependencies

- **transformers** - Hugging Face AI models
- **torch** - PyTorch backend
- **beautifulsoup4** - HTML parsing
- **python-dotenv** - Environment variables
- **PyYAML** - Configuration
- **schedule** - Task scheduling
- **colorama** - Colored logs

All dependencies are open-source and free!

## 🚀 Deployment Options

### Option 1: Run as Background Service (Linux/Mac)
```bash
# Create systemd service
sudo nano /etc/systemd/system/mail-agent.service

# Start service
sudo systemctl start mail-agent
sudo systemctl enable mail-agent
```

### Option 2: Windows Task Scheduler
```powershell
# Create scheduled task
schtasks /create /tn "MailAgent" /tr "python D:\Mail_agent\main.py --continuous" /sc onstart /ru SYSTEM
```

### Option 3: Docker (Coming Soon)
```bash
docker build -t mail-agent .
docker run -d --name mail-agent mail-agent
```

### Option 4: Cron Job (Linux/Mac)
```bash
# Edit crontab
crontab -e

# Add line to run every 15 minutes
*/15 * * * * cd /path/to/mail-agent && python main.py --continuous
```

## ❓ FAQ

### Q: Do I need to install Gmail/Outlook desktop app?
**A:** No! The agent connects directly via IMAP/SMTP protocols. No desktop application needed.

### Q: Is my email password safe?
**A:** Yes! Use app passwords (not your main password). Credentials are stored locally in `.env` file which is gitignored.

### Q: How much disk space does this need?
**A:** Very little! The Hugging Face model (google/flan-t5-base) is only ~300MB. Much smaller than Ollama (several GB).

### Q: Can I use this with multiple email accounts?
**A:** Currently supports one account per instance. You can run multiple instances with different configs.

### Q: Does it work offline?
**A:** Email connection requires internet. Model runs locally after initial download.

### Q: How do I stop reminders for certain senders?
**A:** Add them to `low_priority_domains` in `config/rules.yaml` or create custom rules.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Make changes
4. Submit pull request

## 📄 License

MIT License - See LICENSE file for details.

## 🙏 Acknowledgments

- Hugging Face for excellent open-source models
- Google for FLAN-T5 model
- Python community for amazing libraries

## 📞 Support

- Documentation: See `QUICKSTART.md` and `RULES.md`
- Issues: GitHub Issues
- Questions: Check FAQ above

---

**Made with ❤️ using open-source technologies**
