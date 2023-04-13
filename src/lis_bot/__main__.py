# Builtin
import logging
from pathlib import Path

# Pip
from discord import Status, Activity, ActivityType, Intents
from discord.ext import bridge

# Custom
from lis_bot.config import token
from lis_bot.helpers.utils.utils import extensions, restrictor

# Discord variables
bot = bridge.Bot(command_prefix="$", case_insensitive=True, intents=Intents().all())

# Path variables
logPath = Path(__file__).parent.joinpath("debug_files").joinpath("lisBot.log")


# Function which runs once the bot is set up and running
async def startup() -> None:
    await bot.wait_until_ready()

    # Set up the helper scripts
    await restrictor.setBot(bot)

    # Run the startup functions for each cog
    for cog in bot.cogs.values():
        await cog.startup()

    # Change the presence to show the help command
    await bot.change_presence(
        status=Status.online,
        activity=Activity(type=ActivityType.watching, name="Life is Strange"),
    )

    # Send message to the debug channel signalling that the bot is ready
    channel = await bot.fetch_channel(817807544482922496)
    await channel.send("Running")


# Setup automatic logging for debugging
logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=logPath, encoding="utf-8", mode="a")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(message)s"),
)
logger.addHandler(handler)

# Load all extensions (filenames for the exterior cogs)
for extension in extensions:
    bot.load_extension(extension)

# Start discord bot
bot.loop.create_task(startup())
bot.run(token)
