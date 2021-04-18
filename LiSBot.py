# Import libraries
from discord.ext import commands
from discord import Game
from discord import Status
import logging
import os

# Initialise discord variables
token = "default"  # Default token
#token = "test"  # Test token
client = commands.Bot(command_prefix=["s?", "S?"], description="A LiS Discord Bot")

# Path variables
rootDirectory = os.path.join(os.path.dirname(__file__))
logPath = os.path.join(rootDirectory, "BotFiles", "lisBot.log")


# Run when discord bot has started
@client.event
async def on_ready():
    # Get channel ID for test channel
    channel = client.get_channel(817807544482922496)
    # Change the presence to show the help command
    await client.change_presence(status=Status.online, activity=Game(name="s?help"))
    # Send message to user signalling that the bot is ready
    await channel.send("Running")


# Setup automatic logging for debugging
logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=logPath, encoding="utf-8", mode="a")
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s'))
logger.addHandler(handler)

# Load all extensions (filenames for the exterior cogs)
extensions = [
    "Cogs.Admin",
    "Cogs.Fanfic",
    "Cogs.Images",
    "Cogs.Other",
    "Cogs.Trivia"
]
for extension in extensions:
    client.load_extension(extension)

# Start discord bot
client.run(token)