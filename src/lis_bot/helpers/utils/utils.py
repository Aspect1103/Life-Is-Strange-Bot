# Builtin
from pathlib import Path
from typing import Any

# Pip
import pendulum
from AO3.utils import HTTPError
from discord import Embed, Colour, Message
from discord.ext import commands, bridge

# Custom
from lis_bot.helpers.managers.database_manager import DatabaseManager
from lis_bot.helpers.utils.restrictor import Restrictor


# Function to split a list with a set amount of items in each
def listSplit(arr: list[Any], perListSize: int, listAmount: int) -> list[list[Any]]:
    result = []
    for i in range(listAmount):
        result.append(arr[i * perListSize : i * perListSize + perListSize])
    return result


# Function to sort a list of tuples based on a specific index
def rankSort(arr: list[tuple[int, ...]], indexToSort: int) -> list[tuple[int, ...]]:
    return sorted(arr, key=lambda x: x[indexToSort], reverse=True)


# Function to create an embed displaying the command error
async def commandDebugEmbed(
    ctx: bridge.BridgeApplicationContext | bridge.BridgeExtContext, message: str
) -> Message:
    return await ctx.respond(
        embed=Embed(
            title="Command Info", description=message, colour=Colour.from_rgb(0, 0, 0)
        )
    )


# Handle errors
async def errorHandler(
    ctx: bridge.BridgeApplicationContext | bridge.BridgeExtContext,
    error: commands.CommandError,
) -> None:
    if isinstance(error, commands.errors.MissingPermissions):
        await commandDebugEmbed(
            ctx, "You do not have sufficient permission to run this command"
        )
    elif isinstance(error, commands.errors.NotOwner):
        await commandDebugEmbed(ctx, "You are not owner")
    elif isinstance(error, commands.errors.CommandOnCooldown):
        await commandDebugEmbed(
            ctx,
            f"Command is on cooldown, try again in {round(error.retry_after, 2)} seconds",
        )
    elif isinstance(error, commands.errors.CheckFailure):
        result = await restrictor.grabAllowed(ctx)
        await commandDebugEmbed(ctx, result)
    elif isinstance(error.original, HTTPError):
        await commandDebugEmbed(ctx, error.original)

    # Write the error message
    open(errorPath, "a").write(f"{pendulum.now()}, {error.with_traceback()}\n")


# Path variables
rootDirectory = Path(__file__).parent.parent.parent
lisDatabasePath = (
    rootDirectory.joinpath("resources").joinpath("files").joinpath("lisBot.db")
)
errorPath = rootDirectory.joinpath("debug_files").joinpath("error.txt")

# Script variables
extensions = ["cogs.life_is_strange", "cogs.fanfic", "cogs.miscellaneous", "cogs.admin"]
database = DatabaseManager(lisDatabasePath)

# Restrictor class initialisation
commandGroups = {
    "life is strange": ["choices", "memory", "remasterMemory"],
    "trivia": ["trivia", "triviaLeaderboard", "triviaScore"],
    "fanfic": [
        "quote",
        "nextQuote",
        "searchQuote",
        "searchQuote start",
        "searchQuote add",
        "searchQuote remove",
        "outline",
        "works",
    ],
    "image": ["image"],
    "bot bidness": ["stop", "botRefresh", "channelRefresh", "about", "help"],
}
restrictor = Restrictor(commandGroups)

# Cooldown variables
superShort = 5
extraShort = 10
short = 20
medium = 45
long = 60
extraLong = 120
superLong = 300
