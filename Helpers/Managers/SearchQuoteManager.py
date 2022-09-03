# Builtin
from typing import List
# Pip
from discord import Embed, Colour, Message, ApplicationContext, Bot
# Custom
from Helpers.Utils import Utils


# SearchQuoteManager class to switch between different embeds
class SearchQuoteManager:
    # Initialise variables
    def __init__(self, bot: Bot, ctx: ApplicationContext, message: Message, colour: Colour, worksheet: List[List[str]]):
        self.bot = bot
        self.ctx = ctx
        self.message = message
        self.colour = colour
        self.orgArray = worksheet
        self.finalArray = worksheet
        self.filters = {
            "title": [self.titleFilter, None],
            "author": [self.authorFilter, None],
            "ship": [self.shipFilter, None],
            "series": [self.seriesFilter, None],
            "status": [self.statusFilter, None],
            "smut": [self.smutFilter, None],
            "words": [self.wordsFilter, None],
            "chapters": [self.chaptersFilter, None]
        }

    # Filter for a title arguments
    def titleFilter(self, arg: str) -> List[List[str]]:
        return [item for item in self.finalArray if arg in item[1]]

    # Filter for a author arguments
    def authorFilter(self, arg: str) -> List[List[str]]:
        return [item for item in self.finalArray if arg in item[2]]

    # Filter for a ship arguments
    def shipFilter(self, arg: str) -> List[List[str]]:
        return [item for item in self.finalArray if arg in item[3].split("/")]

    # Filter for a series arguments
    def seriesFilter(self, arg: str) -> List[List[str]]:
        return [item for item in self.finalArray if arg in item[5]]

    # Filter for a status arguments
    def statusFilter(self, arg: str) -> List[List[str]]:
        return [item for item in self.finalArray if arg.capitalize() == item[6]]

    # Filter for a smut arguments
    def smutFilter(self, arg: str) -> List[List[str]]:
        return [item for item in self.finalArray if arg.capitalize() == item[7]]

    # Filter for a words arguments
    def wordsFilter(self, arg: str) -> List[List[str]]:
        return [item for item in self.finalArray if self.intSearch(item[8], arg)]

    # Filter for a chapters arguments
    def chaptersFilter(self, arg: str) -> List[List[str]]:
        return [item for item in self.finalArray if self.intSearch(item[9], arg)]

    # Search for possible matches for words and chapters
    def intSearch(self, rowElement: str, arg: str) -> bool:
        # If the searchNumber is only letters, then None is returned which causes the if statement to be False
        searchNumber = int("".join([str(num) for num in arg if num.isdigit()]))
        if "==" in arg:
            return int(rowElement) == searchNumber
        elif "!=" in arg:
            return not int(rowElement) == searchNumber
        elif ">" in arg:
            return int(rowElement) > searchNumber
        elif ">=" in arg:
            return int(rowElement) >= searchNumber
        elif "<" in arg:
            return int(rowElement) < searchNumber
        elif "<=" in arg:
            return int(rowElement) <= searchNumber
        elif "-" in arg:
            splitted: List[str] = arg.split("-")
            num1 = int("".join([str(num) for num in splitted[0] if num.isdigit()]))
            num2 = int("".join([str(num) for num in splitted[1] if num.isdigit()]))
            return num1 < int(rowElement) < num2

    # Remove NSFW items
    def removeNSFW(self) -> None:
        self.finalArray = self.filters["smut"][0]("No")

    # Add a filter to the array
    async def addFilter(self, category: str, term: str) -> None:
        if category is None:
            await Utils.commandDebugEmbed(self.ctx, "Invalid category")
        elif term is None:
            await Utils.commandDebugEmbed(self.ctx, "Invalid term")
        else:
            lowerCase = category.lower()
            if lowerCase not in self.filters.keys():
                await Utils.commandDebugEmbed(self.ctx, "Unknown category")
            elif self.filters[lowerCase][1] is not None:
                await Utils.commandDebugEmbed(self.ctx, f"Filter already added. Use /searchQuote remove to remove the filter")
            else:
                # Filter the array and store the term
                self.finalArray: List[List[str]] = self.filters[lowerCase][0](term)
                if lowerCase == "status":
                    self.filters["status"][1] = term.capitalize()
                elif lowerCase == "smut":
                    self.filters["smut"][1] = term.capitalize()
                else:
                    self.filters[lowerCase][1] = term
                await self.updateEmbed()

    # Remove a filter from the array
    async def removeFilter(self, category):
        if category is None:
            await Utils.commandDebugEmbed(self.ctx, "Invalid category")
        else:
            lowerCase = category.lower()
            if lowerCase not in self.filters.keys():
                await Utils.commandDebugEmbed(self.ctx, "Unknown category")
            elif self.filters[lowerCase][1] is None:
                await Utils.commandDebugEmbed(self.ctx, f"Filter already added. Use /searchQuote remove to remove the filter")
            else:
                # Remove the term and re-filter the array from the start
                self.filters[lowerCase][1] = None
                self.finalArray: List[List[str]] = self.orgArray
                for key, value in self.filters.items():
                    if value[1] is not None:
                        self.finalArray = self.filters[key][0](value[1])
                await self.updateEmbed()

    # Update the embed with the filters
    async def updateEmbed(self) -> None:
        tempEmbed = Embed(title="Quote Searcher", colour=self.colour)
        tempEmbed.set_footer(text=f"Total Results: {len(self.finalArray)}")
        for key, value in self.filters.items():
            if value[1] is None:
                tempEmbed.add_field(name=key.capitalize(), value="No filters added")
            else:
                tempEmbed.add_field(name=key.capitalize(), value=value[1])
        await self.message.edit(embed=tempEmbed)
