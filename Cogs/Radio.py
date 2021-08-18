# Pip
from discord.ext import commands
# Custom
from Helpers.Utils import Utils


# Cog to manage radio commands
class Radio(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Function to run channelCheck for Radio
    async def cog_check(self, ctx):
        return await Utils.restrictor.commandCheck(ctx)

    # Catch any cog errors
    async def cog_command_error(self, ctx, error):
        await Utils.errorHandler(ctx, error)


# Function which initialises the Radio cog
def setup(client):
    client.add_cog(Radio(client))
