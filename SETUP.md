# GetaPro Job Monitor - Setup Guide

Monitors job postings on getapro.lv and sends Telegram notifications.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` and follow the instructions
3. You'll receive a bot token like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
4. Open your new bot and send it a message (e.g., `/start`)

### 3. Run Setup Script

```bash
python setup_telegram.py
```

This will:
- Verify your bot token
- Get your chat ID automatically  
- Send a test message
- Update `config.json` with your credentials

### 4. Configure Categories

Edit `config.json` and add categories you want to monitor:

```json
{
  "enabled_categories": [
    "it-pakalpojumi",
    "dizains-maksla-reklama",
    "foto-video-audio"
  ]
}
```

Available categories:
- `celtniecibas-darbi` - Construction work
- `apdares-darbi` - Finishing work
- `sadzives-remonts` - Home repairs
- `uzkopsanas-pakalpojumi` - Cleaning services
- `darza-un-zemes-darbi` - Garden and land work
- `sadzives-pakalpojumi` - Household services
- `dizains-maksla-reklama` - Design, art, advertising
- `piegade-un-parvadajumi` - Delivery and transportation
- `mebelu-izgatavosana` - Furniture making
- `profesionalie-pakalpojumi` - Professional services
- `foto-video-audio` - Photo, video and audio
- `pasakumu-organizesana` - Event organization
- `it-pakalpojumi` - Internet and IT services
- `majskolotaji-instruktori` - Tutors, instructors
- `elektrotehnikas-remonts` - Electronics repair
- `transportlidzeklu-remonts` - Vehicle repair
- `skaistums-un-veseliba` - Beauty and health
- `cits` - Other

### 5. Run the Monitor

**Test run (single check):**
```bash
python scraper.py --once
```

**Continuous monitoring:**
```bash
python scraper.py
```

## Cloud Deployment

### Option 1: Railway.app (Free tier available)

1. Create account at [railway.app](https://railway.app)
2. Create new project from GitHub or upload files
3. Add environment variables:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
4. Deploy!

### Option 2: Render.com

1. Create account at [render.com](https://render.com)
2. Create new "Background Worker"
3. Connect your repo or upload
4. Set environment variables
5. Deploy

### Option 3: PythonAnywhere (Free tier)

1. Create account at [pythonanywhere.com](https://pythonanywhere.com)
2. Upload files to your account
3. Set up a scheduled task to run every 10 minutes:
   ```
   /home/yourusername/getapro-job-monitor/scraper.py --once
   ```

### Option 4: Your own server/VPS

```bash
# Using screen
screen -S jobmonitor
python scraper.py
# Ctrl+A, D to detach

# Or using systemd service
# See systemd/getapro-monitor.service
```

## Files

- `scraper.py` - Main scraper and monitor
- `config.json` - Configuration file
- `setup_telegram.py` - Telegram bot setup helper
- `test_scraper.py` - Test the scraper without notifications
- `seen_jobs.json` - Auto-generated, tracks seen jobs
- `requirements.txt` - Python dependencies

