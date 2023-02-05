import discord
from anvolt.discord import AnVoltMusic, PageEmbed
from anvolt.notifier import NotifierClient
from discord.ext import commands

intents = discord.Intents().all()
bot = commands.Bot(command_prefix="!", intents=intents)
client = AnVoltMusic(bot=bot, client_id="lbr2j5jeg042EeeZZqDQTE8GQ9ekdQnA")
NotifierClient = NotifierClient(
    client_id="hyb2b6zxwo3731lkmqgp9i07ke81rs",
    client_secret="iuqjj3wb7zqlbt8npmuspbkco6wynr",
)


@client.event
async def on_music_start(ctx: commands.Context, player):
    print("Music Started", player.title, player.duration)
    await ctx.send(f"Music played: {player.title}")


@client.event
async def on_music_end(ctx: commands.Context):
    await ctx.send(f"All queue on {ctx.guild.name} is done")


@client.event
async def on_music_error(ctx: commands.Context, error):
    print("error", ctx, error)


@bot.event
async def on_ready():
    print(f"{bot.user.name} Is ready.")


@bot.command()
async def play(ctx: commands.Context, *, url):
    if not ctx.voice_client:
        await client.join(ctx)

    music = await client.play(ctx, query=url)

    if music:
        await ctx.send(music.title)


@bot.command()
async def join(ctx: commands.Context):
    await client.join(ctx)


@bot.command()
async def leave(ctx: commands.Context):
    await client.disconnect(ctx)


@bot.command()
async def volume(ctx: commands.Context, volume: int = None):
    await ctx.send(await client.volume(ctx, volume))


@bot.command()
async def pause(ctx: commands.Context):
    await ctx.send(await client.pause(ctx))


@bot.command()
async def resume(ctx: commands.Context):
    await ctx.send(await client.resume(ctx))


@bot.command()
async def skip(ctx: commands.Context):
    await ctx.send(await client.skip(ctx))


@bot.command()
async def loop(ctx: commands.Context):
    await ctx.send(await client.loop(ctx))


@bot.command()
async def queueloop(ctx: commands.Context):
    await ctx.send(await client.queueloop(ctx))


@bot.command()
async def queue(ctx: commands.Context):
    if get_queue := await client.get_queue(ctx):
        await ctx.send(get_queue.queue)


@bot.command()
async def history(ctx: commands.Context):
    if get_history := await client.get_history(ctx):
        await ctx.send(get_history)


@bot.command()
async def now_play(ctx: commands.Context):
    if now_playing := await client.now_playing(ctx):
        await ctx.send(
            f"Title: {now_playing.title}\nDuration: {now_playing.current_duration}/{client.parse_duration(now_playing.duration)}"
        )


bot.run("ODYxNTAxMDUzNDcyMjEwOTY1.G7Pddm.EHM3d3SHEtAAA6yIWMWhq4T8JnW-hca1Tj38Zk")
