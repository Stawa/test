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

    async def _play_next(self, ctx: commands.Context) -> None:
        queue = self.queue.get(ctx.guild.id)
        current_playing = self.currently_playing.get(ctx.guild.id)

        if not queue or not queue.queue:
            self.currently_playing.pop(ctx.guild.id, None)
            self.queue.pop(ctx.guild.id, None)

            await self.call_event(event_type="on_music_end", ctx=ctx)
            return

        if current_playing.loop == MusicEnums.QUEUE_LOOPS:
            if ctx.guild.id not in self.combined_queue:
                self.combined_queue[ctx.guild.id] = [current_playing] + queue.queue

            next_track = self.combined_queue[ctx.guild.id][self.num]
            self.task_loop(
                self.bot.loop,
                self.play(
                    ctx,
                    query=next_track,
                    volume=current_playing.volume or self.default_volume,
                    loop=MusicEnums.QUEUE_LOOPS,
                ),
            )

            self.num = (self.num + 1) % len(self.combined_queue[ctx.guild.id])
            return

        if current_playing.loop == MusicEnums.LOOPS:
            self.task_loop(
                self.bot.loop,
                self.play(
                    ctx,
                    query=current_playing,
                    volume=current_playing.volume or self.default_volume,
                    loop=MusicEnums.LOOPS,
                ),
            )
            return

        next_song = queue.queue.pop(0)
        self.task_loop(
            self.bot.loop,
            self.play(
                ctx,
                query=next_song,
                volume=current_playing.volume or self.default_volume,
                loop=MusicEnums.NO_LOOPS,
            ),
        )
