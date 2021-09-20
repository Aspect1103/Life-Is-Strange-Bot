# Builtin
import asyncio
import json
from pathlib import Path
# Pip
import asyncpraw
import pendulum
from discord import Colour, Embed
from discord.ext import tasks
from discord.ext.commands import Bot
# Custom
import Config
from Helpers.Utils import Utils

# Path variables
rootDirectory = Path(__file__).parent.parent.parent
historyEventsPath = rootDirectory.joinpath("Resources").joinpath("Files").joinpath("historyEvents.json")


# Tasks class to run specific events on startup
class Tasks:
    # Initialise variables
    def __init__(self) -> None:
        self.colour = Colour.purple()
        self.historyEventsTable = json.loads(open(historyEventsPath, "r").read())
        self.redditClient = asyncpraw.Reddit(
            client_id=Config.redditID,
            client_secret=Config.redditSecret,
            user_agent="linux:LiSBot:1.0 (by u/JackAshwell1)"
        )
        self.bot = None
        self.posts = None

    # Function which runs once the bot is setup and running
    async def startup(self, bot: Bot) -> None:
        self.bot = bot
        self.posts = {guild.id: [] for guild in self.bot.guilds}

    # Function which starts the various events
    async def start(self) -> None:
        self.redditPoster.start()
        await self.historyEvents()

    # Function which sends a message linking the top post from r/lifeisstrange
    @tasks.loop(hours=3)
    async def redditPoster(self) -> None:
        subreddit = await self.redditClient.subreddit("lifeisstrange")
        for guild in self.bot.guilds:
            # Grab top 100 posts from the last week
            async for submission in subreddit.top("week"):
                if submission.id not in self.posts[guild.id]:
                    # Submission is not posted to the discord channel yet so create an embed
                    self.posts[guild.id].append(submission.id)
                    await submission.author.load()
                    postEmbed = Embed(title=submission.title, url=f"https://www.reddit.com{submission.permalink}", colour=self.colour)
                    postEmbed.set_image(url=submission.url)
                    postEmbed.set_author(name=submission.author.name, url=f"https://www.reddit.com/user/{submission.author.name}", icon_url=submission.author.icon_img)
                    await self.sendEmbed(postEmbed)
                    break

    # Function which sends a message detailing a LiS event which happened on the same day
    async def historyEvents(self) -> None:
        # Get tomorrow's date so once midnight hits, the correct date can be checked
        tomorrowDate = pendulum.now().add(days=1)
        midnight: pendulum.DateTime = pendulum.DateTime(year=tomorrowDate.year, month=tomorrowDate.month, day=tomorrowDate.day, hour=23, minute=59, tzinfo=tomorrowDate.tzinfo)
        await asyncio.sleep(tomorrowDate.diff(midnight).in_seconds()+120)
        tomorrowEvent = [event for event in self.historyEventsTable if tomorrowDate.strftime("%d/%m") in event[1]]
        if len(tomorrowEvent) == 1:
            tomorrowDateString = pendulum.from_format(tomorrowEvent[0][1], "D/MM/YYYY").format("Do of MMMM YYYY")
            await self.sendEmbed(Embed(title=f"Today on the {tomorrowDateString}, this happened:", description=tomorrowEvent[0][0], colour=self.colour))

    # Function to send an embed to designated channel
    async def sendEmbed(self, embed):
        for value in Utils.restrictor.IDs["life is strange"].values():
            try:
                # If the amount of allowed channels for a specific guild is larger than 1, then the first channel is used
                await self.bot.get_channel(value[0]).send(embed=embed)
            except AttributeError:
                # This is just for testing purposes
                # Normally this will never run since the bot will be in every guild in IDs
                # And if it isn't then the bot automatically removes those guilds from channelIDs.json
                continue
