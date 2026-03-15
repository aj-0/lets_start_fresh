import logging
from hydrogram import Client, filters
from hydrogram.types import Message
from info import ADMINS, INDEX_CHANNELS, INDEX_EXTENSIONS
from database import save_file, delete_all_files, count_files

logger = logging.getLogger(__name__)


@Client.on_message(filters.command("index") & filters.user(ADMINS))
async def index_files(client, message: Message):
    """Index files from INDEX_CHANNELS using bot-compatible method."""
    if not INDEX_CHANNELS:
        return await message.reply_text(
            "❌ No INDEX_CHANNELS set!\n\n"
            "Add INDEX_CHANNELS in your environment variables."
        )

    status = await message.reply_text("⏳ Starting indexing...")
    total_saved = 0
    total_skip  = 0
    total_err   = 0

    for channel in INDEX_CHANNELS:
        try:
            chat = await client.get_chat(channel)
            await status.edit_text(
                f"📂 Indexing: **{chat.title}**\n"
                f"⏳ This may take a while for large channels..."
            )

            msg_id      = 1
            batch_size  = 200
            empty_batches = 0

            while empty_batches < 3:
                try:
                    ids = list(range(msg_id, msg_id + batch_size))
                    messages = await client.get_messages(channel, ids)

                    has_content = False
                    for msg in messages:
                        if not msg or not msg.id:
                            continue
                        has_content = True
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
                            logger.warning(f"File error: {e}")

                    if not has_content:
                        empty_batches += 1
                    else:
                        empty_batches = 0

                    msg_id += batch_size

                    if msg_id % 1000 == 1:
                        await status.edit_text(
                            f"📂 Indexing: **{chat.title}**\n"
                            f"✅ Saved: `{total_saved}`\n"
                            f"⏭ Skipped: `{total_skip}`\n"
                            f"🔄 Scanning message #{msg_id}..."
                        )

                except Exception as e:
                    logger.warning(f"Batch error at {msg_id}: {e}")
                    msg_id += batch_size
                    continue

        except Exception as e:
            logger.error(f"Channel error {channel}: {e}")
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
    await message.reply_text(
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


@Client.on_message(filters.command("index_channels") & filters.user(ADMINS))
async def show_index_channels(client, message: Message):
    if not INDEX_CHANNELS:
        return await message.reply_text("❌ No INDEX_CHANNELS configured!")
    text = "📋 **Indexed Channels:**\n\n"
    for ch in INDEX_CHANNELS:
        try:
            chat = await client.get_chat(ch)
            text += f"• {chat.title} (`{ch}`)\n"
        except Exception:
            text += f"• `{ch}` (can't fetch name)\n"
    await message.reply_text(text)
