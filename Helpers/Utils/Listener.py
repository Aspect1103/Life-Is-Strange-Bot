# Builtin
import asyncio
import json
from pathlib import Path
from typing import List
# Pip
import pendulum
from discord import Colour, Embed
from discord.ext.commands import Bot
# Custom
from Helpers.Utils import Utils

# Path variables
rootDirectory = Path(__file__).parent.parent.parent
historyEventsPath = rootDirectory.joinpath("Resources").joinpath("Files").joinpath("historyEvents.json")


# Listener class to run specific events on startup
class Listener:
    # Initialise variables
    def __init__(self) -> None:
        self.historyEventsTable: List[List[str]] = json.loads(open(historyEventsPath, "r").read())
        self.colour = Colour.purple()
        self.bot = None

    # Function to set the bot variable
    def setBot(self, bot: Bot) -> None:
        self.bot = bot

    # Function which starts the various events
    async def start(self) -> None:
        await self.historyEvents()

    # Sends a message detailing a LiS event which happened on the same day
    async def historyEvents(self) -> None:
        # Get tomorrow's date so once midnight hits, the correct date can be checked
        tomorrowDate = pendulum.now().add(days=1)
        midnight: pendulum.DateTime = pendulum.DateTime(year=tomorrowDate.year, month=tomorrowDate.month, day=tomorrowDate.day, hour=23, minute=59, tzinfo=tomorrowDate.tzinfo)
        await asyncio.sleep(tomorrowDate.diff(midnight).in_seconds()+120)
        tomorrowEvent = [event for event in self.historyEventsTable if tomorrowDate.strftime("%d/%m") in event[1]]
        if len(tomorrowEvent) == 1:
            tomorrowDateString = pendulum.from_format(tomorrowEvent[0][1], "D/MM/YYYY").format("Do of MMMM YYYY")
            historyEmbed = Embed(title=f"Today on the {tomorrowDateString}, this happened:", description=tomorrowEvent[0][0], colour=self.colour)
            for value in Utils.restrictor.IDs["life is strange"].values():
                try:
                    # If the amount of allowed channels for a specific guild is larger than 1, then the first channel is used
                    await self.bot.get_channel(value[0]).send(embed=historyEmbed)
                except AttributeError:
                    # This is just for testing purposes
                    # Normally this will never run since the bot will be in every guild in IDs
                    # And if it isn't then the bot automatically removes those guilds from channelIDs.json
                    continue
