import pprint
from typing import Dict
from anvolt.models import MusicPlatform, errors
from youtube_search import YoutubeSearch
import aiohttp
import re
import youtube_dl
import asyncio

e = errors
FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-loglevel panic -hide_banner -nostats -nostdin -vn -b:a 192k -ac 2",
}
YDL_OPTIONS = {
    "format": "bestaudio/best",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
}


class AudioStreamFetcher:
    def __init__(self) -> None:
        pass

    def _check_url(self, query: str) -> MusicPlatform:
        youtube_extractor = youtube_dl.extractor.get_info_extractor("Youtube")
        soundcloud_pattern = re.compile("^https://soundcloud.com/")

        if youtube_extractor.suitable(query):
            return MusicPlatform.YOUTUBE_URL

        if re.match(soundcloud_pattern, query):
            return MusicPlatform.SOUNDCLOUD

        return MusicPlatform.YOUTUBE_QUERY

    async def _retreive_soundcloud_url(self, query: str, client_id: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api-widget.soundcloud.com/resolve?url={query}&format=json&client_id={client_id}",
            ) as response:
                return await response.json()

    async def _extract_soundcloud_info(self, query: str, client_id: str) -> Dict:
        url = await self._retreive_soundcloud_url(query, client_id)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{url.get('media')['transcodings'][0]['url']}?client_id={client_id}"
            ) as response:
                return await response.json(), url

    async def _extract_youtube_info(self, query: str) -> Dict:
        if not query.startswith("https"):
            search = YoutubeSearch(search_terms=query, max_results=5).to_dict()
            query = "https://www.youtube.com/watch?v={}".format(search[0]["id"])

        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            sound_info = ydl.extract_info(query, download=False)
            return sound_info

    async def retrieve_audio(
        self, source: MusicPlatform = None, query: str = None, **kwargs
    ) -> Dict:
        task = None

        if source == MusicPlatform.YOUTUBE_URL:
            task = asyncio.ensure_future(self._extract_youtube_info(query))

        if source == MusicPlatform.SOUNDCLOUD:
            task = asyncio.ensure_future(
                self._extract_soundcloud_info(query, client_id=kwargs.get("client_id"))
            )

        await asyncio.wait([task])
        return task.result()
