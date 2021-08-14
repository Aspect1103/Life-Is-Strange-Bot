# Builtin
import asyncio
# Pip
from discord import Colour
from discord import Client
from discord import Embed
# Custom
from Helpers.Games.TicTacToe import TicTacToe
from Helpers.Games.Connect4 import Connect4
from Helpers.Games.Hangman import Hangman
from Helpers.Utils import Utils


# GameManager class to streamline executing games
class GameManager:
    """
    Game Modes:
        1 - TicTacToe (multiplayer)
        2 - Connect4 (multiplayer)
        3 - Hangman (singleplayer)
    """
    # Initialise variables
    def __init__(self, client: Client, colour: Colour):
        self.client = client
        self.colour = colour
        self.gameInitReaction = "✅"
        self.gameInitTimeout = 300
        self.ctx = None
        self.gameObj = None
        self.gameAllowed = None

    # Run a game based on a specific ID
    async def runGame(self, ctx, ID):
        self.ctx = ctx
        if self.gameAllowed[self.ctx.guild.id]:
            self.gameAllowed[self.ctx.guild.id] = False
            if ID == 1:
                self.gameObj = TicTacToe(self.ctx, self.client, self.colour)
                await self.multiplayer()
            elif ID == 2:
                self.gameObj = Connect4(self.ctx, self.client, self.colour)
                await self.multiplayer()
            elif ID == 3:
                self.gameObj = Hangman(self.ctx, self.client, self.colour)
                await self.singleplayer()
            await self.gameObj.gameMessage.clear_reactions()
            self.gameObj = None
            self.gameAllowed[self.ctx.guild.id] = True
        else:
            await Utils.commandDebugEmbed(self.ctx, True, "New game not allowed. Finish any currently running games")

    # Manage singleplayer games
    async def singleplayer(self):
        await self.gameObj.start()

    # Manage multiplayer games
    async def multiplayer(self):
        def gameReactChecker(reaction, user):
            return user.id != self.client.user.id and str(reaction) == self.gameInitReaction and reaction.message.guild.id == self.gameObj.ctx.guild.id and user.id != self.gameObj.ctx.author.id
        initialEmbed = Embed(title=f"{self.gameObj} Request", description=f"{self.gameObj.player1.mention} wants to play {self.gameObj}. React to this message if you want to challenge them!", colour=self.colour)
        self.gameObj.gameMessage = await self.gameObj.ctx.send(embed=initialEmbed)
        await self.gameObj.gameMessage.add_reaction(self.gameInitReaction)
        while True:
            try:
                reaction, user = await self.client.wait_for("reaction_add", timeout=self.gameInitTimeout, check=gameReactChecker)
                self.gameObj.player2 = user
            except asyncio.TimeoutError:
                await Utils.commandDebugEmbed(self.ctx, False, "Game has timed out")
            break
        if self.gameObj.player2 is not None:
            await self.gameObj.ctx.channel.send(f"Let's play {self.gameObj}! {self.gameObj.player1.mention} vs {self.gameObj.player2.mention}")
            await self.gameObj.gameMessage.clear_reactions()
            await self.gameObj.updateBoard()
            for emoji in self.gameObj.gameEmojis:
                await self.gameObj.gameMessage.add_reaction(emoji)
            await self.gameObj.start()
