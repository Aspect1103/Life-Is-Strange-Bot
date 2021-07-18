# Builtin
import asyncio
import os
import random
import math
# Pip
from discord.ext import commands
from discord import Embed
from discord import Colour
import gspread
import AO3
# Custom
from Utils.SearchQuoteManager import SearchQuoteManager
from Utils.Paginator import Paginator
from Utils import Utils
import Config

# Path variables
rootDirectory = os.path.join(os.path.dirname(__file__), os.pardir)
ignorePath = os.path.join(rootDirectory, "Resources", "ignoreFics.txt")


# Cog to manage fanfic commands
class Fanfic(commands.Cog):
    # Initialise the client
    def __init__(self, client):
        self.client = client
        self.session = AO3.Session(Config.ao3Username, Config.ao3Password)
        self.colour = Colour.green()
        self.ignore = []
        self.worksheetArray = None
        self.quoteSearcher = None
        self.fanficInit()

    # Function to initialise fanfic variables
    def fanficInit(self):
        # Creates the formatted 2D array for the google spreadsheet
        serviceAccountPath = os.path.join(rootDirectory, "BotFiles", "service_account_secret.json")
        serviceAccount = gspread.service_account(filename=serviceAccountPath)
        worksheet = serviceAccount.open("Life Is Strange Read Fanfictions").worksheet(
            "Life Is Strange Read Fanfictions").get_all_values()
        worksheet = worksheet[2:]
        emptyRow = 0
        for row in range(len(worksheet)):
            if worksheet[row][10] == "":
                emptyRow = row
                break
        self.worksheetArray = worksheet[:emptyRow]

        # Assign the IDs which are to be ignored to the ignore list
        self.ignore = [line for line in open(ignorePath, "r").readlines()]

    # Function to make random quotes
    def quoteMaker(self, link):
        # Create work object
        work = AO3.Work(AO3.utils.workid_from_url(link), self.session)
        if str(work.id) in self.ignore:
            # Work is ignored
            return "", None, None, None
        # Repeat until a good quote is found
        quote = ""
        retries = 10
        # Set to 170 because embed description limit is 1024 (1024/6)=170.66666 words max
        while (len(quote.split()) < 10 or len(quote.split()) > 170) and retries > 0:
            retries -= 1
            # Get a random chapter's text
            randomChapter = work.chapters[random.randint(0, work.nchapters)-1]
            randomChapterText = randomChapter.text
            # Format the text
            textList = list(filter(None, randomChapterText.split("\n")))
            if len(textList) == 0:
                # Work has no words
                return "", None, None, None
            # Create the quote
            quote = textList[random.randint(0, len(textList)-1)]
            # Grab the authors
            authors = self.listConverter(work.authors, True)
        if retries == 0:
            # No quote can be found
            return "", None, None, None
        # Return final values
        return quote, work, authors, randomChapter.title

    # Function to create embeds
    def quoteEmbedCreater(self, quote, work, authors, chapterName):
        quoteEmbed = Embed(colour=self.colour)
        quoteEmbed.title = work.title
        quoteEmbed.url = work.url
        quoteEmbed.add_field(name=chapterName, value=quote)
        quoteEmbed.set_author(name=authors)
        return quoteEmbed

    # Function to convert a list of objects into a string
    def listConverter(self, arr, author=False):
        if len(arr) == 0:
            return None
        elif len(arr) == 1:
            if author:
                return arr[0].username
            return arr[0]
        else:
            if author:
                return ", ".join([element.username for element in arr])
            return ", ".join(arr)

    # Function to split a list with a set amount of items in each
    def listSplit(self, arr, perListSize, listAmmount):
        result = []
        for i in range(listAmmount):
            result.append(arr[i * perListSize:i * perListSize + perListSize])
        return result

    # Function to find the last quote posted
    async def findLastQuote(self, ctx, before=None, repeats=0):
        lastMessage = None
        repeats += 1
        async for message in ctx.channel.history(limit=100, before=before):
            lastMessage = message
            if message.author.id == self.client.user.id:
                try:
                    if message.embeds[0].author.name != Embed.Empty:
                        return message.embeds[0]
                except IndexError:
                    pass
        return None if repeats == 5 else await self.findLastQuote(ctx, lastMessage.created_at, repeats)

    # quote command with a cooldown of 1 use every 45 seconds per guild
    @commands.command(help=f"Grabs a random quote from a LiS fic on AO3. It has a cooldown of {Utils.medium} seconds", usage="quote", brief="Fanfic")
    @commands.cooldown(1, Utils.medium, commands.BucketType.guild)
    async def quote(self, ctx):
        # Grab a random fic link
        randomLink = self.worksheetArray[random.randint(0, len(self.worksheetArray)-1)][10]
        # Get quote
        quote, work, authors, chapterName = self.quoteMaker(randomLink)
        while quote == "":
            # Redo the grab
            randomLink = self.worksheetArray[random.randint(0, len(self.worksheetArray) - 1)][10]
            quote, work, authors, chapterName = self.quoteMaker(randomLink)
        # Create embed and send it
        await ctx.channel.send(embed=self.quoteEmbedCreater(quote, work, authors, chapterName))

    # nextQuote command with a cooldown of 1 use every 45 seconds per guild
    @commands.command(aliases=["nq"], help=f"Finds the last quote posted and picks another quote from the same story. It has a cooldown of {Utils.medium} seconds", usage="nextQuote|nq", brief="Fanfic")
    @commands.cooldown(1, Utils.medium, commands.BucketType.guild)
    async def nextQuote(self, ctx):
        # Get the last quote posted then get a new one
        lastQuote = await self.findLastQuote(ctx)
        if lastQuote is None:
            await ctx.channel.send(f"Cannot find the last quote. Try running {ctx.prefix}quote")
        else:
            lastUrl = lastQuote.url
            quote, work, authors, chapterName = self.quoteMaker(lastUrl)
            # Make sure the quote isn't the same
            retries = 3
            while quote == lastQuote.fields[0].value and retries > 0:
                retries -= 1
                quote, work, authors, chapterName = self.quoteMaker(lastUrl)
            if retries != 0:
                await ctx.channel.send(embed=self.quoteEmbedCreater(quote, work, authors, chapterName))
            else:
                # No more valid quotes found
                await ctx.channel.send("Cannot find any more quotes")

    # Base function to initialise the searchQuote group commands with a cooldown of 5 seconds
    @commands.group(invoke_without_command=True, aliases=["sq"], help=f"Group command for searching for specific fics. This command has subcommands. It has a cooldown of {Utils.superShort} seconds", usage="searchQuote|sq", brief="Fanfic")
    @commands.cooldown(1, Utils.superShort, commands.BucketType.guild)
    async def searchQuote(self, ctx):
       await ctx.send_help(ctx.command)

    # searchQuote start command with a cooldown of 1 use every 60 seconds per guild
    @searchQuote.command(help=f"Starts the quote searcher to search for specific fics. It has a cooldown of {Utils.long} seconds", usage="searchQuote|sq start", brief="Fanfic")
    @commands.cooldown(1, Utils.long, commands.BucketType.guild)
    async def start(self, ctx):
        # Function to check a user's reaction
        def checker(reaction, user):
            return reaction.message.id == self.quoteSearcher.message.id and user.id == self.quoteSearcher.ctx.author.id and str(reaction) == "⏹️"
        # Initialise the SearchQuoteManager object
        message = await ctx.channel.send(embed=Embed(title="Quote Searcher", description=f"No filters added. Use {ctx.prefix}searchQuote add to add a filter", colour=self.colour))
        self.quoteSearcher = SearchQuoteManager(self.client, ctx, message, self.colour, self.worksheetArray)
        await message.add_reaction("⏹️")
        # Wait until the stop button is pressed with a timeout of 5 minutes
        while True:
            try:
                reaction, user = await self.client.wait_for("reaction_add", timeout=300, check=checker)
            except asyncio.TimeoutError:
                pass
            await message.clear_reactions()
            break
        # Pick a row
        tempArray = self.quoteSearcher.array
        if len(tempArray) == 0:
            # No matches found
            await ctx.channel.send("No matches found")
        elif len(tempArray) == 1:
            # Create quote for single match
            quote, work, authors, chapterName = self.quoteMaker(tempArray[0][10])
            if quote != "":
                # Valid quote found
                await ctx.channel.send(embed=self.quoteEmbedCreater(quote, work, authors, chapterName))
            else:
                # No valid quotes found
                await ctx.channel.send("No valid quotes found")
        else:
            # Multiple matches
            quote = ""
            while quote == "" and len(tempArray) > 0:
                quote, work, authors, chapterName = self.quoteMaker(tempArray.pop(random.randint(0, len(tempArray)-1))[10])
                if quote != "":
                    # Valid quote found
                    await ctx.channel.send(embed=self.quoteEmbedCreater(quote, work, authors, chapterName))
                    break
            else:
                # No valid quotes found
                await ctx.channel.send("No valid quotes found")
        # Reset the quote searcher object so it can be reused
        self.quoteSearcher = None

    # searchQuote add command with a cooldown of 1 use every 5 seconds per guild
    @searchQuote.command(help=f"Add a filter to the quote searcher. It has a cooldown of {Utils.superShort} seconds", description="\nArguments:\nTitle - Result contains this term\nAuthor - Result contains this term\nShip - Result matches this term\nSeries - Result contains this term\nStatus - Result matches this term. Can either be 'Completed', 'In progress' or 'Abandoned'\nSmut - Result matches this term. Can either be 'Yes', 'No' or '?'\nWords - Result matches this term. Use '>', '<', '>=', '<=', '==', '!=', '-' (for a range)\nChapters - Result matches this term", usage="searchQuote|sq (title/author/ship/series/status/smut/words/chapters) (term)", brief="Fanfic")
    @commands.cooldown(1, Utils.superShort, commands.BucketType.guild)
    async def add(self, ctx, *args):
        if self.quoteSearcher is None:
            await ctx.channel.send(f"Quote searcher not initialised. Run {ctx.prefix}searchQuote start to initialise it")
        else:
            await self.quoteSearcher.addFilter(ctx, args)

    # outline command with a cooldown of 1 use every 45 seconds per guild
    @commands.command(help=f"Finds the last quote posted and displays the metadata for that fic. It has a cooldown of {Utils.medium} seconds", usage="outline", brief="Fanfic")
    @commands.cooldown(1, Utils.medium, commands.BucketType.guild)
    async def outline(self, ctx):
        # Get the last quote posted and store its url
        lastQuote = await self.findLastQuote(ctx)
        if lastQuote is None:
            await ctx.channel.send(f"Cannot find the last quote. Try running {ctx.prefix}quote")
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
    async def works(self, ctx):
        # Get the last quote posted and create an AO3 User object
        lastQuote = await self.findLastQuote(ctx)
        if lastQuote is None:
            await ctx.channel.send(f"Cannot find the last quote. Try running {ctx.prefix}quote")
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
                    splitList = self.listSplit(works, workLimit, maxPage)
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
                    paginator = Paginator(ctx, self.client)
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
                await ctx.channel.send(f"{authorName} has {user.works} works which is over the limit of {pageLimit*20}")

    # Function to run channelCheck for Fanfic
    async def cog_check(self, ctx):
        return await Utils.restrictor.commandCheck(ctx)

    # Catch any cog errors
    async def cog_command_error(self, ctx, error):
        await Utils.errorHandler(ctx, error)


# Function which initialises the Fanfic cog
def setup(client):
    client.add_cog(Fanfic(client))
