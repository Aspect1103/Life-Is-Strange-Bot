# Builtin
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
from Utils.Paginator import Paginator
from Utils import Utils
import Config

# Path variables
rootDirectory = os.path.join(os.path.dirname(__file__), os.pardir)
ignorePath = os.path.join(rootDirectory, "TextFiles", "ignoreFics.txt")


# Cog to manage fanfic commands
class Fanfic(commands.Cog):
    # Initialise the client
    def __init__(self, client):
        self.client = client
        self.session = AO3.Session(Config.ao3Username, Config.ao3Password)
        self.colour = Colour.green()
        self.ignore = []
        self.worksheetArray = None
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
        with open(ignorePath, "r") as file:
            for line in file.readlines():
                self.ignore.append(line)

    # Function to make random quotes
    def quoteMaker(self, link):
        # Create work object
        work = AO3.Work(AO3.utils.workid_from_url(link), self.session)
        if str(work.workid) in self.ignore:
            # Work is a mystery
            return "", None, None, None
        # Repeat until a good quote is found
        quote = ""
        retries = 10
        # Set to 170 because embed description limit is 1024 (1024/6)=170.66666 words max
        while (len(quote.split()) < 10 or len(quote.split()) > 170) and retries > 0:
            retries -= 1
            # Get a random chapter's text
            randomChapter = random.randint(1, work.chapters)
            randomChapterText = work.get_chapter_text(randomChapter)
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
        return quote, work, authors, work.chapter_names[randomChapter-1]

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

    # Function to search the worksheet array and return matches
    def searcherOld(self, terms):
        # Create temporary 2D array
        tempWorksheet = self.worksheetArray
        # Iterate over each term and find matches
        for term in terms:
            formattedTerm = str(term.split(":")[1])
            if "title:" in term:
                tempWorksheet = [element for element in tempWorksheet if formattedTerm in element[1]]
            elif "author:" in term:
                tempWorksheet = [element for element in tempWorksheet if formattedTerm in element[2]]
            elif "ship:" in term:
                # do matches
                tempWorksheet = [element for element in tempWorksheet if formattedTerm in element[3]]
            elif "series:" in term:
                tempWorksheet = [element for element in tempWorksheet if formattedTerm in element[5]]
            elif "status:" in term:
                # do matches
                tempWorksheet = [element for element in tempWorksheet if formattedTerm in element[6]]
            elif "smut:" in term:
                # do matches
                tempWorksheet = [element for element in tempWorksheet if formattedTerm in element[7]]
            elif "words:" in term:
                # do matches + other stuff
                tempWorksheet = [element for element in tempWorksheet if formattedTerm in element[8]]
            elif "chapters:" in term:
                # do matches + other stuff
                tempWorksheet = [element for element in tempWorksheet if formattedTerm in element[9]]
        # Return the matched results
        return tempWorksheet

    # Function to search for possible matches for words: and chapters:
    def intSearch(term, rowElement, search):
        searchNumber = int("".join([str(num) for num in search if num.isdigit()]))
        if "==" in search:
            return rowElement == searchNumber
        elif "!=" in search:
            return not rowElement == searchNumber
        elif ">" in search:
            return int(rowElement) > searchNumber
        elif ">=" in search:
            return int(rowElement) >= searchNumber
        elif "<" in search:
            return int(rowElement) < searchNumber
        elif "<=" in search:
            return int(rowElement) <= searchNumber
        elif "-" in search:
            splitted = search.split("-")
            num1 = int("".join([str(num) for num in splitted[0] if num.isdigit()]))
            num2 = int("".join([str(num) for num in splitted[1] if num.isdigit()]))
            return num1 < int(rowElement) < num2

    # Function to search the worksheet array and return matches
    def searcher(self, terms):
        # Array to store final matches
        result = []
        # Iterate over every row in the worksheet
        for row in self.worksheetArray:
            # Array to store results of checks
            check = []
            # Iterate over each term
            for term in terms:
                formattedTerm = term.split(":")[1]
                if "title:" in term:
                    # Verify title
                    def filterTitle(row, search):
                        return search in row[1]
                    check.append(filterTitle(row, formattedTerm))
                elif "author:" in term:
                    # Verify author
                    def filterAuthor(row, search):
                        return search in row[2]
                    check.append(filterAuthor(row, formattedTerm))
                elif "ship:" in term:
                    # Verify ship
                    def filterShip(row, search):
                        return search in row[3].split("/")
                    check.append(filterShip(row, formattedTerm))
                elif "series:" in term:
                    # Verify series
                    def filterSeries(row, search):
                        return search in row[6]
                    check.append(filterSeries(row, formattedTerm))
                elif "status:" in term:
                    # Verify status
                    def filterStatus(row, search):
                        if search == "Completed":
                            return row[6] == "Completed"
                        elif search == "In progress":
                            return row[6] == "In progress"
                        elif search == "Abandoned":
                            return row[6] == "Abandoned"
                        else:
                            return False
                    check.append(filterStatus(row, formattedTerm))
                elif "smut:" in term:
                    # Verify smut
                    def filterSmut(row, search):
                        if search == "Yes":
                            return row[7] == "Yes"
                        elif search == "No":
                            return row[7] == "No"
                        elif search == "?":
                            return row[7] == "?"
                        return False
                    check.append(filterSmut(row, formattedTerm))
                elif "words:" in term:
                    # Verify words
                    check.append(self.intSearch(row[8], formattedTerm))
                elif "chapters:" in term:
                    # Verify chapters
                    check.append(self.intSearch(row[9], formattedTerm))
            # If all of the checks passed, then row matches
            if all(check):
                result.append(row)
        # Return all the matches
        return result

    # Function to find the last quote posted
    async def findLastQuote(self, ctx):
        async for message in ctx.channel.history(limit=100):
            if message.author.id == self.client.user.id:
                try:
                    if message.embeds[0].author.name != Embed.Empty:
                        return message.embeds[0]
                except IndexError:
                    pass

    # quote command with a cooldown of 1 use every 15 seconds per guild
    @commands.command(help="Grabs a random quote from a LiS fic on AO3. It has a cooldown of 15 seconds", usage="quote", brief="Fanfic")
    @commands.cooldown(1, 15, commands.BucketType.guild)
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

    # nextQuote command with a cooldown of 1 use every 15 seconds per guild
    @commands.command(aliases=["nq"], help="Finds the last quote posted and picks another quote from the same story. It has a cooldown of 15 seconds", usage="nextQuote|nq", brief="Fanfic")
    @commands.cooldown(1, 15, commands.BucketType.guild)
    async def nextQuote(self, ctx):
        # Get the last quote posted then get a new one
        lastQuote = await self.findLastQuote(ctx)
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

    # searchQuote command with a cooldown of 1 use every 15 seconds per guild
    @commands.command(aliases=["sq"], help="Takes multiple arguments and picks a random fic which matches those terms. It has a cooldown of 15 seconds", description="\nArguments:\nTitle - Result contains this term\nAuthor - Result contains this term\nShip - Result matches this term\nSeries - Result contains this term\nStatus - Result matches this term. Can either be 'Completed', 'In progress' or 'Abandoned'\nSmut - Result matches this term. Can either be 'Yes', 'No' or '?'\nWords - Result matches this term\nChapters - Result matches this term",  usage="searchQuote|sq (argument):(term) ...", brief="Fanfic")
    @commands.cooldown(1, 15, commands.BucketType.guild)
    async def searchQuote(self, ctx, *searchTerms):
        if len(searchTerms) > 0:
            # Search the worksheet array to find matching rows
            try:
                matches = self.searcher(searchTerms)
            except IndexError:
                matches = None
            if matches is None:
                await ctx.channel.send("Invalid format. Make sure there are no spaces for each term")
            elif len(matches) == 0:
                # No matches found
                await ctx.channel.send("No matches found")
            elif len(matches) == 1:
                # Create quote for single match
                quote, work, authors, chapterName = self.quoteMaker(matches[0][10])
                if quote == "":
                    # No valid quotes found
                    await ctx.channel.send("No valid quotes found")
                else:
                    # Valid quote found
                    await ctx.channel.send(embed=self.quoteEmbedCreater(quote, work, authors, chapterName))
            else:
                # Get random fic and create quote
                quote = ""
                while quote == "" and len(matches) > 0:
                    quote, work, authors, chapterName = self.quoteMaker(matches.pop(random.randint(0, len(matches)-1))[10])
                    if quote != "":
                        # Valid quote found
                        await ctx.channel.send(embed=self.quoteEmbedCreater(quote, work, authors, chapterName))
                        break
                else:
                    # No valid quotes found
                    await ctx.channel.send("No valid quotes found")
        else:
            # No search terms provided
            await ctx.channel.send("No search terms provided")

    # outline command with a cooldown of 1 use every 15 seconds per guild
    @commands.command(help="Finds the last quote posted and displays the metadata for that fic. It has a cooldown of 15 seconds", usage="outline", brief="Fanfic")
    @commands.cooldown(1, 15, commands.BucketType.guild)
    async def outline(self, ctx):
        # Get the last quote posted and store its url
        lastQuote = await self.findLastQuote(ctx)
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
        infoEmbed.set_footer(text=f"Words: {work.words}. Chapters: {work.chapters}. Language: {work.language}")
        # Display the embed
        await ctx.channel.send(embed=infoEmbed)

    # works command with a cooldown of 1 use every 45 seconds per guild
    @commands.command(help="Finds the last quote posted and displays all works posted by that author. It has a cooldown of 45 seconds", usage="works", brief="Fanfic")
    @commands.cooldown(1, 45, commands.BucketType.guild)
    async def works(self, ctx):
        # Get the last quote posted and create an AO3 User object
        lastQuote = await self.findLastQuote(ctx)
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
        result = await Utils.restrictor.commandCheck(ctx)
        return result

    # Catch any cog errors
    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            result = await Utils.restrictor.grabAllowed(ctx)
            await ctx.channel.send(result)
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.channel.send(f"Command is on cooldown, try again in {round(error.retry_after, 2)} seconds")
        elif isinstance(error.original, AO3.utils.HTTPError):
            await ctx.channel.send(error.original)
        Utils.errorWrite(error)


# Function which initialises the Fanfic cog
def setup(client):
    client.add_cog(Fanfic(client))