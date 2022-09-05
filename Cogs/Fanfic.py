# Builtin
import math
import random
from datetime import datetime
from pathlib import Path
from typing import Tuple, Union, List, Any
# Pip
import AO3
import gspread
from discord import Colour, Embed, Message, Cog, OptionChoice, SlashCommandGroup, option
from discord.ext import commands, bridge
# Custom
import Config
from Helpers.Managers.SearchQuoteManager import SearchQuoteManager
from Helpers.Utils import Utils
from Helpers.Utils.Paginator import Paginator

# Path variables
rootDirectory = Path(__file__).parent.parent
ignorePath = rootDirectory.joinpath("Resources").joinpath("Files").joinpath("ignoreFics.txt")

# # Grouped commands
# searchquote = SlashCommandGroup("searchquote", "Group command for searching for specific fics")


# Cog to manage fanfic commands
class Fanfic(Cog):
    # Initialise the bot
    def __init__(self, bot: bridge.Bot) -> None:
        self.bot = bot
        self.session = AO3.Session(Config.ao3Username, Config.ao3Password)
        self.colour = Colour.green()
        self.ignore = [line for line in open(ignorePath, "r").readlines()]
        self.quoteSearcher = None
        tempWorksheet = gspread.service_account_from_dict(Config.serviceAccount).open("Life Is Strange Read Fanfictions").worksheet("Life Is Strange Read Fanfictions").get_all_values()[2:]
        self.worksheetArray = tempWorksheet[:tempWorksheet.index([""]*11)]

    # Function to create quotes
    def quoteMaker(self, ficLink: str) -> Tuple[str, Union[AO3.Work, None], Union[str, None], Union[str, None]]:
        work = AO3.Work(AO3.utils.workid_from_url(ficLink), self.session)
        if work.title == "":
            # Work is secret
            return "", None, None, None
        quoteTries = 0
        while quoteTries < 5:
            quoteTries += 1
            randomChapter: AO3.Chapter = work.chapters[random.randrange(work.nchapters)]
            textList = list(filter(None, randomChapter.text.split("\n")))
            if len(textList) == 0:
                # Work has no words
                return "", None, None, None
            quote = random.choice(textList)
            if 10 <= len(quote.split()) <= 170:
                return quote, work, self.listConverter(work.authors, True), randomChapter.title
        # No quotes found
        return "", None, None, None

    # Function to convert a list
    def listConverter(self, lst: List[Any], author: bool = False) -> str:
        return ", ".join([item for item in lst]) if not author else ", ".join([author.username for author in lst])

    # Function to create embeds
    def quoteEmbedCreater(self, quote: str, work: AO3.Work, authors: str, chapterName: str) -> Embed:
        quoteEmbed = Embed(colour=self.colour)
        quoteEmbed.title = work.title
        quoteEmbed.url = work.url
        quoteEmbed.add_field(name=chapterName, value=quote)
        quoteEmbed.set_author(name=authors)
        return quoteEmbed

    # Function which runs once the bot is set up and running
    async def startup(self) -> None:
        # Create dictionary for each guild to hold the quote searcher
        self.quoteSearcher = {guild.id: None for guild in self.bot.guilds}

    # Function to find the last quote posted
    async def findLastQuote(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext], before: datetime = None, repeats: int = 0) -> Union[Message, None]:
        lastMessage = None
        repeats += 1
        async for message in ctx.channel.history(limit=100, before=before):
            lastMessage = message
            if message.author.id == self.bot.user.id:
                try:
                    if message.embeds[0].author.name != Embed.Empty and "https://archiveofourown.org" in message.embeds[0].url:
                        return message.embeds[0]
                except IndexError:
                    pass
        return None if repeats == 5 else await self.findLastQuote(ctx, lastMessage.created_at, repeats)

    # quote command with a cooldown of 1 use every 45 seconds per guild
    @bridge.bridge_command(description=f"Grabs a random quote from a LiS fic on AO3")
    @option("includensfw", str, description="Include NSFW or not", choices=[OptionChoice("Yes", "Yes"), OptionChoice("No", "No")], default="No")
    @commands.cooldown(1, Utils.medium, commands.BucketType.guild)
    async def quote(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext], includensfw: str = "No") -> None:
        if includensfw.capitalize() == "Yes":
            tempArr = [item for item in self.worksheetArray if item[7] == "Yes" or item[7] == "?"]
        else:
            tempArr = [item for item in self.worksheetArray if item[7] == "No"]
        quote = ""
        ficCount = 0
        while quote == "" and ficCount < 5:
            ficCount += 1
            quote, work, authors, chapterName = self.quoteMaker(tempArr.pop(random.randrange(len(tempArr)))[10])
        if quote == "":
            await Utils.commandDebugEmbed(ctx, "No valid quotes found")
        else:
            await ctx.respond(embed=self.quoteEmbedCreater(quote, work, authors, chapterName))

    # nextquote command with a cooldown of 1 use every 45 seconds per guild
    @bridge.bridge_command(aliases=["nq"], description=f"Finds the last quote posted and picks another quote from the same story")
    @commands.cooldown(1, Utils.medium, commands.BucketType.guild)
    async def nextquote(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext]) -> None:
        lastQuote = await self.findLastQuote(ctx)
        if lastQuote is None:
            await Utils.commandDebugEmbed(ctx, f"Cannot find the last quote. Try running {ctx.prefix}quote")
        else:
            quote, work, authors, chapterName = self.quoteMaker(lastQuote.url)
            # Make sure the quote isn't the same
            tries = 0
            while quote == lastQuote.fields[0].value and tries < 5:
                tries += 1
                quote, work, authors, chapterName = self.quoteMaker(lastQuote.url)
            if quote == lastQuote.fields[0].value:
                await Utils.commandDebugEmbed(ctx, "Cannot find any more quotes")
            else:
                await ctx.respond(embed=self.quoteEmbedCreater(quote, work, authors, chapterName))

    # # searchQuote start command with a cooldown of 1 use every 60 seconds per guild
    # @searchquote.command(description=f"Starts the quote searcher to search for specific fics (all NSFW fields are excluded by default)", cooldown=commands.CooldownMapping(commands.Cooldown(1, Utils.long), lambda x: x))
    # async def start(self, ctx: ApplicationContext) -> None:
    #     # Function to check a user's reaction
    #     def checker(reaction, user):
    #         return reaction.message.id == self.quoteSearcher[ctx.guild.id].message.id and user.id == self.quoteSearcher[ctx.guild.id].ctx.author.id and str(reaction) == "⏹️"
    #     # Initialise the SearchQuoteManager object
    #     message: Message = await ctx.channel.send(embed=Embed(title="Quote Searcher", description=f"No filters added. Use /searchQuote add to add a filter", colour=self.colour))
    #     self.quoteSearcher[ctx.guild.id] = SearchQuoteManager(self.bot, ctx, message, self.colour, self.worksheetArray)
    #     await message.add_reaction("⏹️")
    #     # Wait until the stop button is pressed with a timeout of 5 minutes
    #     while True:
    #         try:
    #             reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checker)
    #         except asyncio.TimeoutError:
    #             pass
    #         await message.clear_reactions()
    #         break
    #     # Remove nsfw works if no smut filter is added
    #     if self.quoteSearcher[ctx.guild.id].filters["smut"][1] is None:
    #         self.quoteSearcher[ctx.guild.id].finalArray = self.quoteSearcher[ctx.guild.id].filters["smut"][0]("No")
    #     # Pick a row
    #     tempArray: List[List[str]] = self.quoteSearcher[ctx.guild.id].finalArray
    #     if len(tempArray) == 0:
    #         await message.edit(embed=Embed(title="Quote Searcher", description="No matches found", colour=self.colour))
    #     elif len(tempArray) == 1:
    #         quote, work, authors, chapterName = self.quoteMaker(tempArray[0][10])
    #         if quote == "":
    #             await message.edit(embed=Embed(title="Quote Searcher", description="No matches found", colour=self.colour))
    #         else:
    #             await message.edit(embed=self.quoteEmbedCreater(quote, work, authors, chapterName))
    #     else:
    #         quote = ""
    #         while quote == "" and len(tempArray) > 0:
    #             quote, work, authors, chapterName = self.quoteMaker(tempArray.pop(random.randrange(len(tempArray)))[10])
    #             if quote != "":
    #                 await message.edit(embed=self.quoteEmbedCreater(quote, work, authors, chapterName))
    #                 break
    #         else:
    #             await message.edit(embed=Embed(title="Quote Searcher", description="No matches found", colour=self.colour))
    #     # Reset the quote searcher object so it can be reused
    #     self.quoteSearcher[ctx.guild.id] = None
    #
    # # searchQuote add command with a cooldown of 1 use every 5 seconds per guild
    # @searchquote.command(description=f"Add a filter to the quote searcher", cooldown=commands.CooldownMapping(commands.Cooldown(1, Utils.superShort), lambda x: x))
    # async def add(self, ctx: ApplicationContext, category: Option(str, description="The category to add", choices=[OptionChoice("Title", "title"), OptionChoice("Author", "author"), OptionChoice("Ship", "ship"), OptionChoice("Series", "series"), OptionChoice("Status", "status"), OptionChoice("Smut", "smut"), OptionChoice("Words", "words"), OptionChoice("Chapters", "chapters")]), term: Option(str, description="The term you want to filter for", default=None)) -> None:
    #     if self.quoteSearcher[ctx.guild.id] is None:
    #         await Utils.commandDebugEmbed(ctx.channel, f"Quote searcher not initialised. Run /searchQuote start to initialise it")
    #     else:
    #         if self.quoteSearcher[ctx.guild.id].ctx.author.id != ctx.author.id:
    #             await Utils.commandDebugEmbed(ctx.channel, f"Only {self.quoteSearcher[ctx.guild.id].ctx.author.mention} can add filters")
    #         else:
    #             await self.quoteSearcher[ctx.guild.id].addFilter(category, term)
    #
    # # searchQuote remove command with a cooldown of 1 use every 5 seconds per guild
    # @searchquote.command(description=f"Removes a filter from the quote searcher", cooldown=commands.CooldownMapping(commands.Cooldown(1, Utils.superShort), lambda x: x))
    # async def remove(self, ctx: ApplicationContext, category: Option(str, description="The category to remove", choices=[OptionChoice("Title", "title"), OptionChoice("Author", "author"), OptionChoice("Ship", "ship"), OptionChoice("Series", "series"), OptionChoice("Status", "status"), OptionChoice("Smut", "smut"), OptionChoice("Words", "words"), OptionChoice("Chapters", "chapters")])) -> None:
    #     if self.quoteSearcher[ctx.guild.id] is None:
    #         await Utils.commandDebugEmbed(ctx.channel, f"Quote searcher not initialised. Run /searchQuote start to initialise it")
    #     else:
    #         if self.quoteSearcher[ctx.guild.id].ctx.author.id != ctx.author.id:
    #             await Utils.commandDebugEmbed(ctx.channel, f"Only {self.quoteSearcher[ctx.guild.id].ctx.author.mention} can remove filters")
    #         else:
    #             await self.quoteSearcher[ctx.guild.id].removeFilter(category)

    # outline command with a cooldown of 1 use every 45 seconds per guild
    @bridge.bridge_command(description=f"Finds the last quote posted and displays the metadata for that fic")
    @commands.cooldown(1, Utils.medium, commands.BucketType.guild)
    async def outline(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext]) -> None:
        # Get the last quote posted and store its url
        lastQuote = await self.findLastQuote(ctx)
        if lastQuote is None:
            await Utils.commandDebugEmbed(ctx, f"Cannot find the last quote. Try running /quote")
        else:
            lastUrl: str = lastQuote.url
            print(lastUrl)
            # Create AO3 object then use it to create an info embed
            work = AO3.Work(AO3.utils.workid_from_url(lastUrl), self.session)
            infoEmbed = Embed(colour=self.colour)
            infoEmbed.title = work.title
            infoEmbed.url = work.url
            infoEmbed.set_author(name=self.listConverter(work.authors, True))
            infoEmbed.add_field(name="Rating:", value=work.rating)
            warnings = self.listConverter(work.warnings)
            if len(warnings) > 0:
                infoEmbed.add_field(name="Warnings:", value=warnings)
            categories = self.listConverter(work.categories)
            if len(categories) > 0:
                infoEmbed.add_field(name="Categories:", value=categories)
            fandoms = self.listConverter(work.fandoms)
            if len(fandoms) > 0:
                infoEmbed.add_field(name="Fandom:", value=fandoms)
            relationships = self.listConverter(work.relationships)
            if len(relationships) > 0:
                infoEmbed.add_field(name="Relationships:", value=relationships)
            characters = self.listConverter(work.characters)
            if len(characters) > 0:
                infoEmbed.add_field(name="Characters:", value=characters)
            tags = self.listConverter(work.tags)
            if len(relationships) > 0:
                infoEmbed.add_field(name="Additional Tags:", value=tags)
            infoEmbed.add_field(name="Summary:", value=work.summary)
            infoEmbed.set_footer(text=f"Words: {work.words}. Chapters: {work.nchapters}. Language: {work.language}")
            # Display the embed
            await ctx.respond(embed=infoEmbed)

    # works command with a cooldown of 1 use every 60 seconds per guild
    @bridge.bridge_command(description=f"Finds the last quote posted and displays all works posted by that author")
    @commands.cooldown(1, Utils.long, commands.BucketType.guild)
    async def works(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext]) -> None:
        # Get the last quote posted and create an AO3 User object
        lastQuote = await self.findLastQuote(ctx)
        if lastQuote is None:
            await Utils.commandDebugEmbed(ctx, f"Cannot find the last quote. Try running /quote")
        else:
            authorName: str = random.choice(lastQuote.author.name.split(", "))
            user = AO3.User(authorName, self.session)
            # If there are more than 5 pages of works, don't create embed
            pageLimit = 5
            if user.work_pages <= pageLimit:
                # Get all of their works (Note: Works aren't loaded)
                works: List[AO3.Work] = user.get_works(use_threading=True)
                workLimit = 5
                # If the amount of works is above workLimit, then create paginated menu
                if len(works) > workLimit:
                    # Split the list into set chunks
                    maxPage = math.ceil(len(works)/workLimit)
                    splitList = Utils.listSplit(works, workLimit, maxPage)
                    # Create embed objects for each page
                    pages = []
                    for count, arr in enumerate(splitList):
                        tempEmbed = Embed(colour=self.colour)
                        tempEmbed.title = authorName
                        tempEmbed.url = user.url
                        tempEmbed.set_footer(text=f"Page {count+1} of {maxPage}. Fic Total: {len(works)}")
                        for work in arr:
                            tempEmbed.add_field(name=work.title, value=work.url)
                        pages.append(tempEmbed)
                    # Create paginator
                    paginator = Paginator(ctx, self.bot)
                    paginator.addPages(pages)
                    await paginator.start()
                else:
                    # Create normal menu
                    pageEmbed = Embed(colour=self.colour)
                    pageEmbed.title = authorName
                    pageEmbed.url = user.url
                    for work in works:
                        pageEmbed.add_field(name=work.title, value=work.url)
                    await ctx.respond(embed=pageEmbed)
            else:
                await Utils.commandDebugEmbed(ctx, f"{authorName} has {user.works} works which is over the limit of {pageLimit * 20}")

    # Function to run channelCheck for Fanfic
    async def cog_check(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext]) -> bool:
        return await Utils.restrictor.commandCheck(ctx)

    # Catch any cog errors
    async def cog_command_error(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext], error: commands.CommandError) -> None:
        print(error)
        await Utils.errorHandler(ctx, error)


# Function which initialises the Fanfic cog
def setup(bot: bridge.Bot) -> None:
    bot.add_cog(Fanfic(bot))
    # bot.add_application_command(searchquote)
