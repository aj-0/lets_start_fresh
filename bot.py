import logging
import asyncio
from aiohttp import web

# ── Event loop fix (required for Render/Docker) ────────────────────────────────
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

_orig_get_event_loop = asyncio.get_event_loop
def _safe_get_event_loop():
    try:
        return _orig_get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop
asyncio.get_event_loop = _safe_get_event_loop
# ──────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logging.getLogger('hydrogram').setLevel(logging.WARNING)
logging.getLogger('motor').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

from hydrogram import Client
from info import API_ID, API_HASH, BOT_TOKEN, PORT, LOG_CHANNEL
from database import ensure_indexes
from web import web_server


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="AutoFilterBot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=10,
        )

    async def start(self):
        await super().start()

        # Ensure DB indexes
        ensure_indexes()

        me = await self.get_me()
        logger.info(f"✅ Bot started: @{me.username}")

        # Start web server for keep-alive
        app    = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", PORT).start()
        logger.info(f"🌐 Web server running on port {PORT}")

        # Log channel message
        try:
            await self.send_message(
                LOG_CHANNEL,
                f"✅ **{me.first_name}** started!\n\n"
                f"👤 Username: @{me.username}\n"
                f"🆔 ID: `{me.id}`"
            )
        except Exception as e:
            logger.warning(f"Could not send to LOG_CHANNEL: {e}")

    async def stop(self, *args):
        await super().stop()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    Bot().run()
