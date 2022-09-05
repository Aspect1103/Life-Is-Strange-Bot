# Builtin
from typing import Optional, List, Union
# Pip
from discord import Embed, Interaction, Message, ButtonStyle, ui
from discord.ext import bridge
# Custom
from Helpers.Utils import Utils


# Paginator class to switch between different embeds
class Paginator(ui.View):
    # Initialise variables
    def __init__(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext], bot: bridge.Bot, timeout: float = 300) -> None:
        super().__init__(timeout=timeout, disable_on_timeout=True)
        self.ctx = ctx
        self.bot = bot
        self.pages = []
        self.message = None
        self.currentIndex = 0
        self.maxIndex = -1

    @ui.button(emoji="⏪", style=ButtonStyle.primary)
    async def toStartButton(self, button: ui.Button, interaction: Interaction) -> None:
        if self.currentIndex != 0:
            await self.message.edit(embed=self.pages[0])
            self.currentIndex = 0
            await interaction.response.send_message('Displaying first page', ephemeral=True)
        else:
            await interaction.response.send_message('Already on first page', ephemeral=True)

    @ui.button(emoji="⬅️", style=ButtonStyle.primary)
    async def backButton(self, button: ui.Button, interaction: Interaction) -> None:
        if self.currentIndex != 0:
            await self.message.edit(embed=self.pages[self.currentIndex - 1])
            self.currentIndex -= 1
            await interaction.response.send_message('Displaying previous page', ephemeral=True)
        else:
            await interaction.response.send_message('Already on first page', ephemeral=True)

    @ui.button(emoji="⏹️", style=ButtonStyle.primary)
    async def stopButton(self, button: ui.Button, interaction: Interaction) -> None:
        self.stop()
        await interaction.response.send_message("Stopped buttons", ephemeral=True)

    @ui.button(emoji="➡️", style=ButtonStyle.primary)
    async def nextButton(self, button: ui.Button, interaction: Interaction) -> None:
        if self.currentIndex != self.maxIndex:
            await self.message.edit(embed=self.pages[self.currentIndex + 1])
            self.currentIndex += 1
            await interaction.response.send_message('Displaying next page', ephemeral=True)
        else:
            await interaction.response.send_message('Already on last page', ephemeral=True)

    @ui.button(emoji="⏩", style=ButtonStyle.primary)
    async def toEndButton(self, button: ui.Button, interaction: Interaction) -> None:
        if self.currentIndex != self.maxIndex:
            await self.message.edit(embed=self.pages[self.maxIndex])
            self.currentIndex = self.maxIndex
            await interaction.response.send_message('Displaying last page', ephemeral=True)
        else:
            await interaction.response.send_message('Already on last page', ephemeral=True)

    # Function to add pages to the class
    def addPages(self, pages: Optional[List[Embed]]) -> None:
        if isinstance(pages, List) and all([isinstance(page, Embed) for page in pages]):
            if len(pages) > 0:
                self.pages.extend(pages)
                self.maxIndex = len(self.pages)-1
            else:
                Utils.commandDebugEmbed(self.ctx, "Can't paginate an empty list")
        else:
            Utils.commandDebugEmbed(self.ctx, "Invalid pages parameter")

    # Function to start the paginator
    async def start(self) -> None:
        if len(self.pages) != 0:
            interaction: Interaction = await self.ctx.respond(embed=self.pages[0], view=self)
            self.message: Message = await interaction.original_message()
        else:
            await Utils.commandDebugEmbed(self.ctx, "No embeds to display")
