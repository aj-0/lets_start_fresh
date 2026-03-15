import logging
from hydrogram import Client, filters
from hydrogram.types import Message
from database import get_group_settings, add_group, add_user

logger = logging.getLogger(__name__)


@Client.on_message(filters.new_chat_members & filters.group)
async def welcome_member(client, message: Message):
    await add_group(message.chat.id, message.chat.title)
    settings = await get_group_settings(message.chat.id)

    # Check if welcome is enabled
    if not settings.get('welcome', False):
        return

    for member in message.new_chat_members:
        if member.is_bot:
            continue

        await add_user(member.id, member.first_name)

        welcome_text = settings.get(
            'welcome_text',
            "👋 Welcome {mention} to **{title}**!\n\nType any movie name to search our collection 🎬"
        )

        try:
            text = welcome_text.format(
                mention=member.mention,
                title=message.chat.title,
                first_name=member.first_name,
                id=member.id
            )
            await message.reply_text(text)
        except Exception as e:
            logger.warning(f"Welcome message error: {e}")
