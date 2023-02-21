class AnVoltMusic(Event, AudioStreamFetcher):
    def __init__(self, bot: commands.Bot, **kwargs):
        super().__init__()
        self.bot = bot
        self.default_volume = kwargs.get("default_volume", 15)
        self.inactivity_timeout = kwargs.get("inactivity_timeout", 60)
        self.client_id = kwargs.get("client_id", None)

        self.num = 0
        self.queue: Dict[QueueSession] = {}
        self.history: Dict[QueueSession] = {}
        self.currently_playing: Dict[Any] = {}
        self.combined_queue: Dict[Any] = {}

        self._check_opus()

    @ensure_connection
    async def play(
        self, ctx: commands.Context, query: Union[str, MusicProperty], **kwargs
    ) -> Optional[MusicProperty]:
        voice = ctx.voice_client
        volume = kwargs.get("volume", self.default_volume)
        loop = kwargs.get("loop", MusicEnums.NO_LOOPS)
        player = query if isinstance(query, MusicProperty) else None

        if not isinstance(query, MusicProperty):
            platform = self._check_url(query)

            if platform in YoutubeUri:
                sound_info = await self.retrieve_audio(
                    platform, query, client_id=self.client_id
                )

            if platform == MusicPlatform.SOUNDCLOUD:
                audio, sound_info = await self.retrieve_audio(
                    platform, query, client_id=self.client_id
                )

            if not sound_info:
                return None

            player = MusicProperty(
                audio_url=sound_info.get("url")
                if platform in YoutubeUri
                else audio.get("url"),
                video_id=sound_info.get("id"),
                video_url=sound_info.get("permalink_url")
                if platform == MusicPlatform.SOUNDCLOUD
                else f"https://www.youtube.com/watch?v={sound_info.get('id')}",
                title=sound_info.get("title"),
                duration=round(sound_info.get("duration") / 1000)
                if platform == MusicPlatform.SOUNDCLOUD
                else (
                    "LIVE" if sound_info.get("is_live") else sound_info.get("duration")
                ),
                thumbnails=sound_info.get(
                    "artwork_url"
                    if platform == MusicPlatform.SOUNDCLOUD
                    else "thumbnails"
                ),
                is_live=sound_info.get("is_live") if platform in YoutubeUri else False,
                requester=ctx.author,
            )

        if voice.is_playing():
            self.add_queue(ctx=ctx, player=player)
            return player

        source = discord.FFmpegPCMAudio(player.audio_url, options=FFMPEG_OPTIONS)
        voice.play(
            source,
            after=lambda e: self.task_loop(self.bot.loop, self._play_next(ctx)),
        )
        voice.source = discord.PCMVolumeTransformer(
            original=source, volume=volume / 100
        )

        player.start_time = time.time()
        player.loop = loop
        player.volume = volume
        self.currently_playing[ctx.guild.id] = player

        if loop == MusicEnums.NO_LOOPS:
            self.add_history(ctx, player)

        await self.call_event(event_type="on_music_start", ctx=ctx, player=player)
