from anvolt.models import MusicPropertiesEnums, MusicProperty
from datetime import datetime
from typing import List, Union, Optional
from math import ceil
import discord

DEFAULT_BUTTONS = ["⏪", "◀️", "▶️", "⏩"]
TITLE = "top"
FOOTER = "footer"


class PageEmbed:
    def __init__(
        self,
        messages: List[MusicProperty],
        buttons: List[str] = DEFAULT_BUTTONS,
        fields: int = 10,
        timeout: int = 60,
    ):
        self.messages = messages
        self.buttons = buttons
        self.fields = fields
        self.timeout = timeout

    def generate_embed(
        self,
        page_on: Union[TITLE, FOOTER] = FOOTER,
        value_fields: str = None,
        assets_format: List[MusicPropertiesEnums] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        footer: Optional[str] = None,
        color: Optional[str] = None,
        timestamp: datetime = datetime.utcnow(),
    ) -> List[discord.Embed]:
        num_embeds = ceil(len(self.messages) / self.fields)
        enum_names = [asset.name.lower() for asset in assets_format]
        embeds = []

        for num in range(num_embeds):
            embed_title = (
                title if page_on != TITLE else f"Page {num+1}/{num_embeds} {title}"
            )
            embed_footer = footer if page_on != FOOTER else f"Page {num+1}/{num_embeds}"

            fields = self._get_fields(num)
            embed = discord.Embed(
                title=embed_title,
                description=description,
                color=color,
                timestamp=timestamp,
            ).set_footer(text=embed_footer)

            for field in fields:
                values = [
                    getattr(field["value"], enum_name) for enum_name in enum_names
                ]
                embed.add_field(
                    name=str(field["index"] + 1),
                    value=value_fields.format(*values),
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
