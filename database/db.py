import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from info import DATABASE_URL, DATABASE_NAME

logger = logging.getLogger(__name__)

# Async client for bot operations
async_client = AsyncIOMotorClient(DATABASE_URL)
async_db = async_client[DATABASE_NAME]

# Sync client for indexing
sync_client = MongoClient(DATABASE_URL)
sync_db = sync_client[DATABASE_NAME]

# Collections
files_col     = sync_db['files']
users_col     = async_db['users']
groups_col    = async_db['groups']
settings_col  = async_db['settings']

# ── Indexes ───────────────────────────────────────────────────────────────────
def ensure_indexes():
    files_col.create_index([('file_name', 'text')], default_language='english')
    files_col.create_index('file_id', unique=True)
    logger.info("Database indexes ensured")

# ── File operations ───────────────────────────────────────────────────────────
def save_file(file_id, file_name, file_size, file_type, caption=''):
    try:
        files_col.insert_one({
            'file_id':   file_id,
            'file_name': file_name,
            'file_size': file_size,
            'file_type': file_type,
            'caption':   caption,
        })
        return True
    except DuplicateKeyError:
        return False

def search_files(query, max_results=10, offset=0):
    query = query.strip()
    if not query:
        return [], 0
    cursor = files_col.find(
        {'$text': {'$search': query}},
        {'score': {'$meta': 'textScore'}}
    ).sort([('score', {'$meta': 'textScore'})]).skip(offset).limit(max_results)
    results = list(cursor)
    total   = files_col.count_documents({'$text': {'$search': query}})
    return results, total

def delete_all_files():
    result = files_col.delete_many({})
    return result.deleted_count

def count_files():
    return files_col.count_documents({})

# ── User operations ───────────────────────────────────────────────────────────
async def add_user(user_id, name):
    if not await users_col.find_one({'id': user_id}):
        await users_col.insert_one({'id': user_id, 'name': name})

async def total_users():
    return await users_col.count_documents({})

async def get_all_users():
    return users_col.find({})

# ── Group operations ──────────────────────────────────────────────────────────
async def add_group(chat_id, title):
    if not await groups_col.find_one({'id': chat_id}):
        await groups_col.insert_one({'id': chat_id, 'title': title})

async def total_groups():
    return await groups_col.count_documents({})

# ── Per-group settings ────────────────────────────────────────────────────────
DEFAULT_SETTINGS = {
    'shortlink':    False,
    'shortlink_url': '',
    'shortlink_api': '',
    'auto_delete':  False,
    'imdb':         True,
    'spell_check':  True,
    'force_sub':    False,
    'auth_channel': None,
    'welcome':      False,
    'welcome_text': 'Welcome {mention} to {title}!',
}

async def get_group_settings(chat_id):
    doc = await settings_col.find_one({'chat_id': chat_id})
    if not doc:
        doc = {'chat_id': chat_id, **DEFAULT_SETTINGS}
        await settings_col.insert_one(doc)
    # Merge missing keys with defaults
    for k, v in DEFAULT_SETTINGS.items():
        if k not in doc:
            doc[k] = v
    return doc

async def update_group_setting(chat_id, key, value):
    await settings_col.update_one(
        {'chat_id': chat_id},
        {'$set': {key: value}},
        upsert=True
    )
