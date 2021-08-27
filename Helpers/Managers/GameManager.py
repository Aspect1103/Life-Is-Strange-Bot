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
        1 - TicTacToe (twoplayer)
        2 - Connect4 (twoplayer)
        3 - Hangman (singleplayer)
        4 - Anagram (singleplayer)
    """
    # Initialise variables
    def __init__(self, client: Bot, colour: Colour) -> None:
        self.client = client
        self.colour = colour
        self.twoplayerInitReaction = "✅"
        self.gameInitTimeout = 300
        self.gameObj = None

    # Function to test if a game is a twoplayer game or not
    def isTwoplayer(self, ctx: Context) -> bool:
        gameTypes = {
            True: ["TicTacToe", "Connect4"],
            False: ["Hangman", "Anagram"]
        }
        for key, value in gameTypes.items():
            if str(self.gameObj[ctx.guild.id][ctx.author]) in value:
                return key

    # Function to update the game leaderboard
    def updateGameScores(self, ctx: Context) -> None:
        if self.isTwoplayer(ctx):
            if str(self.gameObj[ctx.guild.id][ctx.author]) == "TicTacToe":
                print("tic")
            elif str(self.gameObj[ctx.guild.id][ctx.author]) == "Connect4":
                print("4")
        else:
            if str(self.gameObj[ctx.guild.id][ctx.author]) == "Hangman":
                print("hang")
            elif str(self.gameObj[ctx.guild.id][ctx.author]) == "Anagram":
                print("ana")

    # Function to run a game based on a specific ID
    async def runGame(self, ctx: Context, ID: int) -> None:
        if ctx.author not in self.gameObj[ctx.guild.id]:
            if ID == 1:
                self.gameObj[ctx.guild.id][ctx.author] = TicTacToe(ctx, self.client, self.colour)
                await self.twoplayer(ctx)
            elif ID == 2:
                self.gameObj[ctx.guild.id][ctx.author] = Connect4(ctx, self.client, self.colour)
                await self.twoplayer(ctx)
            elif ID == 3:
                self.gameObj[ctx.guild.id][ctx.author] = Hangman(ctx, self.client, self.colour)
                await self.singleplayer(ctx)
            elif ID == 4:
                self.gameObj[ctx.guild.id][ctx.author] = Anagram(ctx, self.client, self.colour)
                await self.singleplayer(ctx)
            await self.gameObj[ctx.guild.id][ctx.author].gameMessage.clear_reactions()
            self.updateGameScores(ctx)
            del self.gameObj[ctx.guild.id][ctx.author]
        else:
            await Utils.commandDebugEmbed(ctx.channel, "You can only run one game per user at a time")

    # Function to manage singleplayer games
    async def singleplayer(self, ctx: Context) -> None:
        self.gameObj[ctx.guild.id][ctx.author].gameMessage = await ctx.channel.send(embed=Embed(title="Initialising, please wait", colour=self.colour))
        await self.runner(ctx)

    # Function to manage twoplayer games
    async def twoplayer(self, ctx: Context) -> None:
        def gameReactChecker(reaction: Reaction, user: User) -> bool:
            return user.id != self.client.user.id and user.id != ctx.author.id and str(reaction) == self.twoplayerInitReaction and reaction.message.guild.id == self.gameObj[ctx.guild.id][ctx.author].ctx.guild.id and reaction.message.id == reactMessage.id
        initialEmbed = Embed(title=f"{self.gameObj[ctx.guild.id][ctx.author]} Request", description=f"{self.gameObj[ctx.guild.id][ctx.author].player1.mention} wants to play {self.gameObj[ctx.guild.id][ctx.author]}. React to this message if you want to challenge them!", colour=self.colour)
        reactMessage = self.gameObj[ctx.guild.id][ctx.author].gameMessage = await ctx.channel.send(embed=initialEmbed)
        await self.gameObj[ctx.guild.id][ctx.author].gameMessage.add_reaction(self.twoplayerInitReaction)
        while True:
            try:
                reaction, user = await self.client.wait_for("reaction_add", timeout=self.gameInitTimeout, check=gameReactChecker)
                self.gameObj[ctx.guild.id][ctx.author].player2 = user
            except asyncio.TimeoutError:
                await Utils.commandDebugEmbed(ctx.channel, "Game has timed out")
            break
        if self.gameObj[ctx.guild.id][ctx.author].player2 is not None:
            await ctx.channel.send(f"Let's play {self.gameObj[ctx.guild.id][ctx.author]}! {self.gameObj[ctx.guild.id][ctx.author].player1.mention} vs {self.gameObj[ctx.guild.id][ctx.author].player2.mention}")
            await self.gameObj[ctx.guild.id][ctx.author].gameMessage.clear_reactions()
            await self.runner(ctx)

    # Function to run a game
    async def runner(self, ctx: Context) -> None:
        def checkMove(reaction: Reaction, user: User) -> bool:
            if self.isTwoplayer(ctx):
                return reaction.message.id == self.gameObj[ctx.guild.id][ctx.author].gameMessage.id and user.id == self.gameObj[ctx.guild.id][ctx.author].nextPlayer.id and str(reaction) in self.gameObj[ctx.guild.id][ctx.author].gameEmojis
            else:
                return reaction.message.id == self.gameObj[ctx.guild.id][ctx.author].gameMessage.id and user.id == self.gameObj[ctx.guild.id][ctx.author].user.id and str(reaction) in self.gameObj[ctx.guild.id][ctx.author].gameEmojis
        await self.gameObj[ctx.guild.id][ctx.author].embedUpdate()
        for emoji in self.gameObj[ctx.guild.id][ctx.author].gameEmojis:
            await self.gameObj[ctx.guild.id][ctx.author].gameMessage.add_reaction(emoji)
        while self.gameObj[ctx.guild.id][ctx.author].isPlaying:
            # Test if the game has been idle for 5 minutes
            if Utils.gameActivity(self.gameObj[ctx.guild.id][ctx.author].lastActivity):
                self.gameObj[ctx.guild.id][ctx.author].isPlaying = False
                self.gameObj[ctx.guild.id][ctx.author].result = ("Timeout", None)
                await Utils.commandDebugEmbed(ctx.channel, "Game has timed out")
            else:
                try:
                    reaction, user = await self.client.wait_for("reaction_add", timeout=1, check=checkMove)
                    await self.gameObj[ctx.guild.id][ctx.author].gameMessage.remove_reaction(reaction, user)
                    self.gameObj[ctx.guild.id][ctx.author].processReaction(reaction)
                except asyncio.TimeoutError:
                    continue
            await self.gameObj[ctx.guild.id][ctx.author].embedUpdate()
