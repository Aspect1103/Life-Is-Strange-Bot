# Builtin
import asyncio
import random
import requests
import os
# Pip
from discord.ext import commands
from discord import Embed
from discord import Colour
from bs4 import BeautifulSoup
import deviantart
# Custom
from Utils.Connect4 import Connect4
from Utils.TicTacToe import TicTacToe
from Utils import Utils
import Config

# Path variables
rootDirectory = os.path.join(os.path.dirname(__file__), os.pardir)
questionPath = os.path.join(rootDirectory, "TextFiles", "questions.txt")


# Cog to manage general commands
class General(commands.Cog):
    # Initialise the client
    def __init__(self, client):
        self.client = client
        self.nextQuestion = 0
        self.colour = Colour.blue()
        self.imageGroup = ["art"]
        self.generalGroup = ["question", "connect4", "tictactoe"]
        self.gameInitReaction = "✅"
        self.isNewGameAllowed = True
        self.allowedIDsImage = None
        self.allowedIDsGeneral = None
        self.deviantAPI = None
        self.questionArray = None
        self.generalInit()

    # Function to initialise general variables
    def generalInit(self):
        # Create questions array
        temp = []
        with open(questionPath, "r", encoding="utf") as file:
            for line in file.readlines():
                temp.append(line.replace("\n", ""))
        random.shuffle(temp)
        self.questionArray = temp

        # Setup allowed channel IDs
        self.allowedIDsImage = Utils.allowedIDs["image"]
        self.allowedIDsGeneral = Utils.allowedIDs["general"]

        # Setup the deviantart api
        self.refresh()

    # Function to refresh the deviantart api client
    def refresh(self):
        self.deviantAPI = deviantart.Api(Config.deviantartID, Config.deviantartSecret)

    # Function to calculate how many results available for a tag
    def tagAmmmount(self, tag):
        res = BeautifulSoup(requests.get(f"https://www.deviantart.com/search?q=%23{tag}").content, features="lxml")
        stringAmmount = res.find("span", {"class": "_1ahiJ"}).text[:-8]
        if "No results found" in stringAmmount:
            return None
        if "K" in stringAmmount:
            stringNumber = stringAmmount[:-1]
            return int(float(stringNumber)*1000)
        else:
            return int(stringAmmount)

    # Function to manage games
    async def gameManager(self, ctx, gameObj):
        # Function to detect if another player has reacted
        def gameReactChecker(reaction, user):
            #return user.id != self.client.user.id and str(reaction) == self.gameInitReaction and reaction.message.guild.id == gameObj.ctx.guild.id and user.id != gameObj.ctx.author.id
            return user.id != self.client.user.id and str(reaction) == self.gameInitReaction and reaction.message.guild.id == gameObj.ctx.guild.id
        # Test if a new game is allowed
        if self.isNewGameAllowed:
            self.isNewGameAllowed = False
            # Send reaction embed
            initialEmbed = Embed(title=f"{gameObj} Request", description=f"{gameObj.player1.mention} wants to play {gameObj}. React to this message if you want to challenge them!", colour=self.colour)
            gameObj.gameMessage = await gameObj.ctx.send(embed=initialEmbed)
            await gameObj.gameMessage.add_reaction(self.gameInitReaction)
            # Wait until another player reacts
            while True:
                try:
                    reaction, user = await self.client.wait_for("reaction_add", timeout=gameObj.timeout, check=gameReactChecker)
                    gameObj.player2 = user
                except asyncio.TimeoutError:
                    await gameObj.ctx.send("Game has timed out")
                break
            # Play game
            await gameObj.ctx.channel.send(f"Let's play {gameObj}! {gameObj.player1.mention} vs {gameObj.player2.mention}")
            await gameObj.gameMessage.clear_reactions()
            await gameObj.updateBoard()
            await gameObj.sendEmojis()
            await gameObj.start()
            self.isNewGameAllowed = True
        else:
            await ctx.channel.send("No new games allowed, finish the current one")

    # art command with a cooldown of 1 use every 10 seconds per guild
    @commands.command(help="Displays a random LiS fanart based on a tag. It has a cooldown of 15 seconds", description="\nArguments:\nTag - The deviantart tag to search on", usage="art (tag)", brief="Image")
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def art(self, ctx, *tag):
        if len(tag) == 0:
            # No tag given
            await ctx.channel.send("No tag given, try again")
        elif len(tag) > 1:
            # Too many tags
            await ctx.channel.send("Too many tags. Only one is supported")
        else:
            # Get amount of results
            maxResult = self.tagAmmmount(tag[0])
            if maxResult is None:
                # No results
                await ctx.channel.send("No results found")
            else:
                # Get all results for a random page
                if maxResult > 4999:
                    # Too many pages so reduce it
                    maxResult = 4999
                results = self.deviantAPI.browse(endpoint="tags", tag=tag[0], offset=random.randint(0, maxResult), limit=20)
                if len(results["results"]) == 0:
                    # No results
                    await ctx.channel.send("No results found")
                else:
                    # Add all results with an image to a list
                    final = []
                    for result in results["results"]:
                        try:
                            final.append(result)
                        except TypeError:
                            pass
                    # Pick a random image and send it
                    randomImage = final[random.randint(0, len(final)-1)]
                    await ctx.channel.send(f"{randomImage.title} by {randomImage.author}. Link: {randomImage.url}")

    # question command with a cooldown of 1 use every 15 seconds per guild
    @commands.command(help="Displays a random question for users to answer. It has a cooldown of 15 seconds", usage="question", brief="General")
    @commands.cooldown(1, 15, commands.BucketType.guild)
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
    @commands.command(help="Displays a player vs player game of connect 4. It has a cooldown of 300 seconds", usage="connect4", brief="General")
    @commands.cooldown(1, 300, commands.BucketType.guild)
    async def connect4(self, ctx):
        # Create connect 4 game object
        connect4 = Connect4(ctx, self.client, self.colour)
        # Run game manager to start the game
        await self.gameManager(ctx, connect4)

    # tictactoe command with a cooldown of 1 use every 90 seconds per guild
    @commands.command(help="Displays a player vs player game of tic tac toe. It has a cooldown of 90 seconds", usage="tictactoe", brief="General")
    @commands.cooldown(1, 90, commands.BucketType.guild)
    async def tictactoe(self, ctx):
        # Create tictactoe game object
        tictactoe = TicTacToe(ctx, self.client, self.colour)
        # Run game manager to start the game
        await self.gameManager(ctx, tictactoe)

    # Function to run channelCheck for general
    async def cog_check(self, ctx):
        if str(ctx.command) in self.imageGroup:
            return Utils.channelCheck(ctx, self.allowedIDsImage)
        elif str(ctx.command) in self.generalGroup:
            return Utils.channelCheck(ctx, self.allowedIDsGeneral)

    # Catch any cog errors
    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            if str(ctx.command) in self.imageGroup:
                textChannelAllowed = [self.client.get_channel(channel) for channel in self.allowedIDsImage[str(ctx.guild.id)]]
            elif str(ctx.command) in self.generalGroup:
                textChannelAllowed = [self.client.get_channel(channel) for channel in self.allowedIDsGeneral[str(ctx.guild.id)]]
            if all(element is None for element in textChannelAllowed):
                await ctx.channel.send(f"No channels added. Use {ctx.prefix}channel to add some")
            else:
                guildAllowed = ", ".join([channel.mention for channel in filter(None, textChannelAllowed) if channel.guild.id == ctx.guild.id])
                await ctx.channel.send(f"This command is only allowed in {guildAllowed}")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.channel.send(f"Command is on cooldown, try again in {round(error.retry_after, 2)} seconds")
        elif isinstance(error.original, deviantart.api.DeviantartError):
            if error.original.args[0].code == 401:
                await ctx.channel.send("Refreshing client")
                self.refresh()
                await ctx.channel.send("Client refreshed. Please try again")
        Utils.errorWrite(error)


# Function which initialises the General cog
def setup(client):
    client.add_cog(General(client))