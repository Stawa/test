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
    async def queueloop(self, ctx: commands.Context):
        if not ctx.guild.id in self.currently_playing:
            await self.call_event(
                event_type="on_music_error",
                ctx=ctx,
                error=e.PlayerEmpty("No song is currently being played."),
            )
            return

        if not ctx.guild.id in self.queue:
            await self.call_event(
                event_type="on_music_error",
                ctx=ctx,
                error=e.QueueEmpty(
                    "Unable to activate the queueloop because there are no items in the queue."
                ),
            )
            return

        current_playing = self.currently_playing.get(ctx.guild.id)
        current_playing.loop = (
            MusicEnums.QUEUE_LOOPS
            if current_playing.loop != MusicEnums.QUEUE_LOOPS
            else MusicEnums.NO_LOOPS
        )

        if current_playing.loop == MusicEnums.NO_LOOPS:
            self.combined_queue.pop(ctx.guild.id, None)

        return current_playing.loop