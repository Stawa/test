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
        title: Optional[str] = "",
        description: Optional[str] = "",
        footer: Optional[str] = "",
        color: discord.Color = discord.Color.from_rgb(170, 255, 0),
        timestamp: datetime = datetime.utcnow(),
    ) -> List[discord.Embed]:
        """
        Generate a list of discord.Embed objects to display paginated data.

        :param page_on: A value from the PageType enum indicating whether the page numbers should be in the title or footer.
        :param value_fields: A string format template for the values to be displayed in each field.
        :param assets_format: A list of enums indicating which properties to display for each value.
        :param title: The title of the embed.
        :param description: The description of the embed.
        :param footer: The footer text of the embed.
        :param color: The color of the embed.
        :param timestamp: The timestamp of the embed.
        :return: A list of discord.Embed objects.
        """

        num_embeds = ceil(len(self.messages) / self.fields)
        enum_names = (
            [asset.name.lower() for asset in assets_format] if assets_format else []
        )
        embeds = []

        for num in range(num_embeds):
            page = f"Page {num+1}/{num_embeds}"

            page += title if page_on == TITLE else ""
            page += footer if page_on == FOOTER else ""

            fields = self._get_fields(num)
            embed = discord.Embed(
                title=title if not page_on == TITLE else page,
                description=description,
                color=color,
                timestamp=timestamp,
            ).set_footer(text=footer if not page_on == FOOTER else page)

            for field in fields:
                values = [
                    getattr(field["value"], enum_name) for enum_name in enum_names
                ]
                embed.add_field(
                    name=str(field["index"] + 1),
                    value=value_fields.format(*values) if value_fields else None,
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
