class script:

    START_TXT = """
👋 Hello {mention}!

I'm an **Auto Filter Bot** 🎬

Add me to your group and I'll help users find movies instantly!

🔍 Users just type any movie name — I'll show file buttons with sizes.
📥 Click a button → file arrives in their PM!

📌 **Quick Setup:**
1. Add me to your group as admin
2. Use /index to index your movie channel  
3. Done! Users can start searching 🚀
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

    FILE_CAPTION = "📁 **{file_name}**\n💾 Size: {file_size}"

    IMDB_TEMPLATE = """🎬 **{title}** ({year})
⭐ Rating: {rating}/10
🎭 Genre: {genres}
🌐 Language: {languages}
👥 Cast: {cast}

📖 {plot}

🔗 [IMDB]({url})"""
