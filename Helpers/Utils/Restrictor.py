# Builtin
from pathlib import Path
# Pip
from discord import Client

# Path variables
rootDirectory = Path(__file__).parent.parent
idPath = rootDirectory.joinpath("Resources").joinpath("Files").joinpath("IDs.txt")


# Restrictor class to switch between different embeds
class Restrictor:
    # Initialise variables
    def __init__(self, IDs: dict, commandGroups: dict):
        self.IDs = IDs
        self.commandGroups = commandGroups
        self.client = None

    # Function to set the client variables
    def setClient(self, client: Client):
        self.client = client

    # Function to get the allowed channels for a command
    def getAllowed(self, ctx):
        for key, value in self.commandGroups.items():
            if str(ctx.command) in value:
                allowedChannels = self.IDs[key][str(ctx.guild.id)]
                if allowedChannels[0] != -1:
                    return allowedChannels
        return None

    # Function to check if a command is allowed in a specific channel
    async def commandCheck(self, ctx):
        allowedChannel = self.getAllowed(ctx)
        if allowedChannel is not None:
            return ctx.channel.id in allowedChannel
        return True

    # Function to grab the allowed channels
    async def grabAllowed(self, ctx):
        allowedChannel = self.getAllowed(ctx)
        if allowedChannel is not None:
            textChannelAllowed = [self.client.get_channel(channel) for channel in allowedChannel]
            guildAllowed = ", ".join([channel.mention for channel in textChannelAllowed])
            return f"This command is only allowed in {guildAllowed}"
