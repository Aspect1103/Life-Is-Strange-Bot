# Pip
from discord.ext import commands
# Custom
from Utils import Utils


# Cog to manage miscellaneous commands
class Miscellaneous(commands.Cog):
    # Initialise the client
    def __init__(self, client):
        self.client = client

    # bum command with a cooldown of 1 use every 10 seconds per guild
    @commands.command(help="Displays a hypnotic gif. It has a cooldown of 10 seconds", usage="bum")
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def bum(self, ctx):
        await ctx.channel.send("https://giphy.com/gifs/midland-l4FsJgbbeKQC8MGBy")

    # murica command with a cooldown of 1 use every 10 seconds per guild
    @commands.command(help="Displays a patriot. It has a cooldown of 10 seconds", usage="murica")
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def murica(self, ctx):
        await ctx.channel.send("https://tenor.com/view/merica-gif-9091003")

    # puppy command with a cooldown of 1 use every 10 seconds per guild
    @commands.command(help="Displays a cute puppy. It has a cooldown of 10 seconds", usage="murica")
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def puppy(self, ctx):
        await ctx.channel.send("https://www.youtube.com/watch?v=j5a0jTc9S10")

    # pizza command with a cooldown of 1 use every 10 seconds per guild
    @commands.command(help="Displays a delicious pizza. It has a cooldown of 10 seconds", usage="pizza")
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def pizza(self, ctx):
        await ctx.channel.send("https://tenor.com/view/pizza-party-dance-dancing-gif-10213545")

    # Catch any cog errors
    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.channel.send(f"Command is on cooldown, try again in {round(error.retry_after, 2)} seconds")
        Utils.errorWrite(error)


# Function which initialises the Miscellaneous cog
def setup(client):
    client.add_cog(Miscellaneous(client))
