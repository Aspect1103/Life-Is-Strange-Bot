# Builtin
from typing import List
import asyncio
# Pip
from discord.ext.commands import Context
from discord import Client
from discord import Embed


# Paginator class to switch between different embeds
class Paginator:
    # Initialise variables
    def __init__(self, ctx: Context, client: Client, timeout: float = 300):
        if isinstance(ctx, Context) and isinstance(client, Client):
            self.ctx = ctx
            self.client = client
        else:
            raise TypeError("Invalid parameters")
        self.pages = []
        self.reactions = ["⏪", "⬅️", "⏹️", "➡️", "⏩"]
        self.timeout = timeout
        self.message = None
        self.isRunning = True
        self.currentIndex = 0
        self.maxIndex = -1

    # Function to add pages to the class
    def addPages(self, pages: List[Embed]):
        if isinstance(pages, List) and all([isinstance(page, Embed) for page in pages]):
            if len(pages) > 0:
                self.pages = pages
                self.maxIndex = len(self.pages)-1
            else:
                raise RuntimeError("Can't paginate an empty list")
        else:
            raise TypeError("Invalid pages parameter")

    # Function to check a reaction
    def checker(self, reaction, user):
        return reaction.message.id == self.message.id and user.id != self.client.user.id and str(reaction) in self.reactions

    # Function to stop the paginator
    async def stop(self):
        self.isRunning = False
        await self.message.clear_reactions()

    # Function to control the paginator
    async def manager(self, reaction):
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
    async def start(self):
        self.message = await self.ctx.channel.send(embed=self.pages[0])
        for reaction in self.reactions:
            await self.message.add_reaction(reaction)
        while self.isRunning:
            try:
                reaction, user = await self.client.wait_for("reaction_add", timeout=self.timeout, check=self.checker)
                await self.message.remove_reaction(reaction, user)
                await self.manager(str(reaction))
            except asyncio.TimeoutError:
                await self.stop()
