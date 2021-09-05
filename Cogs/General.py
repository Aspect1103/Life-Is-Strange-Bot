# Builtin
from typing import Optional
import random
from pathlib import Path
# Pip
from discord import Embed, Colour
from discord.ext import commands
# Custom
from Helpers.Managers.GameManager import GameManager
from Helpers.Utils import Utils

# Path variables
rootDirectory = Path(__file__).parent.parent
questionPath = rootDirectory.joinpath("Resources").joinpath("Files").joinpath("questions.txt")


# Cog to manage general commands
class General(commands.Cog):
    # Initialise the bot
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.colour = Colour.blue()
        self.gameManager = GameManager(self.bot, self.colour)
        self.nextQuestion = 0
        self.isNewGameAllowed = True
        self.questionArray = None
        self.generalInit()
        self.bot.loop.create_task(self.startup())

    # Function to initialise general variables
    def generalInit(self) -> None:
        # Create questions array
        temp = [line.replace("\n", "") for line in open(questionPath, "r", encoding="utf").readlines()]
        random.shuffle(temp)
        self.questionArray = temp

    # Function which runs once the bot is setup and running
    async def startup(self) -> None:
        await self.bot.wait_until_ready()
        # Create dictionary for each guild to store variables
        self.gameManager.gameAllowed = {guild.id: True for guild in self.bot.guilds}
        self.gameManager.gameObj = {guild.id: {} for guild in self.bot.guilds}

    # question command with a cooldown of 1 use every 20 seconds per guild
    @commands.command(help=f"Displays a random question for users to answer. It has a cooldown of {Utils.short} seconds", usage="question", brief="General")
    @commands.cooldown(1, Utils.short, commands.BucketType.guild)
    async def question(self, ctx: commands.Context) -> None:
        if self.nextQuestion == len(self.questionArray):
            # All questions done
            random.shuffle(self.questionArray)
            self.nextQuestion = 0
        randomQuestion = self.questionArray[self.nextQuestion]
        self.nextQuestion += 1
        questionEmbed = Embed(title=randomQuestion,  colour=self.colour)
        questionEmbed.set_footer(text=f"{len(self.questionArray)} questions")
        await ctx.channel.send(embed=questionEmbed)

    # tictactoe command with a cooldown of 1 use every 60 seconds per guild
    @commands.command(help=f"Displays a player vs player game of tic tac toe. It has a cooldown of {Utils.long} seconds", usage="tictactoe", brief="General")
    @commands.cooldown(1, Utils.long, commands.BucketType.guild)
    async def tictactoe(self, ctx: commands.Context) -> None:
        await self.gameManager.runGame(ctx, 1)

    # connect4 command with a cooldown of 1 use every 300 seconds per guild
    @commands.command(help=f"Displays a player vs player game of connect 4. It has a cooldown of {Utils.superLong} seconds", usage="connect4", brief="General")
    @commands.cooldown(1, Utils.superLong, commands.BucketType.guild)
    async def connect4(self, ctx: commands.Context) -> None:
        await self.gameManager.runGame(ctx, 2)

    # hangmanStart command with a cooldown of 1 use every 120 seconds per guild
    @commands.command(help=f"Starts a hangman game using a random word from Life is Strange. It has a cooldown of {Utils.extraLong} seconds", usage="hangmanStart", brief="General")
    @commands.cooldown(1, Utils.extraLong, commands.BucketType.guild)
    async def hangmanStart(self, ctx: commands.Context) -> None:
        await self.gameManager.runGame(ctx, 3)

    # hangmanGuess command with a cooldown of 1 use every 5 seconds per guild
    @commands.command(help=f"Guesses a character in a hangman game. It has a cooldown of {Utils.superShort} seconds", description="\nArguments:\nCharacter - An alphabetic character to be guessed", usage="hangmanGuess <character>", brief="General")
    @commands.cooldown(1, Utils.superShort, commands.BucketType.guild)
    async def hangmanGuess(self, ctx: commands.Context, character: Optional[str] = None):
        try:
            if str(self.gameManager.gameObj[ctx.guild.id][ctx.author]) == "Hangman":
                await self.gameManager.gameObj[ctx.guild.id][ctx.author].guess(character)
        except KeyError:
            await Utils.commandDebugEmbed(ctx.channel, f"Game is not currently running. Start it with {ctx.prefix}hangmanStart")

    # anagramStart command with a cooldown of 1 use every 60 seconds per guild
    @commands.command(help=f"Starts a LiS anagram puzzle game. It has a cooldown of {Utils.extraLong} seconds", usage="anagramStart", brief="General")
    @commands.cooldown(1, Utils.extraLong, commands.BucketType.guild)
    async def anagramStart(self, ctx: commands.Context) -> None:
        await self.gameManager.runGame(ctx, 4)

    # anagramGuess command with a cooldown of 1 use every 5 seconds per guild
    @commands.command(help=f"Guesses a word in an anagram game. It has a cooldown of {Utils.superShort} seconds", description="\nArguments:\nWord - An alphabetic word to be guessed", usage="anagramGuess <word>", brief="General")
    @commands.cooldown(1, Utils.superShort, commands.BucketType.guild)
    async def anagramGuess(self, ctx: commands.Context, word: Optional[str] = None) -> None:
        try:
            if str(self.gameManager.gameObj[ctx.guild.id][ctx.author]) == "Anagram":
                await self.gameManager.gameObj[ctx.guild.id][ctx.author].guess(word)
        except KeyError:
            await Utils.commandDebugEmbed(ctx.channel, f"Game is not currently running. Start it with {ctx.prefix}anagramStart")

    # sokoban command with a cooldown of 1 use every 120 seconds per guild
    @commands.command(help=f"Displays a randomly generated Sokoban game. It has a cooldown of {Utils.extraLong} seconds", usage="sokoban", brief="General")
    @commands.cooldown(1, Utils.extraLong, commands.BucketType.guild)
    async def sokoban(self, ctx: commands.Context) -> None:
        await self.gameManager.runGame(ctx, 5)

    # Function to run channelCheck for General
    async def cog_check(self, ctx: commands.Context) -> None:
        return await Utils.restrictor.commandCheck(ctx)

    # Catch any cog errors
    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        await Utils.errorHandler(ctx, error)


# Function which initialises the General cog
def setup(bot: commands.Bot) -> None:
    bot.add_cog(General(bot))
