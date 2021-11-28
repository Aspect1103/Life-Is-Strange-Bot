# Builtin
import json
from pathlib import Path
from typing import List, Dict, Any, Union, Tuple
# Pip
import pendulum
from AO3.utils import HTTPError
from discord import TextChannel, Embed, Colour, Message
from discord.ext import commands
# Custom
from Helpers.Managers.DatabaseManager import DatabaseManager
from .Tasks import Tasks
from .Restrictor import Restrictor


# Function to write messages to error.txt
def errorWrite(error: Union[commands.CommandError, str]) -> None:
    open(errorPath, "a").write(f"{pendulum.now()}, {error}\n")


# Function to split a list with a set amount of items in each
def listSplit(arr: List[Any], perListSize: int, listAmount: int) -> List[List[Any]]:
    result = []
    for i in range(listAmount):
        result.append(arr[i * perListSize:i * perListSize + perListSize])
    return result


# Function to sort a list of tuples based on a specific index
def rankSort(arr: List[Tuple[int, ...]], indexToSort: int) -> List[Tuple[int, ...]]:
    return sorted(arr, key=lambda x: x[indexToSort], reverse=True)


# Function to create an embed displaying the command error
async def commandDebugEmbed(channel: TextChannel, message: str) -> Message:
    return await channel.send(embed=Embed(title="Command Info", description=message, colour=Colour.from_rgb(0, 0, 0)))


# Handle errors
async def errorHandler(ctx: commands.Context, error: commands.CommandError) -> None:
    if isinstance(error, commands.errors.MissingPermissions):
        await commandDebugEmbed(ctx.channel, "You do not have sufficient permission to run this command")
    elif isinstance(error, commands.errors.NotOwner):
        await commandDebugEmbed(ctx.channel, "You are not owner")
    elif isinstance(error, commands.errors.CommandOnCooldown):
        await commandDebugEmbed(ctx.channel, f"Command is on cooldown, try again in {round(error.retry_after, 2)} seconds")
    elif isinstance(error, commands.errors.CheckFailure):
        result = await restrictor.grabAllowed(ctx)
        await commandDebugEmbed(ctx.channel, result)
    elif isinstance(error.original, HTTPError):
        await commandDebugEmbed(ctx.channel, error.original)
    errorWrite(error)


# Path variables
rootDirectory = Path(__file__).parent.parent.parent
lisDatabasePath = rootDirectory.joinpath("Resources").joinpath("Files").joinpath("lisBot.db")
errorPath = rootDirectory.joinpath("DebugFiles").joinpath("error.txt")

# Script variables
extensions = ["Cogs.Life Is Strange", "Cogs.Fanfic", "Cogs.Radio", "Cogs.Miscellaneous", "Cogs.Admin"]
database = DatabaseManager(lisDatabasePath)
tasks = Tasks()

# Restrictor class initialisation
commandGroups = {
    "life is strange": ["choices", "memory"],
    "trivia": ["trivia", "triviaLeaderboard", "triviaScore"],
    "fanfic": ["quote", "nextQuote", "searchQuote", "searchQuote start", "searchQuote add", "searchQuote remove", "outline", "works"],
    "image": ["image"],
    "radio": ["connect"],
    "bot bidness": ["stop", "botRefresh", "channelRefresh", "about", "help"]
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
