# 🎬 Auto Filter Bot

A clean Telegram Auto Filter Bot — no premium system, no third-party channel redirects.

## ✨ Features
- 🔍 Auto filter — users type movie name, bot shows file buttons
- 📁 Files sent directly to user's PM
- 🎬 IMDB poster + movie info
- 🔤 Spell check suggestions
- 🗑 Auto delete after configurable time
- 🔒 Force subscribe to channel
- 🔗 Shortlink support (admin can toggle per group)
- ⚙️ Per-group settings

## 🚀 Deploy on Render

1. Fork this repo
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your fork
4. Set **Build Command**: `pip install -r requirements.txt`
5. Set **Start Command**: `python3 bot.py`
6. Add environment variables (see below)
7. Deploy!

## 🔧 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `API_ID` | ✅ | From my.telegram.org |
| `API_HASH` | ✅ | From my.telegram.org |
| `BOT_TOKEN` | ✅ | From @BotFather |
| `DATABASE_URL` | ✅ | MongoDB connection string |
| `DATABASE_NAME` | ✅ | MongoDB database name |
| `LOG_CHANNEL` | ✅ | Channel ID for bot logs |
| `ADMINS` | ✅ | Your Telegram user ID |
| `INDEX_CHANNELS` | ✅ | Channel IDs to index (space separated) |
| `PORT` | ✅ | `8080` |
| `URL` | ✅ | Your render app URL |
| `PYTHON_VERSION` | ✅ | `3.10.8` |
| `AUTH_CHANNEL` | ❌ | Force subscribe channel ID |
| `SUPPORT_GROUP` | ❌ | Support group ID |
| `SUPPORT_LINK` | ❌ | Support group link |
| `UPDATES_LINK` | ❌ | Updates channel link |
| `SHORTLINK_URL` | ❌ | Shortlink domain e.g. `linkpays.in` |
| `SHORTLINK_API` | ❌ | Shortlink API key |
| `PICS` | ❌ | Space-separated image URLs for start message |
| `DELETE_TIME` | ❌ | Auto delete time in seconds (default: 300) |
| `MAX_BTN` | ❌ | Max file buttons to show (default: 10) |

## 📌 Admin Commands

| Command | Description |
|---|---|
| `/index` | Index files from your channel |
| `/delete_all` | Delete all indexed files |
| `/stats` | Bot statistics |
| `/settings` | Group settings |
| `/set_shortlink <url> <api>` | Set shortlink for group |
| `/set_auth_channel <id>` | Set force subscribe channel |
| `/broadcast` | Broadcast to all users |
| `/files` | Show total indexed files |

## ⚙️ Per-Group Settings (via /settings)

- 🔗 **Shortlink** — ON/OFF (when ON, users click shortlink to get file)
- 🗑 **Auto Delete** — ON/OFF (files auto-delete after DELETE_TIME)
- 🎬 **IMDB Info** — ON/OFF (show movie poster and info)
- 🔤 **Spell Check** — ON/OFF (suggest movies when no results)
- 🔒 **Force Subscribe** — ON/OFF (users must join channel)
- 👋 **Welcome Message** — ON/OFF
