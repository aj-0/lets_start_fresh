import logging
from hydrogram import Client, filters
from hydrogram.types import Message
from info import ADMINS
from database.db import users_col, groups_col

logger = logging.getLogger(__name__)

BANNED_USERS = set()


@Client.on_message(filters.command("ban") & filters.user(ADMINS))
async def ban_user(client, message: Message):
    user_id = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        try:
            user_id = int(message.command[1])
        except ValueError:
            return await message.reply_text("❌ Invalid user ID!")

    if not user_id:
        return await message.reply_text("Reply to a user or provide user ID!")

    BANNED_USERS.add(user_id)
    await users_col.update_one({'id': user_id}, {'$set': {'banned': True}}, upsert=True)
    await message.reply_text(f"✅ User `{user_id}` has been banned.")


@Client.on_message(filters.command("unban") & filters.user(ADMINS))
async def unban_user(client, message: Message):
    user_id = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        try:
            user_id = int(message.command[1])
        except ValueError:
            return await message.reply_text("❌ Invalid user ID!")

    if not user_id:
        return await message.reply_text("Reply to a user or provide user ID!")

    BANNED_USERS.discard(user_id)
    await users_col.update_one({'id': user_id}, {'$set': {'banned': False}})
    await message.reply_text(f"✅ User `{user_id}` has been unbanned.")


@Client.on_message(filters.command("users") & filters.user(ADMINS))
async def list_users(client, message: Message):
    total = await users_col.count_documents({})
    banned = await users_col.count_documents({'banned': True})
    await message.reply_text(
        f"👥 **Users Report**\n\n"
        f"Total Users: `{total}`\n"
        f"Banned Users: `{banned}`"
    )


@Client.on_message(filters.command("groups") & filters.user(ADMINS))
async def list_groups(client, message: Message):
    total = await groups_col.count_documents({})
    await message.reply_text(f"💬 Total Groups: `{total}`")


@Client.on_message(filters.command("leave") & filters.user(ADMINS))
async def leave_group(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/leave <chat_id>`")
    try:
        chat_id = int(message.command[1])
        await client.leave_chat(chat_id)
        await message.reply_text(f"✅ Left chat `{chat_id}`")
    except Exception as e:
        await message.reply_text(f"❌ Error: `{e}`")
