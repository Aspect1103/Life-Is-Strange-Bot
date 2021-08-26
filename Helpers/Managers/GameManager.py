# Builtin
import asyncio
# Pip
from discord.ext.commands import Bot, Context
from discord import Colour, Embed, Reaction, User
# Custom
from Helpers.Games.TicTacToe import TicTacToe
from Helpers.Games.Connect4 import Connect4
from Helpers.Games.Hangman import Hangman
from Helpers.Games.Anagram import Anagram
from Helpers.Utils import Utils


# GameManager class to streamline executing games
class GameManager:
    """
    Game Modes:
        1 - TicTacToe (multiplayer)
        2 - Connect4 (multiplayer)
        3 - Hangman (singleplayer)
        4 - Anagram (singleplayer)
    """
    # Initialise variables
    def __init__(self, client: Bot, colour: Colour) -> None:
        self.client = client
        self.colour = colour
        self.gameInitReaction = "✅"
        self.gameInitTimeout = 300
        self.ctx = None
        self.ID = None
        self.gameObj = None
        self.gameAllowed = None

    # Function to check a move for a game
    def checkMove(self, reaction: Reaction, user: User) -> bool:
        if self.ID == 1 or self.ID == 2:
            return reaction.message.id == self.gameObj[self.ctx.guild.id].gameMessage.id and user.id == self.gameObj[self.ctx.guild.id].nextPlayer.id and str(reaction) in self.gameObj[self.ctx.guild.id].gameEmojis
        elif self.ID == 3 or self.ID == 4:
            return reaction.message.id == self.gameObj[self.ctx.guild.id].gameMessage.id and self.gameObj[self.ctx.guild.id].user.id == user.id and str(reaction) in self.gameObj[self.ctx.guild.id].gameEmojis

    # Function to run a game based on a specific ID
    async def runGame(self, ctx: Context, ID: int) -> None:
        self.ctx = ctx
        self.ID = ID
        if self.gameAllowed[self.ctx.guild.id]:
            self.gameAllowed[self.ctx.guild.id] = False
            if ID == 1:
                self.gameObj[self.ctx.guild.id] = TicTacToe(self.ctx, self.client, self.colour)
                await self.twoplayer()
            elif ID == 2:
                self.gameObj[self.ctx.guild.id] = Connect4(self.ctx, self.client, self.colour)
                await self.twoplayer()
            elif ID == 3:
                self.gameObj[self.ctx.guild.id] = Hangman(self.ctx, self.client, self.colour)
                await self.singleplayer()
            elif ID == 4:
                self.gameObj[self.ctx.guild.id] = Anagram(self.ctx, self.client, self.colour)
                await self.singleplayer()
            await self.gameObj[self.ctx.guild.id].gameMessage.clear_reactions()
            self.gameObj[self.ctx.guild.id] = None
            self.gameAllowed[self.ctx.guild.id] = True
        else:
            await Utils.commandDebugEmbed(self.ctx.channel, "New game not allowed. Finish any currently running games")

    # Function to manage singleplayer games
    async def singleplayer(self) -> None:
        self.gameObj[self.ctx.guild.id].gameMessage = await self.ctx.channel.send(embed=Embed(title="Initialising, please wait", colour=self.colour))
        await self.runner()

    # Function to manage twoplayer games
    async def twoplayer(self) -> None:
        def gameReactChecker(reaction: Reaction, user: User) -> bool:
            return user.id != self.client.user.id and str(reaction) == self.gameInitReaction and reaction.message.guild.id == self.gameObj[self.ctx.guild.id].ctx.guild.id and user.id != self.gameObj[self.ctx.guild.id].ctx.author.id
        initialEmbed = Embed(title=f"{self.gameObj[self.ctx.guild.id]} Request", description=f"{self.gameObj[self.ctx.guild.id].player1.mention} wants to play {self.gameObj[self.ctx.guild.id]}. React to this message if you want to challenge them!", colour=self.colour)
        self.gameObj[self.ctx.guild.id].gameMessage = await self.gameObj[self.ctx.guild.id].ctx.send(embed=initialEmbed)
        await self.gameObj[self.ctx.guild.id].gameMessage.add_reaction(self.gameInitReaction)
        while True:
            try:
                reaction, user = await self.client.wait_for("reaction_add", timeout=self.gameInitTimeout, check=gameReactChecker)
                self.gameObj[self.ctx.guild.id].player2 = user
            except asyncio.TimeoutError:
                await Utils.commandDebugEmbed(self.ctx.channel, "Game has timed out")
            break
        if self.gameObj[self.ctx.guild.id].player2 is not None:
            await self.gameObj[self.ctx.guild.id].ctx.channel.send(f"Let's play {self.gameObj[self.ctx.guild.id]}! {self.gameObj[self.ctx.guild.id].player1.mention} vs {self.gameObj[self.ctx.guild.id].player2.mention}")
            await self.gameObj[self.ctx.guild.id].gameMessage.clear_reactions()
            await self.runner()

    # Function to run a game
    async def runner(self) -> None:
        await self.gameObj[self.ctx.guild.id].embedUpdate()
        for emoji in self.gameObj[self.ctx.guild.id].gameEmojis:
            await self.gameObj[self.ctx.guild.id].gameMessage.add_reaction(emoji)
        while self.gameObj[self.ctx.guild.id].isPlaying:
            # Test if the game has been idle for 5 minutes
            if Utils.gameActivity(self.gameObj[self.ctx.guild.id].lastActivity):
                self.gameObj[self.ctx.guild.id].isPlaying = False
                self.gameObj[self.ctx.guild.id].result = ("Timeout", None)
                await Utils.commandDebugEmbed(self.ctx.channel, "Game has timed out")
            else:
                try:
                    reaction, user = await self.client.wait_for("reaction_add", timeout=1, check=self.checkMove)
                    await self.gameObj[self.ctx.guild.id].gameMessage.remove_reaction(reaction, user)
                    self.gameObj[self.ctx.guild.id].processReaction(reaction)
                except asyncio.TimeoutError:
                    continue
            await self.gameObj[self.ctx.guild.id].embedUpdate()
