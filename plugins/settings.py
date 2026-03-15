import logging
from hydrogram import Client, filters
from hydrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from info import ADMINS
from database import get_group_settings, update_group_setting

logger = logging.getLogger(__name__)


async def is_admin(client, chat_id, user_id):
    if user_id in ADMINS:
        return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status.value in ('administrator', 'creator')
    except Exception:
        return False


async def build_settings_buttons(chat_id):
    stg = await get_group_settings(chat_id)
    def toggle(val):
        return "✅" if val else "❌"

    btn = [
        [
            InlineKeyboardButton(
                f"🔗 Shortlink {toggle(stg.get('shortlink'))}",
                callback_data=f"stg_toggle_{chat_id}_shortlink"
            ),
            InlineKeyboardButton(
                f"🗑 Auto Delete {toggle(stg.get('auto_delete'))}",
                callback_data=f"stg_toggle_{chat_id}_auto_delete"
            )
        ],[
            InlineKeyboardButton(
                f"🎬 IMDB {toggle(stg.get('imdb', True))}",
                callback_data=f"stg_toggle_{chat_id}_imdb"
            ),
            InlineKeyboardButton(
                f"🔤 Spell Check {toggle(stg.get('spell_check', True))}",
                callback_data=f"stg_toggle_{chat_id}_spell_check"
            )
        ],[
            InlineKeyboardButton(
                f"🔒 Force Sub {toggle(stg.get('force_sub'))}",
                callback_data=f"stg_toggle_{chat_id}_force_sub"
            ),
            InlineKeyboardButton(
                f"👋 Welcome {toggle(stg.get('welcome'))}",
                callback_data=f"stg_toggle_{chat_id}_welcome"
            )
        ],[
            InlineKeyboardButton(
                "⚙️ Set Shortlink",
                callback_data=f"stg_set_{chat_id}_shortlink_config"
            )
        ],[
            InlineKeyboardButton(
                "📢 Set Force Sub Channel",
                callback_data=f"stg_set_{chat_id}_auth_channel"
            )
        ],[
            InlineKeyboardButton("❌ Close", callback_data="close")
        ]
    ]
    return btn


@Client.on_message(filters.command("settings"))
async def settings_cmd(client, message: Message):
    if message.chat.type.value == 'private':
        return await message.reply_text("Use this command in a group!")

    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text("⚠️ Only admins can change settings!")

    btn = await build_settings_buttons(message.chat.id)
    stg = await get_group_settings(message.chat.id)

    text = (
        f"⚙️ **Settings for {message.chat.title}**\n\n"
        f"🔗 Shortlink: {'✅ ON' if stg.get('shortlink') else '❌ OFF'}\n"
        f"🗑 Auto Delete: {'✅ ON' if stg.get('auto_delete') else '❌ OFF'} "
        f"({'Every ' + str(stg.get('delete_time', 300) // 60) + ' min' if stg.get('auto_delete') else 'Disabled'})\n"
        f"🎬 IMDB Info: {'✅ ON' if stg.get('imdb', True) else '❌ OFF'}\n"
        f"🔤 Spell Check: {'✅ ON' if stg.get('spell_check', True) else '❌ OFF'}\n"
        f"🔒 Force Subscribe: {'✅ ON' if stg.get('force_sub') else '❌ OFF'}\n"
        f"👋 Welcome Msg: {'✅ ON' if stg.get('welcome') else '❌ OFF'}\n"
    )
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(btn))


@Client.on_callback_query(filters.regex(r"^stg_toggle_"))
async def toggle_setting(client, query):
    parts   = query.data.split("_", 4)
    chat_id = int(parts[2])
    key     = parts[3] if len(parts) > 3 else parts[-1]

    if not await is_admin(client, chat_id, query.from_user.id):
        return await query.answer("Only admins can change settings!", show_alert=True)

    stg      = await get_group_settings(chat_id)
    defaults = {'imdb': True, 'spell_check': True}
    current  = stg.get(key, defaults.get(key, False))
    await update_group_setting(chat_id, key, not current)
    await query.answer(f"{'✅ Enabled' if not current else '❌ Disabled'} {key.replace('_', ' ').title()}")

    btn = await build_settings_buttons(chat_id)
    try:
        await query.message.edit_reply_markup(InlineKeyboardMarkup(btn))
    except Exception:
        pass


@Client.on_callback_query(filters.regex(r"^stg_set_"))
async def set_setting(client, query):
    parts   = query.data.split("_", 4)
    chat_id = int(parts[2])
    config  = "_".join(parts[3:])

    if not await is_admin(client, chat_id, query.from_user.id):
        return await query.answer("Only admins can change settings!", show_alert=True)

    if config == "shortlink_config":
        await query.message.edit_text(
            "🔗 **Set Shortlink**\n\n"
            "Send shortlink in this format:\n"
            "`/set_shortlink <url> <api_key>`\n\n"
            "Example:\n"
            "`/set_shortlink linkpays.in your_api_key`"
        )
    elif config == "auth_channel":
        await query.message.edit_text(
            "📢 **Set Force Subscribe Channel**\n\n"
            "Send channel ID:\n"
            "`/set_auth_channel -1001234567890`"
        )


@Client.on_message(filters.command("set_shortlink"))
async def set_shortlink(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text("Only admins can do this!")

    args = message.command[1:]
    if len(args) < 2:
        return await message.reply_text(
            "Usage: `/set_shortlink <url> <api_key>`\n"
            "Example: `/set_shortlink linkpays.in your_api_key`"
        )

    url, api = args[0], args[1]
    await update_group_setting(message.chat.id, 'shortlink_url', url)
    await update_group_setting(message.chat.id, 'shortlink_api', api)
    await update_group_setting(message.chat.id, 'shortlink', True)
    await message.reply_text(
        f"✅ Shortlink configured!\n"
        f"URL: `{url}`\n"
        f"Shortlink is now **ON**"
    )


@Client.on_message(filters.command("set_auth_channel"))
async def set_auth_channel(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text("Only admins can do this!")

    args = message.command[1:]
    if not args:
        return await message.reply_text("Usage: `/set_auth_channel -1001234567890`")

    try:
        channel_id = int(args[0])
        await update_group_setting(message.chat.id, 'auth_channel', channel_id)
        await update_group_setting(message.chat.id, 'force_sub', True)
        await message.reply_text(
            f"✅ Force Subscribe channel set to `{channel_id}`\n"
            f"Force Subscribe is now **ON**"
        )
    except ValueError:
        await message.reply_text("❌ Invalid channel ID!")


@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def broadcast(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a message to broadcast it!")

    from database.db import users_col
    status = await message.reply_text("📢 Broadcasting...")
    success = fail = 0
    async for user in users_col.find({}):
        try:
            await message.reply_to_message.copy(user['id'])
            success += 1
        except Exception:
            fail += 1

    await status.edit_text(
        f"✅ Broadcast complete!\n"
        f"Success: `{success}`\n"
        f"Failed: `{fail}`"
    )
