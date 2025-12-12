"""
GetaPro.lv Job Monitor
Scrapes jobs from getapro.lv and sends Telegram notifications for new jobs
"""

import os
import requests
from bs4 import BeautifulSoup
import json
import time
import base64
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# File paths
CONFIG_FILE = Path(__file__).parent / "config.json"
SEEN_JOBS_FILE = Path(__file__).parent / "seen_jobs.json"


class GetaProScraper:
    """Scraper for GetaPro.lv job listings"""
    
    BASE_URL = "https://getapro.lv"
    JOBS_URL = "https://getapro.lv/job"
    
    # All available categories with their URL slugs
    CATEGORIES = {
        "celtniecibas-darbi": {
            "id": 8,
            "name": "Celtniecības darbi",
            "url": "/job/index/8-celtniecibas-darbi"
        },
        "apdares-darbi": {
            "id": 10,
            "name": "Apdares darbi",
            "url": "/job/index/10-apdares-darbi"
        },
        "sadzives-remonts": {
            "id": 1,
            "name": "Sadzīves remonts",
            "url": "/job/index/1-sadzives-remonts"
        },
        "uzkopsanas-pakalpojumi": {
            "id": 2,
            "name": "Uzkopšanas pakalpojumi",
            "url": "/job/index/2-uzkopsanas-pakalpojumi"
        },
        "darza-un-zemes-darbi": {
            "id": 15,
            "name": "Dārza un zemes darbi",
            "url": "/job/index/15-darza-un-zemes-darbi"
        },
        "sadzives-pakalpojumi": {
            "id": 19,
            "name": "Sadzīves pakalpojumi",
            "url": "/job/index/19-sadzives-pakalpojumi"
        },
        "dizains-maksla-reklama": {
            "id": 16,
            "name": "Dizains, māksla, reklāma",
            "url": "/job/index/16-dizains-maksla-reklama"
        },
        "piegade-un-parvadajumi": {
            "id": 3,
            "name": "Piegāde un pārvadājumi",
            "url": "/job/index/3-piegade-un-parvadajumi"
        },
        "mebelu-izgatavosana": {
            "id": 11,
            "name": "Mēbeļu un interjera priekšmetu izgatavošana",
            "url": "/job/index/11-mebelu-un-interjera-prieksmetu-izgatavosan"
        },
        "profesionalie-pakalpojumi": {
            "id": 6,
            "name": "Profesionālie pakalpojumi",
            "url": "/job/index/6-profesionalie-pakalpojumi"
        },
        "foto-video-audio": {
            "id": 17,
            "name": "Foto, video un audio",
            "url": "/job/index/17-foto-video-un-audio"
        },
        "pasakumu-organizesana": {
            "id": 9,
            "name": "Pasākumu organizēšana",
            "url": "/job/index/9-pasakumu-organizesana"
        },
        "it-pakalpojumi": {
            "id": 13,
            "name": "Internets un IT pakalpojumi",
            "url": "/job/index/13-internets-un-it-pakalpojumi"
        },
        "majskolotaji-instruktori": {
            "id": 14,
            "name": "Mājskolotāji, instruktori",
            "url": "/job/index/14-majskolotaji-instruktori"
        },
        "elektrotehnikas-remonts": {
            "id": 12,
            "name": "Elektrotehnikas remonts",
            "url": "/job/index/12-elektrotehnikas-remonts"
        },
        "transportlidzeklu-remonts": {
            "id": 7,
            "name": "Transportlīdzekļu remonts",
            "url": "/job/index/7-transportlidzeklu-remonts"
        },
        "skaistums-un-veseliba": {
            "id": 5,
            "name": "Skaistums un veselība",
            "url": "/job/index/5-skaistums-un-veseliba"
        },
        "cits": {
            "id": 4,
            "name": "Cits",
            "url": "/job/index/4-cits"
        }
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'lv,en;q=0.9',
        })
    
    def scrape_jobs(self, category_slug: Optional[str] = None) -> List[Dict]:
        """
        Scrape jobs from GetaPro.lv
        
        Args:
            category_slug: Optional category slug to filter jobs
            
        Returns:
            List of job dictionaries
        """
        if category_slug and category_slug in self.CATEGORIES:
            url = self.BASE_URL + self.CATEGORIES[category_slug]["url"]
            category_name = self.CATEGORIES[category_slug]["name"]
        else:
            url = self.JOBS_URL
            category_name = "Visi"
        
        logger.info(f"Scraping jobs from: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch jobs: {e}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = []
        
        # Find all job cards using the correct class
        job_cards = soup.select('.job-list-item')
        
        # Parse each job card
        for card in job_cards:
            try:
                job = self._parse_job_card(card, category_name)
                if job:
                    jobs.append(job)
            except Exception as e:
                logger.debug(f"Failed to parse job card: {e}")
                continue
        
        logger.info(f"Found {len(jobs)} jobs in category: {category_name}")
        return jobs
    
    def _parse_job_card(self, card, category_name: str) -> Optional[Dict]:
        """Parse a single job card element using data attributes and HTML structure"""
        
        # Get data from attributes (most reliable)
        job_id = card.get('data-id')
        if not job_id:
            return None
        
        title = card.get('data-name', '')
        location = card.get('data-brand', '')  # 'brand' is location in their system
        price_value = card.get('data-price', '0')
        date_posted = card.get('data-variant', '')
        
        # Get the URL from data-href (base64 encoded)
        data_href = card.get('data-href', '')
        job_url = ""
        if data_href:
            try:
                decoded_path = base64.b64decode(data_href).decode('utf-8')
                job_url = self.BASE_URL + decoded_path
            except Exception:
                job_url = f"{self.BASE_URL}/job/details/{job_id}"
        else:
            job_url = f"{self.BASE_URL}/job/details/{job_id}"
        
        # Get description from content section
        content_elem = card.select_one('.job-list__content p')
        description = content_elem.get_text(strip=True) if content_elem else ""
        description = description.strip('"').strip()
        
        # Get subcategory from the first list item
        subcategory_elem = card.select_one('.job-post-tags li:first-child i')
        subcategory = subcategory_elem.get_text(strip=True) if subcategory_elem else ""
        
        # Get price from price li
        price_elem = card.select_one('.job-post-tags li.price i')
        price = price_elem.get_text(strip=True) if price_elem else ""
        
        # Get time posted from time li
        time_elem = card.select_one('.job-post-tags li.time i')
        time_posted = time_elem.get_text(strip=True) if time_elem else ""
        
        # Get location from address span (more accurate than data attribute)
        address_elem = card.select_one('.address')
        if address_elem:
            location = address_elem.get_text(strip=True)
        
        job = {
            'id': job_id,  # Use the actual job ID from the site
            'title': title,
            'description': description,
            'category': category_name,
            'subcategory': subcategory,
            'price': price if price and price != 'Nav norādīts' else 'Nav norādīts',
            'location': location or 'Nav norādīts',
            'time_posted': time_posted,
            'url': job_url,
            'date_posted': date_posted,
            'scraped_at': datetime.now().isoformat()
        }
        
        return job
    
    def scrape_all_categories(self, category_slugs: List[str]) -> List[Dict]:
        """Scrape jobs from multiple categories"""
        all_jobs = []
        seen_ids = set()
        
        for slug in category_slugs:
            if slug not in self.CATEGORIES:
                logger.warning(f"Unknown category: {slug}")
                continue
            
            jobs = self.scrape_jobs(slug)
            for job in jobs:
                if job['id'] not in seen_ids:
                    all_jobs.append(job)
                    seen_ids.add(job['id'])
            
            # Small delay between requests
            time.sleep(1)
        
        return all_jobs


class TelegramBot:
    """Telegram bot with command handling and notifications"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        self.last_update_id = 0
    
    def send_message(self, text: str, parse_mode: str = "HTML", chat_id: str = None) -> bool:
        """Send a message via Telegram"""
        url = f"{self.api_url}/sendMessage"
        payload = {
            'chat_id': chat_id or self.chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_web_page_preview': True
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    def get_updates(self) -> List[Dict]:
        """Get new messages/commands from Telegram"""
        url = f"{self.api_url}/getUpdates"
        params = {
            'offset': self.last_update_id + 1,
            'timeout': 1
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('ok') and data.get('result'):
                updates = data['result']
                if updates:
                    self.last_update_id = updates[-1]['update_id']
                return updates
        except Exception as e:
            logger.debug(f"Error getting updates: {e}")
        
        return []
    
    def process_commands(self, config_manager) -> None:
        """Check for and process any pending commands"""
        updates = self.get_updates()
        
        for update in updates:
            if 'message' not in update:
                continue
            
            message = update['message']
            chat_id = str(message['chat']['id'])
            
            # Only respond to authorized user
            if chat_id != self.chat_id:
                continue
            
            text = message.get('text', '')
            if not text.startswith('/'):
                continue
            
            # Parse command
            parts = text.split(maxsplit=1)
            command = parts[0].lower().split('@')[0]  # Handle @botname suffix
            args = parts[1] if len(parts) > 1 else ""
            
            # Handle commands
            if command == '/start' or command == '/help':
                self._cmd_help(chat_id)
            elif command == '/status':
                self._cmd_status(chat_id, config_manager)
            elif command == '/categories':
                self._cmd_categories(chat_id, config_manager)
            elif command == '/list':
                self._cmd_list(chat_id)
            elif command == '/add':
                self._cmd_add(chat_id, args, config_manager)
            elif command == '/remove':
                self._cmd_remove(chat_id, args, config_manager)
            elif command == '/check':
                self._cmd_check(chat_id)
            elif command == '/latest':
                self._cmd_latest(chat_id, config_manager)
            elif command == '/interval':
                self._cmd_interval(chat_id, args, config_manager)
    
    def _cmd_help(self, chat_id: str):
        """Show help message"""
        help_text = """🤖 <b>GetaPro Job Monitor</b>

<b>Komandas:</b>
/status - Bota statuss
/categories - Aktīvās kategorijas
/list - Visas pieejamās kategorijas
/add [kategorija] - Pievienot kategoriju
/remove [kategorija] - Noņemt kategoriju
/latest - Rādīt 10 jaunākos darbus
/interval [min] - Mainīt pārbaudes intervālu
/check - Pārbaudīt jaunus darbus tagad
/help - Rādīt šo palīdzību"""
        self.send_message(help_text, chat_id=chat_id)
    
    def _cmd_status(self, chat_id: str, config_manager):
        """Show bot status"""
        config = config_manager.get_config()
        categories = config.get('enabled_categories', [])
        interval = config.get('check_interval_minutes', 10)
        
        status = f"""✅ <b>Bots darbojas!</b>

⏰ Pārbaudes intervāls: {interval} min
📁 Aktīvās kategorijas: {len(categories)}
"""
        for cat in categories:
            cat_name = GetaProScraper.CATEGORIES.get(cat, {}).get('name', cat)
            status += f"\n  • {cat_name}"
        
        self.send_message(status, chat_id=chat_id)
    
    def _cmd_categories(self, chat_id: str, config_manager):
        """Show active categories"""
        config = config_manager.get_config()
        categories = config.get('enabled_categories', [])
        
        if not categories:
            self.send_message("❌ Nav aktīvu kategoriju!\n\nIzmanto /add lai pievienotu.", chat_id=chat_id)
            return
        
        msg = "📁 <b>Aktīvās kategorijas:</b>\n"
        for cat in categories:
            cat_name = GetaProScraper.CATEGORIES.get(cat, {}).get('name', cat)
            msg += f"\n  • <code>{cat}</code>\n    {cat_name}"
        
        msg += "\n\n💡 Izmanto /remove &lt;kategorija&gt; lai noņemtu"
        self.send_message(msg, chat_id=chat_id)
    
    def _cmd_list(self, chat_id: str):
        """List all available categories"""
        msg = "📋 <b>Pieejamās kategorijas:</b>\n"
        
        for slug, info in GetaProScraper.CATEGORIES.items():
            msg += f"\n<code>{slug}</code>\n  {info['name']}\n"
        
        msg += "\n💡 Izmanto /add &lt;kategorija&gt; lai pievienotu"
        self.send_message(msg, chat_id=chat_id)
    
    def _cmd_add(self, chat_id: str, category: str, config_manager):
        """Add a category"""
        category = category.strip().lower()
        
        if not category:
            self.send_message("❌ Norādi kategoriju!\n\nPiemērs: /add it-pakalpojumi\n\nIzmanto /list lai redzētu pieejamās.", chat_id=chat_id)
            return
        
        if category not in GetaProScraper.CATEGORIES:
            self.send_message(f"❌ Nezināma kategorija: <code>{category}</code>\n\nIzmanto /list lai redzētu pieejamās.", chat_id=chat_id)
            return
        
        config = config_manager.get_config()
        categories = config.get('enabled_categories', [])
        
        if category in categories:
            cat_name = GetaProScraper.CATEGORIES[category]['name']
            self.send_message(f"ℹ️ Kategorija jau ir aktīva:\n{cat_name}", chat_id=chat_id)
            return
        
        categories.append(category)
        config['enabled_categories'] = categories
        config_manager.save_config(config)
        
        cat_name = GetaProScraper.CATEGORIES[category]['name']
        self.send_message(f"✅ Kategorija pievienota!\n\n<b>{cat_name}</b>", chat_id=chat_id)
    
    def _cmd_remove(self, chat_id: str, category: str, config_manager):
        """Remove a category"""
        category = category.strip().lower()
        
        if not category:
            self.send_message("❌ Norādi kategoriju!\n\nPiemērs: /remove foto-video-audio\n\nIzmanto /categories lai redzētu aktīvās.", chat_id=chat_id)
            return
        
        config = config_manager.get_config()
        categories = config.get('enabled_categories', [])
        
        if category not in categories:
            self.send_message(f"❌ Kategorija nav aktīva: <code>{category}</code>\n\nIzmanto /categories lai redzētu aktīvās.", chat_id=chat_id)
            return
        
        categories.remove(category)
        config['enabled_categories'] = categories
        config_manager.save_config(config)
        
        cat_name = GetaProScraper.CATEGORIES.get(category, {}).get('name', category)
        self.send_message(f"✅ Kategorija noņemta!\n\n<b>{cat_name}</b>", chat_id=chat_id)
    
    def _cmd_check(self, chat_id: str):
        """Trigger a check (handled by main loop)"""
        self.send_message("🔍 Pārbaudu jaunus darbus...", chat_id=chat_id)
        # The actual check is triggered by setting a flag that main loop reads
        self._force_check = True
    
    def _cmd_latest(self, chat_id: str, config_manager):
        """Show 10 latest jobs"""
        self.send_message("🔍 Meklēju jaunākos darbus...", chat_id=chat_id)
        
        config = config_manager.get_config()
        categories = config.get('enabled_categories', [])
        
        if not categories:
            self.send_message("❌ Nav aktīvu kategoriju!\n\nIzmanto /add lai pievienotu.", chat_id=chat_id)
            return
        
        scraper = GetaProScraper()
        all_jobs = []
        
        # Scrape from enabled categories (limit to avoid too many messages)
        for cat in categories[:3]:  # Max 3 categories
            try:
                jobs = scraper.scrape_jobs(cat)
                all_jobs.extend(jobs[:5])  # Max 5 per category
                time.sleep(0.5)  # Small delay
            except Exception as e:
                logger.error(f"Error scraping {cat}: {e}")
        
        if not all_jobs:
            self.send_message("❌ Nav atrasti darbi", chat_id=chat_id)
            return
        
        # Send first 10 jobs
        for job in all_jobs[:10]:
            msg = f"📋 <b>{job['title']}</b>\n"
            msg += f"📁 {job['category']}\n"
            if job.get('subcategory'):
                msg += f"📂 {job['subcategory']}\n"
            msg += f"💰 {job.get('price', 'Nav norādīts')}\n"
            msg += f"📍 {job.get('location', 'Nav norādīts')}\n"
            msg += f"⏰ {job.get('time_posted', '')}\n"
            if job.get('description'):
                desc = job['description'][:150]
                msg += f"\n📝 {desc}{'...' if len(job['description']) > 150 else ''}\n"
            msg += f"\n🔗 <a href=\"{job.get('url', 'https://getapro.lv/job')}\">Skatīt pasūtījumu</a>"
            self.send_message(msg, chat_id=chat_id)
            time.sleep(0.3)  # Small delay between messages
    
    def _cmd_interval(self, chat_id: str, minutes: str, config_manager):
        """Change check interval"""
        if not minutes.strip():
            # Show current interval
            config = config_manager.get_config()
            current = config.get('check_interval_minutes', 10)
            self.send_message(
                f"⏰ Pašreizējais intervāls: <b>{current} min</b>\n\n"
                f"Lai mainītu: /interval 5\n"
                f"(Min: 1, Max: 60 minūtes)",
                chat_id=chat_id
            )
            return
        
        try:
            mins = int(minutes.strip())
            if mins < 1 or mins > 60:
                self.send_message("❌ Intervālam jābūt no 1 līdz 60 minūtēm", chat_id=chat_id)
                return
            
            config = config_manager.get_config()
            config['check_interval_minutes'] = mins
            config_manager.save_config(config)
            
            self.send_message(
                f"✅ Intervāls nomainīts uz <b>{mins} min</b>\n\n"
                f"⚠️ Restartē botu lai izmaiņas stātos spēkā",
                chat_id=chat_id
            )
        except ValueError:
            self.send_message("❌ Norādi minūtes!\n\nPiemērs: /interval 5", chat_id=chat_id)
    
    def should_force_check(self) -> bool:
        """Check if user requested immediate check"""
        result = getattr(self, '_force_check', False)
        self._force_check = False
        return result
    
    def format_job_message(self, job: Dict) -> str:
        """Format a job as a Telegram message"""
        message = f"""🆕 <b>Jauns pasūtījums!</b>

📋 <b>{job['title']}</b>

📁 Kategorija: {job['category']}
{f"📂 Apakškategorija: {job['subcategory']}" if job.get('subcategory') else ""}
💰 Cena: {job.get('price', 'Nav norādīts')}
📍 Vieta: {job.get('location', 'Nav norādīts')}
⏰ {job.get('time_posted', '')}

📝 {job['description'][:300]}{'...' if len(job.get('description', '')) > 300 else ''}

🔗 <a href="{job.get('url', 'https://getapro.lv/job')}">Skatīt pasūtījumu</a>"""
        
        return message
    
    def notify_new_job(self, job: Dict) -> bool:
        """Send notification for a new job"""
        message = self.format_job_message(job)
        return self.send_message(message)


# Keep TelegramNotifier as alias for backwards compatibility
TelegramNotifier = TelegramBot


class ConfigManager:
    """Manages configuration loading and saving"""
    
    def __init__(self):
        self._config = None
        self._load()
    
    def _load(self):
        """Load configuration from file and environment variables"""
        config = {}
        
        # Load from file if exists
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
        
        # Environment variables override file config (for cloud deployment)
        if os.environ.get('TELEGRAM_BOT_TOKEN'):
            config['telegram_bot_token'] = os.environ['TELEGRAM_BOT_TOKEN']
        if os.environ.get('TELEGRAM_CHAT_ID'):
            config['telegram_chat_id'] = os.environ['TELEGRAM_CHAT_ID']
        if os.environ.get('CHECK_INTERVAL_MINUTES'):
            config['check_interval_minutes'] = int(os.environ['CHECK_INTERVAL_MINUTES'])
        if os.environ.get('ENABLED_CATEGORIES'):
            config['enabled_categories'] = os.environ['ENABLED_CATEGORIES'].split(',')
        
        self._config = config
    
    def get_config(self) -> Dict:
        """Get current config (reloads from file)"""
        self._load()
        return self._config.copy()
    
    def save_config(self, config: Dict):
        """Save config to file"""
        # Keep internal fields
        save_config = config.copy()
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(save_config, f, indent=2, ensure_ascii=False)
        
        self._config = config


class JobMonitor:
    """Main job monitoring class"""
    
    def __init__(self):
        self.scraper = GetaProScraper()
        self.config_manager = ConfigManager()
        self.seen_jobs = self._load_seen_jobs()
        self.bot = None
        
        config = self.config_manager.get_config()
        if config.get('telegram_bot_token') and config.get('telegram_chat_id'):
            self.bot = TelegramBot(
                config['telegram_bot_token'],
                config['telegram_chat_id']
            )
    
    def _load_seen_jobs(self) -> set:
        """Load set of already seen job IDs"""
        if SEEN_JOBS_FILE.exists():
            with open(SEEN_JOBS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('seen_ids', []))
        return set()
    
    def _save_seen_jobs(self):
        """Save seen job IDs to file"""
        with open(SEEN_JOBS_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'seen_ids': list(self.seen_jobs),
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)
    
    def check_for_new_jobs(self) -> List[Dict]:
        """Check for new jobs and notify"""
        config = self.config_manager.get_config()
        categories = config.get('enabled_categories', [])
        
        if not categories:
            logger.warning("No categories enabled in config!")
            return []
        
        logger.info(f"Checking categories: {categories}")
        
        # Scrape jobs from enabled categories
        jobs = self.scraper.scrape_all_categories(categories)
        new_jobs = []
        
        for job in jobs:
            if job['id'] not in self.seen_jobs:
                new_jobs.append(job)
                self.seen_jobs.add(job['id'])
                
                # Send notification
                if self.bot:
                    success = self.bot.notify_new_job(job)
                    if success:
                        logger.info(f"Notified: {job['title']}")
                    else:
                        logger.error(f"Failed to notify: {job['title']}")
                else:
                    logger.info(f"New job (no notifier): {job['title']}")
        
        # Save updated seen jobs
        self._save_seen_jobs()
        
        logger.info(f"Found {len(new_jobs)} new jobs out of {len(jobs)} total")
        return new_jobs
    
    def run_once(self):
        """Run a single check"""
        logger.info("Starting job check...")
        new_jobs = self.check_for_new_jobs()
        logger.info(f"Check complete. {len(new_jobs)} new jobs found.")
        return new_jobs
    
    def run_continuous(self, interval_minutes: int = 10):
        """Run continuous monitoring with command handling"""
        logger.info(f"Starting continuous monitoring (interval: {interval_minutes} min)")
        
        if self.bot:
            self.bot.send_message("🚀 <b>Bot startēts!</b>\n\nIzmanto /help lai redzētu komandas.")
        
        last_check = 0
        check_interval = interval_minutes * 60
        command_poll_interval = 2  # Check for commands every 2 seconds
        
        while True:
            try:
                # Process any pending Telegram commands
                if self.bot:
                    self.bot.process_commands(self.config_manager)
                    
                    # Check if user requested immediate check
                    if self.bot.should_force_check():
                        self.run_once()
                        last_check = time.time()
                
                # Check for new jobs at interval
                current_time = time.time()
                if current_time - last_check >= check_interval:
                    self.run_once()
                    last_check = current_time
                
                # Small sleep to avoid hammering CPU/API
                time.sleep(command_poll_interval)
                
            except KeyboardInterrupt:
                logger.info("Stopping monitor...")
                if self.bot:
                    self.bot.send_message("🛑 Bot apturēts.")
                break
            except Exception as e:
                logger.error(f"Error during check: {e}")
                time.sleep(10)  # Wait a bit before retrying


def main():
    """Main entry point"""
    monitor = JobMonitor()
    
    # Check if running in continuous mode
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        monitor.run_once()
    else:
        config = monitor.config_manager.get_config()
        interval = config.get('check_interval_minutes', 10)
        monitor.run_continuous(interval)


if __name__ == "__main__":
    main()

