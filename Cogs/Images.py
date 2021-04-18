# Import libraries
from discord.ext import commands
from discord import File
from datetime import datetime
import os
import json
import random

# Path variables
rootDirectory = os.path.join(os.path.dirname(__file__), os.pardir)
idPath = os.path.join(rootDirectory, "TextFiles", "IDs.txt")
imagePath = os.path.join(rootDirectory, "Images")


# Cog to manage fanfic commands
class Images(commands.Cog):
    # Initialise the client
    def __init__(self, client):
        self.client = client
        self.allowedIDs = None
        self.imageInit()

    # Function to initialise image variables
    def imageInit(self):
        # Load allowed channel IDs
        with open(idPath, "r") as file:
            self.allowedIDs = json.loads(file.read())["image"]

    # Function to check if a command is in the correct channel
    def channelCheck(self, ctx):
        return ctx.channel.id in self.allowedIDs

    # art command with a cooldown of 1 use every 10 seconds per guild
    @commands.command(help="Displays a random LiS fanart. It has a cooldown of 10 seconds")
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def art(self, ctx):
        # Get a random image's filepath
        files = os.listdir(imagePath)
        randomImagePath = os.path.join(imagePath, files[random.randint(0, len(files)-1)])
        # Send image
        await ctx.channel.send(file=File(randomImagePath))

    # Function to run channelCheck for s?trivia
    async def cog_check(self, ctx):
        return self.channelCheck(ctx)

    # Catch any cog errors
    async def cog_command_error(self, ctx, error):
        errorPath = os.path.join(rootDirectory, "BotFiles", "error.txt")
        if isinstance(error, commands.CheckFailure):
            textChannelAllowed = [self.client.get_channel(channel) for channel in self.allowedIDs]
            guildAllowed = ", ".join([channel.mention for channel in filter(None, textChannelAllowed)])
            await ctx.channel.send(f"This command is only allowed in {guildAllowed}")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.channel.send(f"Command is on cooldown, try again in {round(error.retry_after, 2)} seconds")
        with open(errorPath, "a") as file:
            file.write(f"{datetime.now()}, {error}\n")


# Function which initialises the Fanfic cog
def setup(client):
    client.add_cog(Images(client))