from discord.ext import commands
from typing import List
from math import ceil
import discord


class PageEmbed:
    def __init__(
        self,
        ctx: commands.Context,
        messages: List[str],
        buttons: List[str],
        fields: int = 10,
        timeout: int = 60,
    ):
        self.ctx = ctx
        self.messages = messages
        self.buttons = buttons
        self.fields = fields
        self.timeout = timeout

    def generate_embed(self):
        num_embeds = ceil(len(self.messages) / self.fields)
        embeds = []

        for num in range(num_embeds):
            embed = discord.Embed(title=f"Page {num+1}/{num_embeds}")
            fields = self._get_fields(num)
            for field in fields:
                embed.add_field(
                    name=str(field["index"] + 1),
                    value=field["value"],
                    inline=False,
                )
            embeds.append(embed)

        return embeds

    def _get_fields(self, num):
        start = num * self.fields
        end = start + self.fields
        fields = [
            {"index": index, "value": value}
            for index, value in enumerate(self.messages[start:end], start)
        ]
        return fields
