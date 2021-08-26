# Builtin
from typing import List
import logging
from pathlib import Path
# Pip
from discord import Status, Activity, ActivityType, Intents, Guild
from discord.ext import commands
# Custom
import Config
from Helpers.Utils import Utils

# Discord variables
intents = Intents.default()
intents.members = True
client = commands.Bot(command_prefix="$", intents=intents)

# Path variables
rootDirectory = Path(__file__).parent
logPath = rootDirectory.joinpath("DebugFiles").joinpath("lisBot.log")


# Runs when the bot joins a guild
@client.event
async def on_guild_join(guild: Guild) -> None:
    tempDict = Utils.IDs
    for key, value in tempDict.items():
        value[str(guild.id)] = [-1]
    Utils.idWriter(tempDict)


# Runs when the bot leaves a guild
@client.event
async def on_guild_remove(guild: Guild) -> None:
    tempDict = Utils.IDs
    for key, value in tempDict.items():
        del value[str(guild.id)]
    Utils.idWriter(tempDict)


# Runs when the bot has has started
@client.event
async def on_ready() -> None:
    # Setup the client variable for the restrictor and listener class
    Utils.restrictor.setClient(client)
    Utils.listener.setClient(client)
    # Change the presence to show the help command
    await client.change_presence(status=Status.online, activity=Activity(type=ActivityType.listening, name=f"{client.command_prefix}help"))
    # Send message to the debug channel signalling that the bot is ready
    await client.get_channel(817807544482922496).send("Running")
    # Start the listener
    await Utils.listener.start()


# Setup automatic logging for debugging
logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=logPath, encoding="utf-8", mode="a")
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s'))
logger.addHandler(handler)

# Load all extensions (filenames for the exterior cogs)
for extension in Utils.extensions:
    client.load_extension(extension)

# Start discord bot
client.run(Config.token)
