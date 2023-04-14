from __future__ import annotations

# Builtin
from typing import Union

# Pip
from discord import Embed, Interaction, Message, ButtonStyle, ui
from discord.ext import bridge

# Custom
from lis_bot.helpers.utils import utils


# Paginator class to switch between different embeds
class Paginator(ui.View):
    # Initialise variables
    def __init__(
        self,
        ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext],
        bot: bridge.Bot,
        timeout: float = 300,
    ) -> None:
        super().__init__(timeout=timeout, disable_on_timeout=True)
        self.ctx = ctx
        self.bot = bot
        self.pages = []
        self.message = None
        self.currentIndex = 0
        self.maxIndex = -1

    @ui.button(emoji="â�ª", style=ButtonStyle.primary)
    async def toStartButton(self, interaction: Interaction) -> None:
        if self.currentIndex != 0:
            await self.message.edit(embed=self.pages[0])
            self.currentIndex = 0
            await interaction.response.send_message(
                "Displaying first page", ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "Already on first page", ephemeral=True,
            )

    @ui.button(emoji="â¬…ï¸�", style=ButtonStyle.primary)
    async def backButton(self, interaction: Interaction) -> None:
        if self.currentIndex != 0:
            await self.message.edit(embed=self.pages[self.currentIndex - 1])
            self.currentIndex -= 1
            await interaction.response.send_message(
                "Displaying previous page", ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "Already on first page", ephemeral=True,
            )

    @ui.button(emoji="â�¹ï¸�", style=ButtonStyle.primary)
    async def stopButton(self, interaction: Interaction) -> None:
        self.stop()
        await interaction.response.send_message("Stopped buttons", ephemeral=True)

    @ui.button(emoji="âž¡ï¸�", style=ButtonStyle.primary)
    async def nextButton(self, interaction: Interaction) -> None:
        if self.currentIndex != self.maxIndex:
            await self.message.edit(embed=self.pages[self.currentIndex + 1])
            self.currentIndex += 1
            await interaction.response.send_message(
                "Displaying next page", ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "Already on last page", ephemeral=True,
            )

    @ui.button(emoji="â�©", style=ButtonStyle.primary)
    async def toEndButton(self, interaction: Interaction) -> None:
        if self.currentIndex != self.maxIndex:
            await self.message.edit(embed=self.pages[self.maxIndex])
            self.currentIndex = self.maxIndex
            await interaction.response.send_message(
                "Displaying last page", ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "Already on last page", ephemeral=True,
            )

    # Function to add pages to the class
    def addPages(self, pages: Union[list[Embed], None]) -> None:
        if isinstance(pages, list) and all(isinstance(page, Embed) for page in pages):
            if len(pages) > 0:
                self.pages.extend(pages)
                self.maxIndex = len(self.pages) - 1
            else:
                utils.commandDebugEmbed(self.ctx, "Can't paginate an empty list")
        else:
            utils.commandDebugEmbed(self.ctx, "Invalid pages parameter")

    # Function to start the paginator
    async def start(self) -> None:
        if len(self.pages) != 0:
            interaction: Interaction = await self.ctx.respond(
                embed=self.pages[0], view=self,
            )
            self.message: Message = await interaction.original_message()
        else:
            await utils.commandDebugEmbed(self.ctx, "No embeds to display")
