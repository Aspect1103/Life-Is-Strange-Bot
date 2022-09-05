# Builtin
import logging
from pathlib import Path

# Pip
from discord import Status, Activity, ActivityType, Intents
from discord.ext import bridge

# Custom
import Config
from Helpers.Utils import Utils

# Discord variables
intents = Intents().default()
intents.members = True
intents.message_content = True
bot = bridge.Bot(command_prefix="$", case_insensitive=True, intents=intents)

# Path variables
rootDirectory = Path(__file__).parent
logPath = rootDirectory.joinpath("DebugFiles").joinpath("lisBot.log")


# Function which runs once the bot is set up and running
async def startup() -> None:
    await bot.wait_until_ready()
    # Set up the helper scripts
    await Utils.restrictor.setBot(bot)
    await Utils.tasks.startup(bot)
    # Run the startup functions for each cog
    for cog in bot.cogs.values():
        await cog.startup()
    # Change the presence to show the help command
    await bot.change_presence(status=Status.online, activity=Activity(type=ActivityType.watching, name="Life is Strange"))
    # Send message to the debug channel signalling that the bot is ready
    channel = await bot.fetch_channel(817807544482922496)
    await channel.send("Running")
    # Start the listener
    await Utils.tasks.start()


# Setup automatic logging for debugging
logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=logPath, encoding="utf-8", mode="a")
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s'))
logger.addHandler(handler)

# Load all extensions (filenames for the exterior cogs)
for extension in Utils.extensions:
    bot.load_extension(extension)

# Start discord bot
bot.loop.create_task(startup())
bot.run(Config.token)
