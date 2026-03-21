import logging
import random
from hydrogram import Client, filters
from hydrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from info import ADMINS, PICS, SUPPORT_LINK, UPDATES_LINK, AUTH_CHANNEL
from database import add_user, add_group, count_files, total_users, total_groups, get_group_settings
from utils import get_size, is_subscribed
from Script import script

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("start") & filters.private)
async def start(client, message: Message):
    await add_user(message.from_user.id, message.from_user.first_name)

    # Handle file request from group
    if len(message.command) > 1:
        data = message.command[1]
        if data.startswith("file_"):
            parts = data.split("_", 2)
            if len(parts) == 3:
                _, chat_id, file_id = parts
                await send_file_to_user(client, message, chat_id, file_id)
                return

    pic = random.choice(PICS) if PICS else None
    buttons = [[
        InlineKeyboardButton("➕ Add me to Group", url=f"https://t.me/{(await client.get_me()).username}?startgroup=start"),
    ],[
        InlineKeyboardButton("📢 Updates", url=UPDATES_LINK),
        InlineKeyboardButton("🆘 Support", url=SUPPORT_LINK),
    ],[
        InlineKeyboardButton("❓ Help", callback_data="help"),
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)

    if pic:
        await message.reply_photo(
            photo=pic,
            caption=script.START_TXT.format(mention=message.from_user.mention),
            reply_markup=reply_markup
        )
    else:
        await message.reply_text(
            script.START_TXT.format(mention=message.from_user.mention),
            reply_markup=reply_markup
        )


async def send_file_to_user(client, message, chat_id, file_id):
    """Send a file from database to user's PM."""
    from database.db import files_col
    from bson import ObjectId
    from info import DELETE_TIME
    import asyncio

    try:
        file = files_col.find_one({'_id': ObjectId(file_id)})
        if not file:
            return await message.reply_text("❌ File not found! It may have been deleted.")

        # Check force sub
        settings = await get_group_settings(int(chat_id))
        if settings.get('force_sub') and settings.get('auth_channel'):
            if not await is_subscribed(client, message.from_user.id, settings['auth_channel']):
                btn = [[InlineKeyboardButton(
                    "📢 Join Channel",
                    url=f"https://t.me/{(await client.get_chat(settings['auth_channel'])).username}"
                )],[
                    InlineKeyboardButton("✅ I Joined", callback_data=f"checksub_{chat_id}_{file_id}")
                ]]
                return await message.reply_text(
                    "⚠️ You must join our channel to get files!",
                    reply_markup=InlineKeyboardMarkup(btn)
                )

        sent = await client.send_cached_media(
            chat_id=message.chat.id,
            file_id=file['file_id'],
            caption=script.FILE_CAPTION.format(file_name=file['file_name'], file_size=get_size(file['file_size']))
        )

        if settings.get('auto_delete') and DELETE_TIME > 0:
            await message.reply_text(
                f"⚠️ This file will be deleted in {DELETE_TIME // 60} minutes!"
            )
            await asyncio.sleep(DELETE_TIME)
            try:
                await sent.delete()
            except Exception:
                pass

    except Exception as e:
        logger.error(f"Error sending file: {e}")
        await message.reply_text("❌ Error sending file. Please try again.")


@Client.on_message(filters.command("help"))
async def help_cmd(client, message: Message):
    await message.reply_text(HELP_TEXT)


@Client.on_message(filters.command("stats") & filters.user(ADMINS))
async def stats(client, message: Message):
    files  = count_files()
    users  = await total_users()
    groups = await total_groups()
    await message.reply_text(
        f"📊 **Bot Statistics**\n\n"
        f"📁 Total Files: `{files}`\n"
        f"👥 Total Users: `{users}`\n"
        f"💬 Total Groups: `{groups}`"
    )


@Client.on_callback_query(filters.regex("^help$"))
async def help_callback(client, query):
    await query.message.edit_text(HELP_TEXT)


@Client.on_message(filters.new_chat_members)
async def new_group(client, message: Message):
    me = await client.get_me()
    for member in message.new_chat_members:
        if member.id == me.id:
            await add_group(message.chat.id, message.chat.title)
            await message.reply_text(
                f"👋 Thanks for adding me to **{message.chat.title}**!\n\n"
                f"📌 Make me an admin and use /index to index your movie channel.\n"
                f"Then users can search movies by typing their names!"
            )
