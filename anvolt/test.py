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

    async def now_playing(
        self, ctx: commands.Context, parse_duration: bool = True
    ) -> Optional[MusicProperty]:
        currently_playing = self.currently_playing.get(ctx.guild.id)

        if not currently_playing:
            return None

        start_time = currently_playing.start_time

        if ctx.voice_client.is_paused():
            start_time = (
                currently_playing.start_timestamp
                + time.time()
                - currently_playing.last_pause_timestamp
            )

        current_duration = time.time() - start_time

        if parse_duration:
            current_duration = self.parse_duration(duration=current_duration)

        currently_playing.current_duration = current_duration
        return currently_playing
