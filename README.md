# 🔔 GetaPro Job Monitor

Monitors [getapro.lv](https://getapro.lv/job) for new job postings and sends **Telegram notifications**.

## Features

- ✅ Monitors multiple job categories
- ✅ Telegram notifications for new jobs
- ✅ **Telegram commands** to manage categories
- ✅ Runs every 10 minutes (configurable)
- ✅ Tracks seen jobs (no duplicates)

## Telegram Commands

| Command | Description |
|---------|-------------|
| `/help` | Show all commands |
| `/status` | Bot status and active categories |
| `/categories` | Show active categories |
| `/list` | List all available categories |
| `/add <category>` | Add a category |
| `/remove <category>` | Remove a category |
| `/check` | Check for new jobs now |

## Available Categories

- `it-pakalpojumi` - IT services, programming
- `dizains-maksla-reklama` - Design, art, advertising
- `foto-video-audio` - Photo, video, audio
- `celtniecibas-darbi` - Construction
- `apdares-darbi` - Finishing work
- `sadzives-remonts` - Home repairs
- `profesionalie-pakalpojumi` - Professional services
- And more... (use `/list` in Telegram)

## Quick Deploy to Replit

1. Fork this repo
2. Go to [replit.com](https://replit.com) → Import from GitHub
3. Add these **Secrets** (Environment Variables):
   - `TELEGRAM_BOT_TOKEN` = your bot token
   - `TELEGRAM_CHAT_ID` = your chat ID
   - `ENABLED_CATEGORIES` = `it-pakalpojumi,dizains-maksla-reklama`
4. Click **Run**

## Local Setup

```bash
pip install -r requirements.txt
python setup_telegram.py  # Configure Telegram
python scraper.py         # Run monitor
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID |
| `ENABLED_CATEGORIES` | Comma-separated category slugs |
| `CHECK_INTERVAL_MINUTES` | Check interval (default: 10) |

## Create Telegram Bot

1. Open Telegram, search **@BotFather**
2. Send `/newbot`, follow instructions
3. Copy the token
4. Message your bot, then run `setup_telegram.py` to get chat ID

