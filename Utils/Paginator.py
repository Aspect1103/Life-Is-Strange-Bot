# Builtin
from typing import List
import asyncio
# Pip
from discord.ext.commands import Context
from discord import Client
from discord import Embed


# Paginator class to switch between different embeds
class Paginator:
    def __init__(self, ctx: Context, client: Client, timeout: float = 300):
        if isinstance(ctx, Context) and isinstance(client, Client):
            self.__ctx = ctx
            self.__client = client
        else:
            raise TypeError("Invalid parameters")
        self.__pages = []
        self.__reactions = ["⏪", "⬅️", "⏹️", "➡️", "⏩"]
        self.__timeout = timeout
        self.__message = None
        self.__isRunning = True
        self.__currentIndex = 0
        self.__maxIndex = -1

    # Function to add pages to the class
    def addPages(self, pages: List[Embed]):
        if isinstance(pages, List) and all([isinstance(page, Embed) for page in pages]):
            if len(pages) > 0:
                self.__pages = pages
                self.__maxIndex = len(self.__pages)-1
            else:
                raise RuntimeError("Can't paginate an empty list")
        else:
            raise TypeError("Invalid pages parameter")

    # Function to check a reaction
    def __checker(self, reaction, user):
        return reaction.message.id == self.__message.id and user.id != self.__client.user.id and str(reaction) in self.__reactions

    # Function to stop the paginator
    async def __stop(self):
        self.__isRunning = False
        await self.__message.clear_reactions()

    # Function to control the paginator
    async def __manager(self, reaction):
        if reaction == "⏪":
            if self.__currentIndex != 0:
                await self.__message.edit(embed=self.__pages[0])
                self.__currentIndex = 0
        elif reaction == "⬅️":
            if self.__currentIndex != 0:
                await self.__message.edit(embed=self.__pages[self.__currentIndex-1])
                self.__currentIndex -= 1
        elif reaction == "⏹️":
            await self.__stop()
        elif reaction == "➡️":
            if self.__currentIndex != self.__maxIndex:
                await self.__message.edit(embed=self.__pages[self.__currentIndex+1])
                self.__currentIndex += 1
        elif reaction == "⏩":
            if self.__currentIndex != self.__maxIndex:
                await self.__message.edit(embed=self.__pages[self.__maxIndex])
                self.__currentIndex = self.__maxIndex

    # Function to start the paginator
    async def start(self):
        self.__message = await self.__ctx.channel.send(embed=self.__pages[0])
        for reaction in self.__reactions:
            await self.__message.add_reaction(reaction)
        while self.__isRunning:
            try:
                reaction, user = await self.__client.wait_for("reaction_add", timeout=self.__timeout, check=self.__checker)
                await self.__message.remove_reaction(reaction, user)
                await self.__manager(str(reaction))
            except asyncio.TimeoutError:
                await self.__stop()
