# Builtin
import asyncio
from datetime import datetime
import math
import random
from pathlib import Path
from typing import Tuple, Union, List, Any, Optional
# Pip
import AO3
import gspread
from discord import Colour, Embed, Message
from discord.ext import commands
# Custom
import Config
from Helpers.Managers.SearchQuoteManager import SearchQuoteManager
from Helpers.Utils import Utils
from Helpers.Utils.Paginator import Paginator

# Path variables
rootDirectory = Path(__file__).parent.parent
ignorePath = rootDirectory.joinpath("Resources").joinpath("Files").joinpath("ignoreFics.txt")


# Cog to manage fanfic commands
class Fanfic(commands.Cog):
    # Initialise the bot
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.session = AO3.Session(Config.ao3Username, Config.ao3Password)
        self.colour = Colour.green()
        self.ignore = []
        self.worksheetArray = None
        self.quoteSearcher = None
        self.fanficInit()
        self.bot.loop.create_task(self.startup())

    # Function to initialise fanfic variables
    def fanficInit(self) -> None:
        # Creates the formatted 2D array for the google spreadsheet
        serviceAccount = gspread.service_account_from_dict(Config.serviceAccount)
        worksheet = serviceAccount.open("Life Is Strange Read Fanfictions").worksheet("Life Is Strange Read Fanfictions").get_all_values()[2:]
        emptyRow = 0
        for row in range(len(worksheet)):
            if worksheet[row][10] == "":
                emptyRow = row
                break
        self.worksheetArray = worksheet[:emptyRow]

        # Assign the IDs which are to be ignored to the ignore list
        self.ignore = [line for line in open(ignorePath, "r").readlines()]

    # Function to create quotes
    def quoteMaker(self, ficLink: str) -> Tuple[str, Union[AO3.Work, None], Union[str, None], Union[str, None]]:
        work = AO3.Work(AO3.utils.workid_from_url(ficLink), self.session)
        if work.title == "":
            # Work is secret
            return "", None, None, None
        quoteTries = 0
        while quoteTries < 5:
            quoteTries += 1
            randomChapter = work.chapters[random.randrange(work.nchapters)]
            textList = list(filter(None, randomChapter.text.split("\n")))
            if len(textList) == 0:
                # Work has no words
                return "", None, None, None
            quote = random.choice(textList)
            if len(quote.split()) >= 10 and len(quote.split()) <= 170:
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

    # Function to find the last quote posted
    async def findLastQuote(self, ctx: commands.Context, before: datetime = None, repeats: int = 0) -> Union[Message, None]:
        lastMessage = None
        repeats += 1
        async for message in ctx.channel.history(limit=100, before=before):
            lastMessage = message
            if message.author.id == self.bot.user.id:
                try:
                    if message.embeds[0].author.name != Embed.Empty:
                        return message.embeds[0]
                except IndexError:
                    pass
        return None if repeats == 5 else await self.findLastQuote(ctx, lastMessage.created_at, repeats)

    # Function which runs once the bot is setup and running
    async def startup(self) -> None:
        await self.bot.wait_until_ready()
        # Create dictionary for each guild to hold the quote searcher
        self.quoteSearcher = {guild.id: None for guild in self.bot.guilds}

    # quote command with a cooldown of 1 use every 45 seconds per guild
    @commands.command(help=f"Grabs a random quote from a LiS fic on AO3. By default, it will only search non-NSFW fics which can be changed through the includeNSFW argument. It has a cooldown of {Utils.medium} seconds", description="\nArguments:\nIncludeNSFW - Yes/No (doesn't have to be capitalised). This argument is optional as not including it will default to 'No'", usage="quote [includeNSFW]", brief="Fanfic")
    @commands.cooldown(1, Utils.medium, commands.BucketType.guild)
    async def quote(self, ctx: commands.Context, includeNsfw: Optional[str] = "No") -> None:
        if includeNsfw.capitalize() == "Yes":
            tempArr = [item for item in self.worksheetArray if item[7] == "Yes" or item[7] == "?"]
        else:
            tempArr = [item for item in self.worksheetArray if item[7] == "No"]
        quote = ""
        ficCount = 0
        while quote == "" and ficCount < 5:
            ficCount += 1
            quote, work, authors, chapterName = self.quoteMaker(tempArr.pop(random.randrange(len(tempArr)))[10])
        if quote == "":
            await Utils.commandDebugEmbed(ctx.channel, "No valid quotes found")
        else:
            await ctx.channel.send(embed=self.quoteEmbedCreater(quote, work, authors, chapterName))

    # nextQuote command with a cooldown of 1 use every 45 seconds per guild
    @commands.command(aliases=["nq"], help=f"Finds the last quote posted and picks another quote from the same story. It has a cooldown of {Utils.medium} seconds", usage="nextQuote|nq", brief="Fanfic")
    @commands.cooldown(1, Utils.medium, commands.BucketType.guild)
    async def nextQuote(self, ctx: commands.Context) -> None:
        lastQuote = await self.findLastQuote(ctx)
        if lastQuote is None:
            await Utils.commandDebugEmbed(ctx.channel, f"Cannot find the last quote. Try running {ctx.prefix}quote")
        else:
            quote, work, authors, chapterName = self.quoteMaker(lastQuote.url)
            # Make sure the quote isn't the same
            tries = 0
            while quote == lastQuote.fields[0].value and tries < 5:
                tries += 1
                quote, work, authors, chapterName = self.quoteMaker(lastQuote.url)
            if quote == lastQuote.fields[0].value:
                await Utils.commandDebugEmbed(ctx.channel, "Cannot find any more quotes")
            else:
                await ctx.channel.send(embed=self.quoteEmbedCreater(quote, work, authors, chapterName))

    # Base function to initialise the searchQuote group commands with a cooldown of 5 seconds
    @commands.group(invoke_without_command=True, aliases=["sq"], help=f"Group command for searching for specific fics. This command has subcommands. It has a cooldown of {Utils.superShort} seconds", usage="searchQuote|sq", brief="Fanfic")
    @commands.cooldown(1, Utils.superShort, commands.BucketType.guild)
    async def searchQuote(self, ctx: commands.Context) -> None:
       await ctx.send_help(ctx.command)

    # searchQuote start command with a cooldown of 1 use every 60 seconds per guild
    @searchQuote.command(help=f"Starts the quote searcher to search for specific fics. If no filter is added for the 'smut' field, all NSFW fics will be excluded. It has a cooldown of {Utils.long} seconds", usage="searchQuote|sq start", brief="Fanfic")
    @commands.cooldown(1, Utils.long, commands.BucketType.guild)
    async def start(self, ctx: commands.Context) -> None:
        # Function to check a user's reaction
        def checker(reaction, user):
            return reaction.message.id == self.quoteSearcher[ctx.guild.id].message.id and user.id == self.quoteSearcher[ctx.guild.id].ctx.author.id and str(reaction) == "⏹️"
        # Initialise the SearchQuoteManager object
        message = await ctx.channel.send(embed=Embed(title="Quote Searcher", description=f"No filters added. Use {ctx.prefix}searchQuote add to add a filter", colour=self.colour))
        self.quoteSearcher[ctx.guild.id] = SearchQuoteManager(self.bot, ctx, message, self.colour, self.worksheetArray)
        await message.add_reaction("⏹️")
        # Wait until the stop button is pressed with a timeout of 5 minutes
        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=300, check=checker)
            except asyncio.TimeoutError:
                pass
            await message.clear_reactions()
            break
        # Remove nsfw works if no smut filter is added
        if self.quoteSearcher[ctx.guild.id].filters["smut"][1] is None:
            self.quoteSearcher[ctx.guild.id].finalArray = self.quoteSearcher[ctx.guild.id].filters["smut"][0]("No")
        # Pick a row
        tempArray = self.quoteSearcher[ctx.guild.id].finalArray
        if len(tempArray) == 0:
            await message.edit(embed=Embed(title="Quote Searcher", description="No matches found", colour=self.colour))
        elif len(tempArray) == 1:
            quote, work, authors, chapterName = self.quoteMaker(tempArray[0][10])
            if quote == "":
                await message.edit(embed=Embed(title="Quote Searcher", description="No matches found", colour=self.colour))
            else:
                await message.edit(embed=self.quoteEmbedCreater(quote, work, authors, chapterName))
        else:
            quote = ""
            while quote == "" and len(tempArray) > 0:
                quote, work, authors, chapterName = self.quoteMaker(tempArray.pop(random.randrange(len(tempArray)))[10])
                if quote != "":
                    await message.edit(embed=self.quoteEmbedCreater(quote, work, authors, chapterName))
                    break
            else:
                await message.edit(embed=Embed(title="Quote Searcher", description="No matches found", colour=self.colour))
        # Reset the quote searcher object so it can be reused
        self.quoteSearcher[ctx.guild.id] = None

    # searchQuote add command with a cooldown of 1 use every 5 seconds per guild
    @searchQuote.command(help=f"Add a filter to the quote searcher. It has a cooldown of {Utils.superShort} seconds", description="\nArguments:\nCategory - The category which you want to add a filter for. They are as follows:\n> Title - Result contains this term\n> Author - Result contains this term\n> Ship - Result matches this term\n> Series - Result contains this term\n> Status - Result matches this term. Can either be 'Completed', 'In progress' or 'Abandoned'\n> Smut - Result matches this term. Can either be 'Yes', 'No' or '?'\n> Words - Result matches this term. Use '>' (greater than), '<' (less than), '>=' (greater than or equal to), '<=' (less than or equal to), '==' (equal to), '!=' (not equal to) or '-' (for a range)\n> Chapters - Result matches this term. Use '>' (greater than), '<' (less than), '>=' (greater than or equal to), '<=' (less than or equal to), '==' (equal to), '!=' (not equal to) or '-' (for a range)\nTerm - The term you want to filter for", usage="searchQuote|sq add <category> <term>", brief="Fanfic")
    @commands.cooldown(1, Utils.superShort, commands.BucketType.guild)
    async def add(self, ctx: commands.Context, category: str = None, term: str = None) -> None:
        if self.quoteSearcher[ctx.guild.id] is None:
            await Utils.commandDebugEmbed(ctx.channel, f"Quote searcher not initialised. Run {ctx.prefix}searchQuote|sq start to initialise it")
        else:
            if self.quoteSearcher[ctx.guild.id].ctx.author.id != ctx.author.id:
                await Utils.commandDebugEmbed(ctx.channel, f"Only {self.quoteSearcher[ctx.guild.id].ctx.author.mention} can add filters")
            else:
                await self.quoteSearcher[ctx.guild.id].addFilter(category, term)

    # searchQuote remove command with a cooldown of 1 use every 5 seconds per guild
    @searchQuote.command(help=f"Removes a filter from the quote searcher. It has a cooldown of {Utils.superShort} seconds", description="\nArguments:\nCategory - The category which you want to add a filter for. They are as follows:\n> Title - Result contains this term\n> Author - Result contains this term\n> Ship - Result matches this term\n> Series - Result contains this term\n> Status - Result matches this term. Can either be 'Completed', 'In progress' or 'Abandoned'\n> Smut - Result matches this term. Can either be 'Yes', 'No' or '?'\n> Words - Result matches this term. Use '>' (greater than), '<' (less than), '>=' (greater than or equal to), '<=' (less than or equal to), '==' (equal to), '!=' (not equal to) or '-' (for a range)\n> Chapters - Result matches this term. Use '>' (greater than), '<' (less than), '>=' (greater than or equal to), '<=' (less than or equal to), '==' (equal to), '!=' (not equal to) or '-' (for a range)", usage="searchQuote|sq remove <category>", brief="Fanfic")
    @commands.cooldown(1, Utils.superShort, commands.BucketType.guild)
    async def remove(self, ctx: commands.Context, category: str = None) -> None:
        if self.quoteSearcher[ctx.guild.id] is None:
            await Utils.commandDebugEmbed(ctx.channel, f"Quote searcher not initialised. Run {ctx.prefix}searchQuote|sq start to initialise it")
        else:
            if self.quoteSearcher[ctx.guild.id].ctx.author.id != ctx.author.id:
                await Utils.commandDebugEmbed(ctx.channel, f"Only {self.quoteSearcher[ctx.guild.id].ctx.author.mention} can remove filters")
            else:
                await self.quoteSearcher[ctx.guild.id].removeFilter(category)

    # outline command with a cooldown of 1 use every 45 seconds per guild
    @commands.command(help=f"Finds the last quote posted and displays the metadata for that fic. It has a cooldown of {Utils.medium} seconds", usage="outline", brief="Fanfic")
    @commands.cooldown(1, Utils.medium, commands.BucketType.guild)
    async def outline(self, ctx: commands.Context) -> None:
        # Get the last quote posted and store its url
        lastQuote = await self.findLastQuote(ctx)
        if lastQuote is None:
            await Utils.commandDebugEmbed(ctx.channel, f"Cannot find the last quote. Try running {ctx.prefix}quote")
        else:
            lastUrl = lastQuote.url
            # Create AO3 object then use it to create an info embed
            work = AO3.Work(AO3.utils.workid_from_url(lastUrl), self.session)
            infoEmbed = Embed(colour=self.colour)
            infoEmbed.title = work.title
            infoEmbed.url = work.url
            infoEmbed.set_author(name=self.listConverter(work.authors, True))
            infoEmbed.add_field(name="Rating:", value=work.rating)
            warnings = self.listConverter(work.warnings)
            if warnings != None:
                infoEmbed.add_field(name="Warnings:", value=warnings)
            categories = self.listConverter(work.categories)
            if categories != None:
                infoEmbed.add_field(name="Categories:", value=categories)
            fandoms = self.listConverter(work.fandoms)
            if fandoms == None:
                infoEmbed.add_field(name="Fandom:", value=fandoms)
            relationships = self.listConverter(work.relationships)
            if relationships != None:
                infoEmbed.add_field(name="Relationships:", value=relationships)
            characters = self.listConverter(work.characters)
            if characters != None:
                infoEmbed.add_field(name="Characters:", value=characters)
            tags = self.listConverter(work.tags)
            if tags != None:
                infoEmbed.add_field(name="Additional Tags:", value=tags)
            infoEmbed.add_field(name="Summary:", value=work.summary)
            infoEmbed.set_footer(text=f"Words: {work.words}. Chapters: {work.nchapters}. Language: {work.language}")
            # Display the embed
            await ctx.channel.send(embed=infoEmbed)

    # works command with a cooldown of 1 use every 60 seconds per guild
    @commands.command(help=f"Finds the last quote posted and displays all works posted by that author. It has a cooldown of {Utils.long} seconds", usage="works", brief="Fanfic")
    @commands.cooldown(1, Utils.long, commands.BucketType.guild)
    async def works(self, ctx: commands.Context) -> None:
        # Get the last quote posted and create an AO3 User object
        lastQuote = await self.findLastQuote(ctx)
        if lastQuote is None:
            await Utils.commandDebugEmbed(ctx.channel, f"Cannot find the last quote. Try running {ctx.prefix}quote")
        else:
            authorName = lastQuote.author.name
            user = AO3.User(authorName, self.session)
            # If there are more than 5 pages of works, don't create embed
            pageLimit = 5
            if user.work_pages <= pageLimit:
                # Get all of their works (Note: Works aren't loaded)
                works = user.get_works(use_threading=True)
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
                    await ctx.channel.send(embed=pageEmbed)
            else:
                await Utils.commandDebugEmbed(ctx.channel, f"{authorName} has {user.works} works which is over the limit of {pageLimit * 20}")

    # Function to run channelCheck for Fanfic
    async def cog_check(self, ctx: commands.Context) -> bool:
        return await Utils.restrictor.commandCheck(ctx)

    # Catch any cog errors
    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        await Utils.errorHandler(ctx, error)


# Function which initialises the Fanfic cog
def setup(bot: commands.Bot) -> None:
    bot.add_cog(Fanfic(bot))
