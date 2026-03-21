class script:
    START_TXT = """
👋 Hello {mention}!

I'm an **IM A MOVIE BOT** 🎬

𝐌𝐀𝐈𝐍 𝐂𝐇𝐀𝐍𝐍𝐄𝐋🔻
https://t.me/infinity_padangal

𝐀𝐒𝐊 𝐔𝐑 𝐌𝐎𝐕𝐈𝐄𝐒 𝐇𝐄𝐑𝐄🔻
https://t.me/+F8m_NK216hU3NzU1

any problem msg me @Infinity_vibe
"""

    HELP_TXT = """
📖 **Help** — {mention}

**How to use:**
• Type any movie name in the group
• I'll show matching files with sizes
• Click a file → it comes to your PM!

**User Commands:**
• /start — Start the bot
• /help — This message

**Admin Commands:**
• /index — Index movie channel
• /delete_all — Clear all files
• /stats — Bot statistics  
• /settings — Group settings
• /set_shortlink url api — Configure shortlink
• /set_auth_channel id — Set force sub channel
• /broadcast — Message all users
• /ban id — Ban a user
• /unban id — Unban a user
• /users — User stats
• /groups — Group stats
• /files — File count
• /leave id — Leave a group
"""

    NO_RESULTS_TXT = """
❌ No results found for **{query}**

💡 Tips:
• Check spelling
• Try shorter keywords  
• e.g. "RRR" instead of "RRR 2022 Tamil"
"""

    FILE_CAPTION = """📁 **{file_name}**
💾 **Size:** {file_size}

╭─── • ❰ KEEP SUPPORT ❱ • ────➤
𝐌𝐀𝐈𝐍 𝐂𝐇𝐀𝐍𝐍𝐄𝐋🔻
https://t.me/infinity_padangal
𝐀𝐒𝐊 𝐔𝐑 𝐌𝐎𝐕𝐈𝐄𝐒 𝐇𝐄𝐑𝐄🔻
https://t.me/+uqYYOOtw6L0xMDI1
𝐈𝐍𝐒𝐓𝐀 🔻
https://www.instagram.com/invites/contact/?i=yjti421dvitr&utm_content=gzimgf6
╰─────── • ◆ • ───────➤"""

    IMDB_TEMPLATE = """🎬 **{title}** ({year})
⭐ Rating: {rating}/10
🎭 Genre: {genres}
🌐 Language: {languages}
👥 Cast: {cast}

📖 {plot}

🔗 [IMDB]({url})"""
