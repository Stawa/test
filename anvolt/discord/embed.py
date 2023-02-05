from discord.ext import commands
from discord import ui, Interaction
from typing import List, Optional
from math import ceil
import asyncio
import discord


class PageEmbed:
    def __init__(
        self,
        ctx: commands.Context,
        messages: List[str],
        buttons: List[str],
        fields: Optional[int] = 10,
        timeout: int = 60,
    ):
        self.ctx = ctx
        self.messages = messages
        self.buttons = buttons
        self.fields = fields
        self.timeout = timeout
        self.index = 0
        self.message = None
        self.embeds = self._generate_embed()

    def _generate_embed(self):
        num_embeds = ceil(len(self.messages) / self.fields)
        embeds = []

        for num in range(num_embeds):
            embed = discord.Embed(title=f"Page {num+1}/{num_embeds}")
            for i in range(self.fields):
                try:
                    field_index = num * self.fields + i
                    embed.add_field(
                        name=str(field_index + 1),
                        value=self.messages[field_index],
                        inline=False,
                    )
                except IndexError:
                    break
            embeds.append(embed)

        return embeds
