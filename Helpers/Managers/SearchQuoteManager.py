# Pip
from discord.ext.commands import Context
from discord import Embed
from discord import Colour
from discord import Client
from discord import Message


# SearchQuoteManager class to switch between different embeds
class SearchQuoteManager:
    # Initialise variables
    def __init__(self, client: Client, ctx: Context, message: Message, colour: Colour, array: list):
        self.client = client
        self.ctx = ctx
        self.message = message
        self.colour = colour
        self.array = array
        self.categories = {
            "title": [self.titleFilter, "No filters added"],
            "author": [self.authorFilter, "No filters added"],
            "ship": [self.shipFilter, "No filters added"],
            "series": [self.seriesFilter, "No filters added"],
            "status": [self.statusFilter, "No filters added"],
            "smut": [self.smutFilter, "No filters added"],
            "words": [self.wordsFilter, "No filters added"],
            "chapters": [self.chaptersFilter, "No filters added"]
        }

    # Function to filter for title
    def titleFilter(self, arg):
        temp = []
        for row in self.array:
            if arg in row[1]:
                temp.append(row)
        self.array = temp

    # Function to filter for author
    def authorFilter(self, arg):
        temp = []
        for row in self.array:
            if arg in row[2]:
                temp.append(row)
        self.array = temp

    # Function to filter for ship
    def shipFilter(self, arg):
        temp = []
        for row in self.array:
            if arg in row[3].split("/"):
                temp.append(row)
        self.array = temp

    # Function to filter for series
    def seriesFilter(self, arg):
        temp = []
        for row in self.array:
            if arg in row[5]:
                temp.append(row)
        self.array = temp

    # Function to filter for status
    def statusFilter(self, arg):
        temp = []
        for row in self.array:
            if arg == row[6]:
                temp.append(row)
        self.array = temp

    # Function to filter for smut
    def smutFilter(self, arg):
        temp = []
        for row in self.array:
            if arg == row[7]:
                temp.append(row)
        self.array = temp

    # Function to filter for words
    def wordsFilter(self, arg):
        temp = []
        for row in self.array:
            if self.intSearch(row[8], arg):
                temp.append(row)
        self.array = temp

    # Function to filter for chapters
    def chaptersFilter(self, arg):
        temp = []
        for row in self.array:
            if self.intSearch(row[9], arg):
                temp.append(row)
        self.array = temp

    # Function to search for possible matches for words: and chapters:
    def intSearch(self, rowElement, search):
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

    # Function to add a filter
    async def addFilter(self, ctx, args):
        if ctx.author.id != self.ctx.author.id:
            # Incorrect user ID
            await ctx.channel.send(f"Only {self.ctx.author.mention} can add filters")
        else:
            if len(args) != 2:
                # Wrong format
                await ctx.channel.send("Invalid format. Make sure the command format is correct")
            else:
                if args[0].lower() not in self.categories.keys():
                    # Wrong category
                    await ctx.channel.send("Invalid filter. Make sure the category is correct")
                else:
                    if self.categories[args[0]][1] != "No filters added":
                        # Filters added
                        await ctx.channel.send("Filter already added")
                    else:
                        # Filter the worksheet array based on the new terms
                        self.categories[args[0]][0](args[1])
                        self.categories[args[0]][1] = args[1]
                        await self.updateEmbed()

    # Function to update the embed with the filters
    async def updateEmbed(self):
        tempEmbed = Embed(title="Quote Searcher", colour=self.colour)
        tempEmbed.set_footer(text=f"Total Results: {len(self.array)}")
        for key, value in self.categories.items():
            tempEmbed.add_field(name=key.capitalize(), value=value[1])
        await self.message.edit(embed=tempEmbed)
