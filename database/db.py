import logging
import re
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from info import DATABASE_URL, DATABASE_NAME

logger = logging.getLogger(__name__)

async_client = AsyncIOMotorClient(DATABASE_URL)
async_db     = async_client[DATABASE_NAME]
sync_client  = MongoClient(DATABASE_URL)
sync_db      = sync_client[DATABASE_NAME]

files_col    = sync_db['files']
users_col    = async_db['users']
groups_col   = async_db['groups']
settings_col = async_db['settings']


def ensure_indexes():
    files_col.create_index([('file_name', 'text')], default_language='english')
    files_col.create_index('file_id', unique=True)
    logger.info("Database indexes ensured")


def search_files(query, max_results=10, offset=0):
    """
    Accurate search — filters by ALL words in query using regex.
    Falls back to text search if no regex results.
    """
    query = query.strip()
    if not query:
        return [], 0

    # Build regex pattern — all words must appear in filename
    words   = re.split(r'\s+', query.lower())
    pattern = ''.join(f'(?=.*{re.escape(w)})' for w in words)

    try:
        # Primary: regex search (most accurate)
        regex_filter = {'file_name': {'$regex': pattern, '$options': 'i'}}
        total  = files_col.count_documents(regex_filter)
        cursor = files_col.find(regex_filter).skip(offset).limit(max_results)
        results = list(cursor)

        if results:
            return results, total

        # Fallback: text search
        text_filter = {'$text': {'$search': query}}
        total   = files_col.count_documents(text_filter)
        cursor  = files_col.find(
            text_filter,
            {'score': {'$meta': 'textScore'}}
        ).sort([('score', {'$meta': 'textScore'})]).skip(offset).limit(max_results)
        return list(cursor), total

    except Exception as e:
        logger.error(f"Search error: {e}")
        return [], 0


def save_file(file_id, file_name, file_size, file_type, caption='', chat_id=None, msg_id=None):
    try:
        files_col.insert_one({
            'file_id':   file_id,
            'file_name': file_name,
            'file_size': file_size,
            'file_type': file_type,
            'caption':   caption,
            'chat_id':   chat_id,
            'msg_id':    msg_id,
        })
        return True
    except DuplicateKeyError:
        return False


def delete_all_files():
    return files_col.delete_many({}).deleted_count


def count_files():
    return files_col.count_documents({})


async def add_user(user_id, name):
    if not await users_col.find_one({'id': user_id}):
        await users_col.insert_one({'id': user_id, 'name': name})


async def total_users():
    return await users_col.count_documents({})


async def get_all_users():
    return users_col.find({})


async def add_group(chat_id, title):
    if not await groups_col.find_one({'id': chat_id}):
        await groups_col.insert_one({'id': chat_id, 'title': title})


async def total_groups():
    return await groups_col.count_documents({})


DEFAULT_SETTINGS = {
    'shortlink':     False,
    'shortlink_url': '',
    'shortlink_api': '',
    'auto_delete':   False,
    'imdb':          True,
    'spell_check':   True,
    'force_sub':     False,
    'auth_channel':  None,
    'welcome':       False,
    'welcome_text':  'Welcome {mention} to {title}!',
}


async def get_group_settings(chat_id):
    doc = await settings_col.find_one({'chat_id': chat_id})
    if not doc:
        doc = {'chat_id': chat_id, **DEFAULT_SETTINGS}
        await settings_col.insert_one(doc)
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
