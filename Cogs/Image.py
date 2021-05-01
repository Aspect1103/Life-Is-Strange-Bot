# Builtin
import random
import requests
# Pip
from bs4 import BeautifulSoup
from discord.ext import commands
import deviantart
# Custom
from Utils import Utils
import Config


# Cog to manage fanfic commands
class Image(commands.Cog):
    # Initialise the client
    def __init__(self, client):
        self.client = client
        self.allowedIDs = None
        self.deviantAPI = None
        self.imageInit()

    # Function to initialise image variables
    def imageInit(self):
        # Setup allowed channel IDs
        self.allowedIDs = Utils.allowedIDs["image"]

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

    # art command with a cooldown of 1 use every 10 seconds per guild
    @commands.command(help="Displays a random LiS fanart based on a tag. It has a cooldown of 15 seconds", description="\nArguments:\nTag - The deviantart tag to search on", usage="art (tag)")
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

    # Function to run channelCheck for images
    async def cog_check(self, ctx):
        return Utils.channelCheck(ctx, self.allowedIDs)

    # Catch any cog errors
    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            textChannelAllowed = [self.client.get_channel(channel) for channel in self.allowedIDs]
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


# Function which initialises the Image cog
def setup(client):
    client.add_cog(Image(client))