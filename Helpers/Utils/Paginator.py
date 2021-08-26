# Builtin
import asyncio
from typing import Optional, List
# Pip
from discord import Embed, Reaction, User
from discord.ext.commands import Context, Bot
# Custom
from Helpers.Utils import Utils


# Paginator class to switch between different embeds
class Paginator:
    # Initialise variables
    def __init__(self, ctx: Context, client: Bot, timeout: float = 300) -> None:
        self.ctx = ctx
        self.client = client
        self.pages = []
        self.reactions = ["⏪", "⬅️", "⏹️", "➡️", "⏩"]
        self.timeout = timeout
        self.message = None
        self.isRunning = True
        self.currentIndex = 0
        self.maxIndex = -1

    # Function to add pages to the class
    def addPages(self, pages: Optional[List[Embed]]) -> None:
        if isinstance(pages, List) and all([isinstance(page, Embed) for page in pages]):
            if len(pages) > 0:
                self.pages.extend(pages)
                self.maxIndex = len(self.pages)-1
            else:
                Utils.commandDebugEmbed(self.ctx.channel, "Can't paginate an empty list")
        else:
            Utils.commandDebugEmbed(self.ctx.channel, "Invalid pages parameter")

    # Function to check a reaction
    def checker(self, reaction: Reaction, user: User) -> bool:
        return reaction.message.id == self.message.id and user.id != self.client.user.id and str(reaction) in self.reactions

    # Function to stop the paginator
    async def stop(self) -> None:
        self.isRunning = False
        await self.message.clear_reactions()

    # Function to control the paginator
    async def manager(self, reaction: str) -> None:
        if reaction == "⏪":
            if self.currentIndex != 0:
                await self.message.edit(embed=self.pages[0])
                self.currentIndex = 0
        elif reaction == "⬅️":
            if self.currentIndex != 0:
                await self.message.edit(embed=self.pages[self.currentIndex-1])
                self.currentIndex -= 1
        elif reaction == "⏹️":
            await self.stop()
        elif reaction == "➡️":
            if self.currentIndex != self.maxIndex:
                await self.message.edit(embed=self.pages[self.currentIndex+1])
                self.currentIndex += 1
        elif reaction == "⏩":
            if self.currentIndex != self.maxIndex:
                await self.message.edit(embed=self.pages[self.maxIndex])
                self.currentIndex = self.maxIndex

    # Function to start the paginator
    async def start(self) -> None:
        if len(self.pages) != 0:
            self.message = await self.ctx.channel.send(embed=self.pages[0])
            for reaction in self.reactions:
                await self.message.add_reaction(reaction)
            while self.isRunning:
                try:
                    reaction, user = await self.client.wait_for("reaction_add", timeout=self.timeout,
                                                                check=self.checker)
                    await self.message.remove_reaction(reaction, user)
                    await self.manager(str(reaction))
                except asyncio.TimeoutError:
                    await self.stop()
        else:
            await Utils.commandDebugEmbed(self.ctx.channel, "No embeds to display")
