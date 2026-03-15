import logging
from hydrogram import Client, filters
from hydrogram.types import Message
from info import ADMINS, INDEX_CHANNELS, INDEX_EXTENSIONS
from database import save_file, delete_all_files, count_files

logger = logging.getLogger(__name__)


@Client.on_message(filters.command("index") & filters.user(ADMINS))
async def index_files(client, message: Message):
    """Index files from INDEX_CHANNELS."""
    if not INDEX_CHANNELS:
        return await message.reply_text(
            "❌ No INDEX_CHANNELS set!\n\n"
            "Add `INDEX_CHANNELS` in your environment variables with your channel ID."
        )

    status = await message.reply_text("⏳ Starting indexing...")
    total_saved = 0
    total_skip  = 0
    total_err   = 0

    for channel in INDEX_CHANNELS:
        try:
            chat = await client.get_chat(channel)
            await status.edit_text(f"📂 Indexing: **{chat.title}**\nPlease wait...")

            async for msg in client.get_chat_history(channel):
                try:
                    file = None
                    if msg.document:
                        file = msg.document
                    elif msg.video:
                        file = msg.video
                    elif msg.audio:
                        file = msg.audio

                    if not file:
                        continue

                    name = getattr(file, 'file_name', '') or ''
                    ext  = name.rsplit('.', 1)[-1].lower() if '.' in name else ''

                    if INDEX_EXTENSIONS and ext not in INDEX_EXTENSIONS:
                        continue

                    saved = save_file(
                        file_id=file.file_id,
                        file_name=name or f"file_{file.file_unique_id}",
                        file_size=file.file_size or 0,
                        file_type=ext,
                        caption=msg.caption or ''
                    )
                    if saved:
                        total_saved += 1
                    else:
                        total_skip += 1

                except Exception as e:
                    total_err += 1
                    logger.warning(f"File index error: {e}")

        except Exception as e:
            logger.error(f"Channel index error for {channel}: {e}")
            await status.edit_text(f"❌ Error accessing channel `{channel}`:\n`{e}`")
            return

    total = count_files()
    await status.edit_text(
        f"✅ **Indexing Complete!**\n\n"
        f"➕ New files saved: `{total_saved}`\n"
        f"⏭ Duplicates skipped: `{total_skip}`\n"
        f"❌ Errors: `{total_err}`\n"
        f"📁 Total files in DB: `{total}`"
    )


@Client.on_message(filters.command("delete_all") & filters.user(ADMINS))
async def delete_all(client, message: Message):
    """Delete all indexed files."""
    confirm = await message.reply_text(
        "⚠️ Are you sure you want to delete ALL indexed files?\n\n"
        "Reply with /confirm_delete to proceed."
    )


@Client.on_message(filters.command("confirm_delete") & filters.user(ADMINS))
async def confirm_delete(client, message: Message):
    status = await message.reply_text("🗑 Deleting all files...")
    deleted = delete_all_files()
    await status.edit_text(f"✅ Deleted `{deleted}` files from database.")


@Client.on_message(filters.command("files") & filters.user(ADMINS))
async def file_count(client, message: Message):
    total = count_files()
    await message.reply_text(f"📁 Total indexed files: `{total}`")
