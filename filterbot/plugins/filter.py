import asyncio
import logging
import re
from hydrogram import Client, filters
from hydrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from info import ADMINS, MAX_BTN, DELETE_TIME, SUPPORT_GROUP
from database import search_files, get_group_settings, add_user
from utils import get_size, get_shortlink, get_imdb_info, get_spell_suggestions, is_subscribed

logger = logging.getLogger(__name__)

# In-memory store for search results
SEARCH_CACHE = {}


def clean_query(text):
    """Clean search query."""
    text = re.sub(r'[-:"\';!@#$%^&*()]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


@Client.on_message(filters.group & filters.text & filters.incoming)
async def group_filter(client, message: Message):
    """Main auto filter handler for groups."""
    if not message.text or message.text.startswith('/'):
        return
    if not message.from_user:
        return

    await add_user(message.from_user.id, message.from_user.first_name)

    chat_id  = message.chat.id
    settings = await get_group_settings(chat_id)

    # Force subscribe check
    if settings.get('force_sub') and settings.get('auth_channel'):
        if not await is_subscribed(client, message.from_user.id, settings['auth_channel']):
            try:
                channel = await client.get_chat(settings['auth_channel'])
                inv = await client.export_chat_invite_link(settings['auth_channel'])
                btn = [[InlineKeyboardButton("📢 Join Channel", url=inv)]]
                k = await message.reply_text(
                    f"⚠️ {message.from_user.mention}, join our channel first to use this bot!",
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                await asyncio.sleep(30)
                await k.delete()
            except Exception as e:
                logger.warning(f"Force sub error: {e}")
            return

    query   = clean_query(message.text)
    if len(query) < 2:
        return

    # Show searching message
    s = await message.reply(f"🔍 Searching for `{query}`...")

    files, total = search_files(query, max_results=MAX_BTN)

    if not files:
        # Spell check
        if settings.get('spell_check', True):
            await show_spell_suggestions(client, message, s, query)
        else:
            await s.edit_text(f"❌ No results found for **{query}**")
        return

    # Build result
    await show_results(client, message, s, query, files, total, settings)


async def show_results(client, message, s, query, files, total, settings):
    """Show search results with file buttons."""
    chat_id = message.chat.id
    user_id = message.from_user.id
    key     = f"{chat_id}_{message.id}"
    SEARCH_CACHE[key] = {'query': query, 'offset': 0}

    # Build file buttons
    btn = []
    for file in files:
        btn.append([
            InlineKeyboardButton(
                text=f"📁 {file['file_name'][:50]} [{get_size(file['file_size'])}]",
                callback_data=f"file_{chat_id}_{str(file['_id'])}"
            )
        ])

    # Pagination
    if total > MAX_BTN:
        btn.append([
            InlineKeyboardButton(f"1/{-((-total) // MAX_BTN)}", callback_data="pages"),
            InlineKeyboardButton("Next »", callback_data=f"next_{key}_0_{user_id}")
        ])

    # Send All button (shortlink or direct)
    if settings.get('shortlink') and settings.get('shortlink_url') and settings.get('shortlink_api'):
        send_all_url = await get_shortlink(
            settings['shortlink_url'],
            settings['shortlink_api'],
            f"https://t.me/{(await client.get_me()).username}?start=all_{chat_id}_{key}"
        )
        btn.insert(0, [InlineKeyboardButton("📦 Send All Files ♻️", url=send_all_url)])
    else:
        btn.insert(0, [InlineKeyboardButton("📦 Send All Files", callback_data=f"sendall_{key}_{user_id}")])

    # IMDB info
    caption = f"🎬 Found **{total}** results for `{query}`\n\n"
    photo   = None

    if settings.get('imdb', True):
        imdb = await get_imdb_info(query)
        if imdb:
            caption = (
                f"🎬 **{imdb['title']}** ({imdb['year']})\n"
                f"⭐ Rating: {imdb['rating']}/10\n"
                f"🎭 Genre: {imdb['genres']}\n"
                f"🌐 Language: {imdb['languages']}\n"
                f"👥 Cast: {imdb['cast']}\n\n"
                f"📖 {imdb['plot'][:200]}...\n\n"
                f"Found **{total}** file(s) 👇"
            )
            photo = imdb.get('poster')

    # Auto delete notice
    del_notice = ''
    if settings.get('auto_delete') and DELETE_TIME > 0:
        del_notice = f"\n\n⚠️ Files auto-delete in {DELETE_TIME // 60} minutes"

    await s.delete()

    try:
        if photo:
            k = await message.reply_photo(
                photo=photo,
                caption=caption[:1024] + del_notice,
                reply_markup=InlineKeyboardMarkup(btn)
            )
        else:
            k = await message.reply_text(
                caption + del_notice,
                reply_markup=InlineKeyboardMarkup(btn)
            )
    except Exception:
        k = await message.reply_text(
            caption + del_notice,
            reply_markup=InlineKeyboardMarkup(btn)
        )

    # Auto delete
    if settings.get('auto_delete') and DELETE_TIME > 0:
        await asyncio.sleep(DELETE_TIME)
        try:
            await k.delete()
            await message.delete()
        except Exception:
            pass


async def show_spell_suggestions(client, message, s, query):
    """Show IMDB spell check suggestions."""
    movies = await get_spell_suggestions(query)
    if not movies:
        await s.edit_text(
            f"❌ No results found for **{query}**\n\n"
            "💡 Try different spelling or keywords!"
        )
        return

    btn = []
    for movie in movies[:5]:
        title = movie.get('title', '')
        year  = movie.get('year', '')
        label = f"{title} ({year})" if year else title
        btn.append([InlineKeyboardButton(label, callback_data=f"spell_{movie.movieID}")])

    btn.append([InlineKeyboardButton("❌ Close", callback_data="close")])

    await s.edit_text(
        f"❓ Did you mean one of these for **{query}**?",
        reply_markup=InlineKeyboardMarkup(btn)
    )


@Client.on_callback_query(filters.regex(r"^file_"))
async def file_callback(client, query):
    """Handle file button click — redirect user to PM."""
    _, chat_id, file_id = query.data.split("_", 2)
    me = await client.get_me()
    await query.answer(
        url=f"https://t.me/{me.username}?start=file_{chat_id}_{file_id}"
    )


@Client.on_callback_query(filters.regex(r"^sendall_"))
async def send_all_callback(client, query):
    """Handle send all button."""
    parts   = query.data.split("_")
    key     = f"{parts[1]}_{parts[2]}"
    user_id = int(parts[3])

    if query.from_user.id != user_id:
        return await query.answer("This is not for you!", show_alert=True)

    cache = SEARCH_CACHE.get(key)
    if not cache:
        return await query.answer("Session expired. Search again.", show_alert=True)

    files, total = search_files(cache['query'], max_results=50)
    me = await client.get_me()
    await query.answer(
        url=f"https://t.me/{me.username}?start=all_{key}"
    )


@Client.on_callback_query(filters.regex(r"^spell_"))
async def spell_callback(client, query):
    """Handle spell check movie selection."""
    movie_id = query.data.split("_")[1]
    from imdb import Cinemagoer
    ia = Cinemagoer()
    try:
        movie  = ia.get_movie(movie_id)
        search = movie.get('title', '')
        s = await query.message.edit_text(f"🔍 Searching for `{search}`...")
        files, total = search_files(search, max_results=MAX_BTN)
        if not files:
            await s.edit_text(f"❌ No results for **{search}**")
            return
        settings = await get_group_settings(query.message.chat.id)
        await show_results(client, query, s, search, files, total, settings)
    except Exception as e:
        logger.error(f"Spell callback error: {e}")
        await query.answer("Error! Try again.", show_alert=True)


@Client.on_callback_query(filters.regex(r"^close$"))
async def close_callback(client, query):
    await query.message.delete()


@Client.on_callback_query(filters.regex(r"^pages$"))
async def pages_callback(client, query):
    await query.answer("Page info", show_alert=False)
