# Builtin
import os
import json
# Pip
from discord import Client

# Path variables
rootDirectory = os.path.join(os.path.dirname(__file__), os.pardir)
idPath = os.path.join(rootDirectory, "TextFiles", "IDs.txt")


# Function to create allowedIDs
def initIDs():
    with open(idPath, "r") as file:
        return json.loads(file.read())


# Restrictor class to switch between different embeds
class Restrictor:
    # Initialise variables
    def __init__(self, client: Client, commandGroups: dict):
        self.client = client
        self.IDs = initIDs()
        self.commandGroups = commandGroups

    # Function to get the allowed channels for a command
    def getAllowed(self, ctx):
        for key, value in self.commandGroups.items():
            if str(ctx.command) in value:
                allowedChannels = self.IDs[key][str(ctx.guild.id)]
                if allowedChannels != -1:
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
