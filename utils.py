import logging
import re
import aiohttp
from imdb import Cinemagoer

logger = logging.getLogger(__name__)
ia = Cinemagoer()


def get_size(size):
    """Convert bytes to human readable size."""
    units = ["Bytes", "KB", "MB", "GB", "TB"]
    size  = float(size)
    i     = 0
    while size >= 1024.0 and i < 4:
        i    += 1
        size /= 1024.0
    return f"{size:.2f} {units[i]}"


def clean_filename(name):
    """Remove @mentions and clean up filename."""
    # Remove @mentions (e.g. @channelname, @abc123)
    name = re.sub(r'@\w+', '', name)
    # Remove extra spaces left behind
    name = re.sub(r'\s{2,}', ' ', name)
    return name.strip()


async def get_shortlink(url, api, link):
    """Generate a shortened link using shortlink service."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'https://{url}/api',
                params={'api': api, 'url': link},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                data = await resp.json()
                if data.get('status') == 'success':
                    return data['shortenedUrl']
    except Exception as e:
        logger.warning(f"Shortlink error: {e}")
    return link


async def get_imdb_info(title):
    """Fetch IMDB info for a movie title."""
    try:
        results = ia.search_movie(title)
        if not results:
            return None
        movie  = ia.get_movie(results[0].movieID)
        poster = movie.get('full-size cover url') or movie.get('cover url', '')
        return {
            'title':     movie.get('title', title),
            'year':      movie.get('year', 'N/A'),
            'rating':    movie.get('rating', 'N/A'),
            'genres':    ', '.join(movie.get('genres', [])[:3]),
            'plot':      movie.get('plot outline', '') or (movie.get('plot', [''])[0] if movie.get('plot') else ''),
            'languages': ', '.join(movie.get('languages', [])[:3]),
            'poster':    poster,
            'url':       f"https://www.imdb.com/title/tt{results[0].movieID}/",
            'cast':      ', '.join([p['name'] for p in movie.get('cast', [])[:3]]),
        }
    except Exception as e:
        logger.warning(f"IMDB error: {e}")
        return None


async def get_spell_suggestions(title):
    """Get IMDB movie suggestions for spell check."""
    try:
        results = ia.search_movie(title)
        return results[:5] if results else []
    except Exception as e:
        logger.warning(f"Spell check error: {e}")
        return []


async def is_subscribed(client, user_id, channel_id):
    """Check if user is subscribed to a channel."""
    try:
        member = await client.get_chat_member(channel_id, user_id)
        return member.status.value not in ('left', 'banned', 'kicked')
    except Exception:
        return True
