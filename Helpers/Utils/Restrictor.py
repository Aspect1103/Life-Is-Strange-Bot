# Builtin
from pathlib import Path
from typing import Union, List, Dict
# Pip
from discord import TextChannel, VoiceChannel
from discord.ext.commands import Context, Bot

# Path variables
rootDirectory = Path(__file__).parent.parent
idPath = rootDirectory.joinpath("Resources").joinpath("Files").joinpath("IDs.txt")


# Restrictor class to switch between different embeds
class Restrictor:
    # Initialise variables
    def __init__(self, IDs: Dict[str, Dict[str, List[int]]], commandGroups: Dict[str, List[str]]) -> None:
        self.IDs = IDs
        self.commandGroups = commandGroups
        self.bot = None

    # Function to set the bot variable
    def setBot(self, bot: Bot) -> None:
        self.bot = bot

    # Function to get the allowed channels for a command
    def getAllowed(self, ctx: Context) -> Union[List[int], None]:
        for key, value in self.commandGroups.items():
            if str(ctx.command) in value:
                allowedChannels = self.IDs[key][str(ctx.guild.id)]
                if allowedChannels[0] != -1:
                    return allowedChannels
        return None

    # Function to check if a command is allowed in a specific channel
    async def commandCheck(self, ctx: Context) -> bool:
        allowedChannel = self.getAllowed(ctx)
        if allowedChannel is not None:
            return ctx.channel.id in allowedChannel
        return True

    # Function to grab the allowed channels
    async def grabAllowed(self, ctx: Context) -> str:
        allowedChannel = self.getAllowed(ctx)
        textChannelAllowed: List[Union[TextChannel, VoiceChannel]] = [self.bot.get_channel(channel) for channel in allowedChannel]
        guildAllowed = ", ".join([channel.mention for channel in textChannelAllowed])
        return f"This command is only allowed in {guildAllowed}"
