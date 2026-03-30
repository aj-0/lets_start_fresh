import logging
from hydrogram import Client, filters
from hydrogram.types import Message
from info import ADMINS, INDEX_CHANNELS, INDEX_EXTENSIONS
from database import save_file, delete_all_files, count_files

logger = logging.getLogger(__name__)


@Client.on_message(filters.command("index") & filters.user(ADMINS))
async def index_command(client, message: Message):
    """
    Usage:
    1. /index — indexes all INDEX_CHANNELS from env
    2. /index -1001234567890 — indexes a specific channel by ID
    3. Forward any message from a channel then reply /index — indexes that channel
    """

    channels_to_index = []

    # Case 1: Reply to a forwarded message — get channel from it
    if message.reply_to_message:
        fwd = message.reply_to_message
        if fwd.forward_from_chat:
            ch_id = fwd.forward_from_chat.id
            channels_to_index.append(ch_id)
            await message.reply_text(
                f"📡 Detected channel from forwarded message!\n"
                f"Channel: **{fwd.forward_from_chat.title}**\n"
                f"ID: `{ch_id}`\n\n"
                f"⏳ Starting index..."
            )
        else:
            return await message.reply_text(
                "❌ That message is not forwarded from a channel!\n\n"
                "Forward any message from the channel you want to index, then reply /index to it."
            )

    # Case 2: /index -1001234567890 — channel ID provided directly
    elif len(message.command) > 1:
        try:
            ch_id = int(message.command[1])
            channels_to_index.append(ch_id)
        except ValueError:
            return await message.reply_text(
                "❌ Invalid channel ID!\n\n"
                "Usage: `/index -1001234567890`"
            )

    # Case 3: /index alone — use INDEX_CHANNELS from env
    else:
        if INDEX_CHANNELS:
            channels_to_index = INDEX_CHANNELS
        else:
            return await message.reply_text(
                "❌ No channels to index!\n\n"
                "**3 ways to use /index:**\n\n"
                "1️⃣ Forward any message from your channel → reply `/index`\n\n"
                "2️⃣ `/index -1001234567890` — direct channel ID\n\n"
                "3️⃣ Set `INDEX_CHANNELS` in environment variables"
            )

    await _do_index(client, message, channels_to_index)


async def _do_index(client, message, channels):
    """Core indexing function."""
    status      = await message.reply_text("⏳ Indexing started...")
    total_saved = 0
    total_skip  = 0
    total_err   = 0

    for channel in channels:
        try:
            chat = await client.get_chat(channel)
            await status.edit_text(
                f"📂 Indexing: **{chat.title}**\n"
                f"⏳ Please wait, this may take a while..."
            )

            msg_id        = 1
            batch_size    = 200
            empty_batches = 0

            while empty_batches < 3:
                try:
                    ids      = list(range(msg_id, msg_id + batch_size))
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
                                caption=msg.caption or '',
                                chat_id=channel,
                                msg_id=msg.id
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
            await status.edit_text(f"❌ Cannot access channel `{channel}`:\n`{e}`\n\nMake sure bot is admin in that channel!")
            return

    total = count_files()
    await status.edit_text(
        f"✅ **Indexing Complete!**\n\n"
        f"📂 Channel(s): `{len(channels)}`\n"
        f"➕ New files saved: `{total_saved}`\n"
        f"⏭ Duplicates skipped: `{total_skip}`\n"
        f"❌ Errors: `{total_err}`\n"
        f"📁 Total files in DB: `{total}`"
    )


@Client.on_message(filters.command("delete_all") & filters.user(ADMINS))
async def delete_all(client, message: Message):
    await message.reply_text(
        "⚠️ Are you sure you want to delete **ALL** indexed files?\n\n"
        "Reply with /confirm_delete to proceed."
    )


@Client.on_message(filters.command("confirm_delete") & filters.user(ADMINS))
async def confirm_delete(client, message: Message):
    status  = await message.reply_text("🗑 Deleting all files...")
    deleted = delete_all_files()
    await status.edit_text(f"✅ Deleted `{deleted}` files from database.")


@Client.on_message(filters.command("files") & filters.user(ADMINS))
async def file_count(client, message: Message):
    total = count_files()
    await message.reply_text(f"📁 Total indexed files: `{total}`")


@Client.on_message(filters.command("index_channels") & filters.user(ADMINS))
async def show_index_channels(client, message: Message):
    if not INDEX_CHANNELS:
        return await message.reply_text(
            "❌ No INDEX_CHANNELS in env variables.\n\n"
            "Use `/index -1001234567890` or forward a message and reply `/index`"
        )
    text = "📋 **Channels in INDEX_CHANNELS env:**\n\n"
    for ch in INDEX_CHANNELS:
        try:
            chat  = await client.get_chat(ch)
            text += f"• **{chat.title}** (`{ch}`)\n"
        except Exception:
            text += f"• `{ch}`\n"
    await message.reply_text(text)
