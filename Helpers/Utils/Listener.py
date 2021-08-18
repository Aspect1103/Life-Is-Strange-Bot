# Builtin
from pathlib import Path
import asyncio
import json
# Pip
from discord import Client
from discord import Colour
from discord import Embed
import pendulum
# Custom
from Helpers.Utils import Utils

# Path variables
rootDirectory = Path(__file__).parent.parent.parent
historyEventsPath = rootDirectory.joinpath("Resources").joinpath("Files").joinpath("historyEvents.json")


# Listener class to run specific events on startup
class Listener:
    # Initialise variables
    def __init__(self):
        self.historyEventsTable = json.loads(open(historyEventsPath, "r").read())
        self.colour = Colour.from_rgb(255, 192, 203)
        self.client = None

    # Function to set the client variables
    def setClient(self, client: Client):
        self.client = client

    # Function which starts the various events
    async def start(self):
        await self.historyEvents()

    # Sends a message detailing a LiS event which happened on the same day
    async def historyEvents(self):
        # Get tomorrow's date so once midnight hits, the correct date can be checked
        tomorrowDate = pendulum.now().add(days=1)
        midnight = pendulum.DateTime(year=tomorrowDate.year, month=tomorrowDate.month, day=tomorrowDate.day, hour=23, minute=59, tzinfo=tomorrowDate.tzinfo)
        await asyncio.sleep(tomorrowDate.diff(midnight).in_seconds()+120)
        tomorrowEvent = [event for event in self.historyEventsTable if tomorrowDate.strftime("%d/%m") in event[1]]
        if len(tomorrowEvent) == 1:
            tomorrowDateString = pendulum.from_format(tomorrowEvent[0][1], "D/MM/YYYY").format("Do of MMMM YYYY")
            historyEmbed = Embed(title=f"Today on the {tomorrowDateString}, this happened:", description=tomorrowEvent[0][0], colour=self.colour)
            for value in Utils.restrictor.IDs["life is strange"].values():
                try:
                    # If the amount of allowed channels for a specific guild is larger than 1, then the first channel is used
                    await self.client.get_channel(value[0]).send(embed=historyEmbed)
                except AttributeError:
                    # This is just for testing purposes
                    # Normally this will never run since the bot will be in every guild in IDs
                    # And if it isn't then the bot automatically removes those guilds from channelIDs.json
                    continue
