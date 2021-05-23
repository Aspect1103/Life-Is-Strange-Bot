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
            self._ctx = ctx
            self._client = client
        else:
            raise TypeError("Invalid parameters")
        self._pages = []
        self._reactions = ["⏪", "⬅️", "⏹️", "➡️", "⏩"]
        self._timeout = timeout
        self._message = None
        self._isRunning = True
        self._currentIndex = 0
        self._maxIndex = -1

    # Function to add pages to the class
    def addPages(self, pages: List[Embed]):
        if isinstance(pages, List) and all([isinstance(page, Embed) for page in pages]):
            if len(pages) > 0:
                self._pages = pages
                self._maxIndex = len(self._pages)-1
            else:
                raise RuntimeError("Can't paginate an empty list")
        else:
            raise TypeError("Invalid pages parameter")

    # Function to check a reaction
    def _checker(self, reaction, user):
        return reaction.message.id == self._message.id and user.id != self._client.user.id and str(reaction) in self._reactions

    # Function to stop the paginator
    async def _stop(self):
        self._isRunning = False
        await self._message.clear_reactions()

    # Function to control the paginator
    async def _manager(self, reaction):
        if reaction == "⏪":
            if self._currentIndex != 0:
                await self._message.edit(embed=self._pages[0])
                self._currentIndex = 0
        elif reaction == "⬅️":
            if self._currentIndex != 0:
                await self._message.edit(embed=self._pages[self._currentIndex-1])
                self._currentIndex -= 1
        elif reaction == "⏹️":
            await self._stop()
        elif reaction == "➡️":
            if self._currentIndex != self._maxIndex:
                await self._message.edit(embed=self._pages[self._currentIndex+1])
                self._currentIndex += 1
        elif reaction == "⏩":
            if self._currentIndex != self._maxIndex:
                await self._message.edit(embed=self._pages[self._maxIndex])
                self._currentIndex = self._maxIndex

    # Function to start the paginator
    async def start(self):
        self._message = await self._ctx.channel.send(embed=self._pages[0])
        for reaction in self._reactions:
            await self._message.add_reaction(reaction)
        while self._isRunning:
            try:
                reaction, user = await self._client.wait_for("reaction_add", timeout=self._timeout, check=self._checker)
                await self._message.remove_reaction(reaction, user)
                await self._manager(str(reaction))
            except asyncio.TimeoutError:
                await self._stop()
