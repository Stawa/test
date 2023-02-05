from .audio import AudioStreamFetcher, FFMPEG_OPTIONS
from anvolt.models import MusicProperty, MusicEnums, MusicPlatform, errors
from anvolt.discord import Event
from discord.ext import commands
from typing import Tuple, Union, Optional, Callable, Dict
from youtube_search import YoutubeSearch
import asyncio
import discord
import time

VocalGuildChannel = Union[discord.VoiceChannel, discord.StageChannel]
e = errors


class AnVoltMusic(Event):
    def __init__(self, bot: commands.Bot, **kwargs):
        super().__init__()
        self.audio = AudioStreamFetcher()
        self.bot = bot
        self.default_volume = kwargs.get("default_volume", 15)
        self.inactivity_timeout = kwargs.get("inactivity_timeout", 60)
        self.client_id = kwargs.get("client_id", None)

        self.num = 0
        self.queue: Dict[MusicProperty] = {}
        self.history: Dict[MusicProperty] = {}
        self.currently_playing: Dict[MusicProperty] = {}

    async def _check_inactivity(self, ctx: commands.Context):
        while True:
            await asyncio.sleep(10)

            if ctx.voice_client:
                members = list(
                    filter(lambda x: not x.bot, ctx.voice_client.channel.members)
                )

                if len(members) == 0:
                    await asyncio.sleep(self.inactivity_timeout)
                    await ctx.voice_client.disconnect(force=True)

    async def _check_connection(self, ctx: commands.Context):
        if not ctx.voice_client:
            await self.call_event(
                event_type="on_music_error",
                ctx=ctx,
                error=e.NotConnected("Client isn't connected to a voice channel."),
            )
            return False

        if not ctx.author.voice:
            await self.call_event(
                event_type="on_music_error",
                ctx=ctx,
                error=e.NotConnected("User isn't connected to a voice channel."),
            )
            return False

        return True

    def ensure_connection(func: Callable):
        async def wrapper(self, ctx, *args, **kwargs):
            if await self._check_connection(ctx):
                return await func(self, ctx, *args, **kwargs)

        return wrapper

    def add_queue(self, ctx: commands.Context, player: MusicProperty) -> None:
        self.queue.setdefault(ctx.guild.id, MusicProperty()).queue.append(player)

    def remove_queue(self, ctx: commands.Context, num: int) -> None:
        if self.queue.get(ctx.guild.id):
            self.queue[ctx.guild.id].queue.pop(num)

    def add_history(self, ctx: commands.Context, player: MusicProperty):
        self.history.setdefault(ctx.guild.id, MusicProperty()).history.append(player)

    def parse_duration(self, duration: Union[str, float]) -> str:
        if duration == "LIVE":
            return "LIVE"

        duration = time.strftime("%H:%M:%S", time.gmtime(duration))
        return duration[3:] if duration.startswith("00") else duration

    async def get_queue(self, ctx: commands.Context) -> Optional[MusicProperty]:
        if self.queue.get(ctx.guild.id):
            return self.queue[ctx.guild.id]

    async def get_history(self, ctx: commands.Context) -> Optional[MusicProperty]:
        if self.history.get(ctx.guild.id):
            return self.history[ctx.guild.id]

    async def _play_next(self, ctx: commands.Context) -> None:
        if self.currently_playing[ctx.guild.id].loop == MusicEnums.LOOPS:
            await self.play(
                ctx,
                f"https://www.youtube.com/watch?v={self.currently_playing[ctx.guild.id].video_id}",
            )
            return

        if self.queue.get(ctx.guild.id) or self.queue.get(ctx.guild.id).queue:
            if not self.queue[ctx.guild.id].queue:
                if self.currently_playing.get(ctx.guild.id):
                    del self.currently_playing[ctx.guild.id]

                await self.call_event(
                    event_type="on_music_end",
                    ctx=ctx,
                )
                return

        if self.queue.get(ctx.guild.id):
            if len(self.queue[ctx.guild.id].queue) > 0:
                next_song = self.queue[ctx.guild.id].queue.pop(0)
                await self.play(ctx, query=next_song.video_url)

    async def now_playing(
        self, ctx: commands.Context, parse_duration: bool = True
    ) -> Optional[MusicProperty]:
        if self.currently_playing.get(ctx.guild.id):
            player = self.currently_playing[ctx.guild.id]
            current_duration = time.time() - player.start_time
            player.current_duration = (
                self.parse_duration(duration=current_duration)
                if parse_duration
                else current_duration
            )
            return player

    async def join(
        self, ctx: commands.Context
    ) -> Optional[Tuple[VocalGuildChannel, discord.VoiceClient]]:
        if not ctx.author.voice:
            await self.call_event(
                event_type="on_music_error",
                ctx=ctx,
                error=e.NotConnected("User isn't connected to a voice channel."),
            )
            return

        channel = ctx.author.voice.channel
        voice_client = await channel.connect(cls=discord.VoiceClient)
        self.bot.loop.create_task(self._check_inactivity(ctx))
        return channel, voice_client

    @ensure_connection
    async def disconnect(self, ctx: commands.Context) -> Optional[VocalGuildChannel]:
        channel = ctx.voice_client.channel
        await ctx.voice_client.disconnect(force=True)
        return channel

    @ensure_connection
    async def volume(self, ctx: commands.Context, volume: int = None) -> Optional[int]:
        if not volume:
            return round(ctx.voice_client.source.volume * 100)

        if not (0 <= volume <= 100):
            await self.call_event(
                event_type="on_music_error",
                ctx=ctx,
                error=e.InvalidNumber("Invalid volume, it must be between 0 and 100."),
            )
            return

        ctx.voice_client.source.volume = volume / 100

        if self.queue.get(ctx.guild.id):
            self.queue[ctx.guild.id].volume = volume

        if not self.queue.get(ctx.guild.id):
            self.currently_playing[ctx.guild.id].volume = volume

        return round(ctx.voice_client.source.volume * 100)

    @ensure_connection
    async def pause(self, ctx: commands.Context) -> Optional[bool]:
        if ctx.voice_client.is_paused():
            await self.call_event(
                event_type="on_music_error",
                ctx=ctx,
                error=e.PlayerAlreadyPaused("The music player is already paused."),
            )
            return

        ctx.voice_client.pause()
        return True

    @ensure_connection
    async def resume(self, ctx: commands.Context) -> Optional[bool]:
        if not ctx.voice_client.is_paused():
            await self.call_event(
                event_type="on_music_error",
                ctx=ctx,
                error=e.PlayerNotPaused("The music player isn't paused."),
            )
            return

        ctx.voice_client.resume()
        return True

    @ensure_connection
    async def skip(self, ctx: commands.Context) -> Optional[bool]:
        if not ctx.voice_client.is_playing():
            await self.call_event(
                event_type="on_music_error",
                ctx=ctx,
                error=e.PlayerEmpty("No song is currently being played."),
            )
            return

        if ctx.voice_client:
            ctx.voice_client.stop()

        return True

    @ensure_connection
    async def loop(self, ctx: commands.Context):
        if not ctx.guild.id in self.currently_playing:
            await self.call_event(
                event_type="on_music_error",
                ctx=ctx,
                error=e.PlayerEmpty("No song is currently being played."),
            )
            return

        self.currently_playing[ctx.guild.id].loop = (
            MusicEnums.LOOPS
            if self.currently_playing[ctx.guild.id].loop != MusicEnums.LOOPS
            else MusicEnums.NO_LOOPS
        )

        return self.currently_playing[ctx.guild.id].loop

    @ensure_connection
    async def play(self, ctx: commands.Context, query: str) -> Optional[MusicProperty]:
        voice = ctx.voice_client
        volume = self.default_volume
        loop = MusicEnums.NO_LOOPS

        platform, sound_info = self.audio.get_audio_info(query, self.client_id)
        if not sound_info:
            return None

        player = MusicProperty(
            audio_url=sound_info.get("url"),
            video_id=sound_info.get("id"),
            video_url=sound_info.get(
                "permalink_url"
                if platform == MusicPlatform.SOUNDCLOUD
                else "https://www.youtube.com/watch?v={}".format(sound_info.get("id"))
            ),
            title=sound_info.get("title"),
            duration=round(sound_info.get("duration") / 1000)
            if platform == MusicPlatform.SOUNDCLOUD
            else ("LIVE" if sound_info.get("is_live") else sound_info.get("duration")),
            thumbnails=sound_info.get(
                "artwork_url" if platform == MusicPlatform.SOUNDCLOUD else "thumbnails"
            ),
            is_live=sound_info.get("is_live")
            if platform == MusicPlatform.YOUTUBE
            else False,
            requester=ctx.author,
        )

        if voice.is_playing():
            self.add_queue(ctx=ctx, player=player)
            return player

        source = discord.FFmpegPCMAudio(player.audio_url, options=FFMPEG_OPTIONS)
        if self.currently_playing.get(ctx.guild.id):
            volume = self.currently_playing[ctx.guild.id].volume
            loop = self.currently_playing[ctx.guild.id].loop

        voice.play(
            source, after=lambda e: self.task_loop(self.bot.loop, self._play_next(ctx))
        )
        voice.source = discord.PCMVolumeTransformer(
            original=source, volume=volume / 100
        )

        player.start_time = time.time()
        player.volume = volume
        player.loop = loop
        self.currently_playing[ctx.guild.id] = player
        self.add_history(ctx, player)

        await self.call_event(event_type="on_music_start", ctx=ctx, player=player)
