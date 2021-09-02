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

    # Base function to initialise the hangman group commands with a cooldown of 5 seconds
    @commands.group(invoke_without_command=True, help=f"Group command for playing a hangman game using words from Life is Strange. This command has subcommands. It has a cooldown of {Utils.superShort} seconds", usage="hangman", brief="General")
    @commands.cooldown(1, Utils.superShort, commands.BucketType.guild)
    async def hangman(self, ctx: commands.Context) -> None:
        await ctx.send_help(ctx.command)

    # hangman start command with a cooldown of 1 use every 120 seconds per guild
    @hangman.command(help=f"Starts a hangman game using a random word from Life is Strange. It has a cooldown of {Utils.extraLong} seconds", usage="hangman start", brief="General")
    @commands.cooldown(1, Utils.extraLong, commands.BucketType.guild)
    async def start(self, ctx: commands.Context) -> None:
        await self.gameManager.runGame(ctx, 3)

    # hangman guess command with a cooldown of 1 use every 5 seconds per guild
    @hangman.command(help=f"Guesses a character in a hangman game. It has a cooldown of {Utils.superShort} seconds", description="\nArguments:\nCharacter - An alphabetic character to be guessed", usage="hangman guess (character)", brief="General")
    @commands.cooldown(1, Utils.superShort, commands.BucketType.guild)
    async def guess(self, ctx: commands.Context, character: Optional[str] = None):
        if str(self.gameManager.gameObj[ctx.guild.id][ctx.author]) == "Hangman":
            await self.gameManager.gameObj[ctx.guild.id][ctx.author].guess(character)
        else:
            await Utils.commandDebugEmbed(ctx.channel, f"Game is not currently running. Start it with {ctx.prefix}hangman start")

    # Base function to initialise the anagram group commands with a cooldown of 5 seconds
    @commands.group(invoke_without_command=True, help=f"Group command for playing a LiS anagram puzzle game. This command has subcommands. It has a cooldown of {Utils.superShort} seconds", usage="anagram", brief="General")
    @commands.cooldown(1, Utils.superShort, commands.BucketType.guild)
    async def anagram(self, ctx: commands.Context) -> None:
        await ctx.send_help(ctx.command)

    # anagram start command with a cooldown of 1 use every 60 seconds per guild
    @anagram.command(help=f"Starts a LiS anagram puzzle game. It has a cooldown of {Utils.extraLong} seconds", usage="anagram start", brief="General")
    @commands.cooldown(1, Utils.extraLong, commands.BucketType.guild)
    async def start(self, ctx: commands.Context) -> None:
        await self.gameManager.runGame(ctx, 4)

    # anagram guess command with a cooldown of 1 use every 5 seconds per guild
    @anagram.command(help=f"Guesses a word in an anagram game. It has a cooldown of {Utils.superShort} seconds", description="\nArguments:\nWord - An alphabetic word to be guessed", usage="anagram guess (word)", brief="General")
    @commands.cooldown(1, Utils.superShort, commands.BucketType.guild)
    async def guess(self, ctx: commands.Context, word: Optional[str] = None) -> None:
        if str(self.gameManager.gameObj[ctx.guild.id][ctx.author]) == "Anagram":
            await self.gameManager.gameObj[ctx.guild.id][ctx.author].guess(word)
        else:
            await Utils.commandDebugEmbed(ctx.channel, f"Game is not currently running. Start it with {ctx.prefix}anagram start")

    # sokoban command with a cooldown of 1 use every 120 seconds per guild
    @commands.command(help=f"Displays a randomly generated Sokoban game. It has a cooldown of {Utils.extraLong} seconds", usage="sokoban", brief="General")
    @commands.cooldown(1, Utils.extraLong, commands.BucketType.guild)
    async def sokoban(self, ctx: commands.Context) -> None:
        await self.gameManager.runGame(ctx, 5)

    # Function to run channelCheck for General
    async def cog_check(self, ctx: commands.Context) -> None:
        return await Utils.restrictor.commandCheck(ctx)

    # Catch any cog errors
    #async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
    #    await Utils.errorHandler(ctx, error)


# Function which initialises the General cog
def setup(bot: commands.Bot) -> None:
    bot.add_cog(General(bot))
