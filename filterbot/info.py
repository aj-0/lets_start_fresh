import re
from os import environ
import logging

logger = logging.getLogger(__name__)

def is_enabled(key, default):
    val = environ.get(key, str(default)).lower()
    if val in ["true", "yes", "1", "enable", "y"]:
        return True
    elif val in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        logger.warning(f"{key} invalid value, using default: {default}")
        return default

# ── Required ──────────────────────────────────────────────────────────────────
API_ID = environ.get('API_ID', '')
if not API_ID:
    logger.error('API_ID is missing'); exit()
API_ID = int(API_ID)

API_HASH = environ.get('API_HASH', '')
if not API_HASH:
    logger.error('API_HASH is missing'); exit()

BOT_TOKEN = environ.get('BOT_TOKEN', '')
if not BOT_TOKEN:
    logger.error('BOT_TOKEN is missing'); exit()

DATABASE_URL = environ.get('DATABASE_URL', '')
if not DATABASE_URL:
    logger.error('DATABASE_URL is missing'); exit()

DATABASE_NAME = environ.get('DATABASE_NAME', 'filterbot')

LOG_CHANNEL = environ.get('LOG_CHANNEL', '')
if not LOG_CHANNEL:
    logger.error('LOG_CHANNEL is missing'); exit()
LOG_CHANNEL = int(LOG_CHANNEL)

ADMINS = environ.get('ADMINS', '')
if not ADMINS:
    logger.error('ADMINS is missing'); exit()
ADMINS = [int(x) for x in ADMINS.split()]

# ── Channels ──────────────────────────────────────────────────────────────────
INDEX_CHANNELS = []
raw = environ.get('INDEX_CHANNELS', '')
if raw:
    INDEX_CHANNELS = [int(x) if x.startswith('-') else x for x in raw.split()]

AUTH_CHANNEL = environ.get('AUTH_CHANNEL', '')
AUTH_CHANNEL = int(AUTH_CHANNEL) if AUTH_CHANNEL else None

SUPPORT_GROUP = environ.get('SUPPORT_GROUP', '')
SUPPORT_GROUP = int(SUPPORT_GROUP) if SUPPORT_GROUP else None

# ── Your Links (set these in env vars) ────────────────────────────────────────
SUPPORT_LINK  = environ.get('SUPPORT_LINK',  'https://t.me/your_support_group')
UPDATES_LINK  = environ.get('UPDATES_LINK',  'https://t.me/your_channel')
TUTORIAL_LINK = environ.get('TUTORIAL_LINK', 'https://t.me/your_channel')

# ── Shortlink (admin can toggle per group) ────────────────────────────────────
SHORTLINK_URL = environ.get('SHORTLINK_URL', 'linkpays.in')
SHORTLINK_API = environ.get('SHORTLINK_API', '')

# ── Bot Settings ──────────────────────────────────────────────────────────────
PORT          = int(environ.get('PORT', 8080))
URL           = environ.get('URL', '')
if URL and not URL.endswith('/'):
    URL += '/'

PICS = environ.get('PICS', '').split()

MAX_BTN       = int(environ.get('MAX_BTN', 10))
DELETE_TIME   = int(environ.get('DELETE_TIME', 300))   # seconds, 0 = never
CACHE_TIME    = int(environ.get('CACHE_TIME', 300))

# ── Feature Toggles (defaults — admin can override per group) ─────────────────
IMDB          = is_enabled('IMDB', True)
SPELL_CHECK   = is_enabled('SPELL_CHECK', True)
AUTO_DELETE   = is_enabled('AUTO_DELETE', False)
SHORTLINK     = is_enabled('SHORTLINK', False)  # OFF by default
FORCE_SUB     = is_enabled('FORCE_SUB', False)
WELCOME       = is_enabled('WELCOME', False)

# ── File settings ─────────────────────────────────────────────────────────────
INDEX_EXTENSIONS = [x.lower() for x in environ.get('INDEX_EXTENSIONS', 'mp4 mkv avi mov').split()]
