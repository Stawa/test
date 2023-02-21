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

    async def get_queue(self, ctx: commands.Context) -> Optional[MusicProperty]:
        currently_playing = self.currently_playing.get(ctx.guild.id)

        if currently_playing.loop == MusicEnums.QUEUE_LOOPS:
            if ctx.guild.id in self.combined_queue:
                return self.combined_queue[ctx.guild.id][self.num :]
            return self.queue[ctx.guild.id].queue[self.num :]

        if self.queue.get(ctx.guild.id):
            return self.queue[ctx.guild.id].queue