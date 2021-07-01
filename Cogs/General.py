# Builtin
import asyncio
import random
import os
# Pip
from discord.ext import commands
from discord import Embed
from discord import Colour
# Custom
from Utils.TicTacToe import TicTacToe
from Utils.Connect4 import Connect4
from Utils.Hangman import Hangman
from Utils import Utils

# Path variables
rootDirectory = os.path.join(os.path.dirname(__file__), os.pardir)
questionPath = os.path.join(rootDirectory, "Resources", "questions.txt")


# Cog to manage general commands
class General(commands.Cog):
    # Initialise the client
    def __init__(self, client):
        self.client = client
        self.colour = Colour.blue()
        self.gameInitReaction = "✅"
        self.nextQuestion = 0
        self.gameTimeout = 300
        self.isNewGameAllowed = True
        self.questionArray = None
        self.hangmanInstance = None
        self.generalInit()

    # Function to initialise general variables
    def generalInit(self):
        # Create questions array
        temp = [line.replace("\n", "") for line in open(questionPath, "r", encoding="utf").readlines()]
        random.shuffle(temp)
        self.questionArray = temp

    # Function to manage games
    async def gameManager(self, ctx, gameObj):
        if self.isNewGameAllowed:
            # Stop more games from being started
            self.isNewGameAllowed = False
            # Function to detect if another player has reacted
            def gameReactChecker(reaction, user):
                return user.id != self.client.user.id and str(reaction) == self.gameInitReaction and reaction.message.guild.id == gameObj.ctx.guild.id and user.id != gameObj.ctx.author.id
            # Send reaction embed
            initialEmbed = Embed(title=f"{gameObj} Request", description=f"{gameObj.player1.mention} wants to play {gameObj}. React to this message if you want to challenge them!", colour=self.colour)
            gameObj.gameMessage = await gameObj.ctx.send(embed=initialEmbed)
            await gameObj.gameMessage.add_reaction(self.gameInitReaction)
            # Wait until another player reacts
            while True:
                try:
                    reaction, user = await self.client.wait_for("reaction_add", timeout=self.gameTimeout, check=gameReactChecker)
                    gameObj.player2 = user
                except asyncio.TimeoutError:
                    await gameObj.ctx.send("Game has timed out")
                break
            # Play game
            gameObj.timeout = self.gameTimeout
            if gameObj.player2 is not None:
                await gameObj.ctx.channel.send(f"Let's play {gameObj}! {gameObj.player1.mention} vs {gameObj.player2.mention}")
                await gameObj.gameMessage.clear_reactions()
                await gameObj.updateBoard()
                await gameObj.sendEmojis()
                await gameObj.start()
            await gameObj.gameMessage.clear_reactions()
            del gameObj
            self.isNewGameAllowed = True
        else:
            await ctx.channel.send("New game not allowed. Finish any currently running games")

    # question command with a cooldown of 1 use every 20 seconds per guild
    @commands.command(help=f"Displays a random question for users to answer. It has a cooldown of {Utils.short} seconds", usage="question", brief="General")
    @commands.cooldown(1, Utils.short, commands.BucketType.guild)
    async def question(self, ctx):
        if self.nextQuestion == len(self.questionArray):
            # All questions done
            random.shuffle(self.questionArray)
            self.nextQuestion = 0
        randomQuestion = self.questionArray[self.nextQuestion]
        self.nextQuestion += 1
        questionEmbed = Embed(title=randomQuestion,  colour=self.colour)
        questionEmbed.set_footer(text=f"{len(self.questionArray)} questions")
        await ctx.channel.send(embed=questionEmbed)

    # connect4 command with a cooldown of 1 use every 300 seconds per guild
    @commands.command(help=f"Displays a player vs player game of connect 4. It has a cooldown of {Utils.superLong} seconds", usage="connect4", brief="General")
    @commands.cooldown(1, Utils.superLong, commands.BucketType.guild)
    async def connect4(self, ctx):
        # Create connect 4 game object
        connect4 = Connect4(ctx, self.client, self.colour)
        # Run game manager to start the game
        await self.gameManager(ctx, connect4)

    # tictactoe command with a cooldown of 1 use every 60 seconds per guild
    @commands.command(help=f"Displays a player vs player game of tic tac toe. It has a cooldown of {Utils.long} seconds", usage="tictactoe", brief="General")
    @commands.cooldown(1, Utils.long, commands.BucketType.guild)
    async def tictactoe(self, ctx):
        # Create tictactoe game object
        tictactoe = TicTacToe(ctx, self.client, self.colour)
        # Run game manager to start the game
        await self.gameManager(ctx, tictactoe)

    # Base function to initialise the hangman group commands with a cooldown of 10 seconds
    @commands.group(invoke_without_command=True, help=f"Group command for playing a hangman game using words from Life is Strange. This command has subcommands. It has a cooldown of {Utils.superShort} seconds", usage="hangman", brief="General")
    @commands.cooldown(1, Utils.superShort, commands.BucketType.guild)
    async def hangman(self, ctx):
        await ctx.send_help(ctx.command)

    # hangman start command with a cooldown of 1 use every 60 seconds per guild
    @hangman.command(help=f"Starts a hangman game using a random word from Life is Strange. It has a cooldown of {Utils.long} seconds", usage="hangman start", brief="General")
    @commands.cooldown(1, Utils.long, commands.BucketType.guild)
    async def start(self, ctx):
        if self.isNewGameAllowed:
            self.isNewGameAllowed = False
            self.hangmanInstance = Hangman(ctx, self.client, self.colour)
            await self.hangmanInstance.start()
            await self.hangmanInstance.message.clear_reactions()
            self.hangmanInstance = None
            self.isNewGameAllowed = True
        else:
            await ctx.channel.send("New game not allowed. Finish any currently running games")

    # hangman guess command
    @hangman.command(help="Guesses a character in a hangman game", description="\nArguments:\nCharacter - An alphabetic character", usage="hangman guess (character)", brief="General")
    async def guess(self, ctx, *args):
        if self.hangmanInstance is not None:
            await self.hangmanInstance.guess(args)
        else:
            await ctx.channel.send(f"Game is not currently running. Start it with {ctx.prefix}hangman start")

    # Function to run channelCheck for General
    async def cog_check(self, ctx):
        result = await Utils.restrictor.commandCheck(ctx)
        return result

    # Catch any cog errors
    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            result = await Utils.restrictor.grabAllowed(ctx)
            await ctx.channel.send(result)
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.channel.send(f"Command is on cooldown, try again in {round(error.retry_after, 2)} seconds")
        Utils.errorWrite(error)


# Function which initialises the General cog
def setup(client):
    client.add_cog(General(client))
