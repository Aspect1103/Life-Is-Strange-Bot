# Builtin
from collections import defaultdict
import os
import requests
import random
import csv
import asyncio
# Pip
from discord.ext import commands
from discord import Embed
from discord import Colour
from bs4 import BeautifulSoup
# Custom
from Utils import Utils
from Utils.Paginator import Paginator

# Path variables
rootDirectory = os.path.join(os.path.dirname(__file__), os.pardir)
triviaPath = os.path.join(rootDirectory, "TextFiles", "trivia.txt")
errorPath = os.path.join(rootDirectory, "BotFiles", "error.txt")
questionPath = os.path.join(rootDirectory, "TextFiles", "../TextFiles/questions.txt")


# Cog to manage general commands
class General(commands.Cog):
    # Initialise the client
    def __init__(self, client):
        self.client = client
        self.nextTrivia = 0
        self.nextQuestion = 0
        self.colour = Colour.purple()
        self.allowedIDsTrivia = None
        self.allowedIDsChoices = None
        self.allowedIDsQuestion = None
        self.triviaQuestions = None
        self.choicesTable = None
        self.questionArray = None
        self.generalInit()

    # Function to initialise general variables
    def generalInit(self):
        # Create trivia questions array
        temp = []
        with open(triviaPath, "r") as file:
            reader = csv.reader(file, delimiter="/")
            for line in reader:
                temp.append(line)
        random.shuffle(temp)
        self.triviaQuestions = temp

        # Create questions array
        temp = []
        with open(questionPath, "r", encoding="utf") as file:
            for line in file.readlines():
                temp.append(line.replace("\n", ""))
        random.shuffle(temp)
        self.questionArray = temp

        # Setup allowed channel IDs
        self.allowedIDsTrivia = Utils.allowedIDs["trivia"]
        self.allowedIDsChoices = Utils.allowedIDs["choices"]
        self.allowedIDsQuestion = Utils.allowedIDs["question"]

        # Setup the choices table
        self.choiceGrabber()

    # Function to create trivia questions
    def triviaMaker(self):
        if self.nextTrivia == len(self.triviaQuestions):
            # All questions done
            random.shuffle(self.triviaQuestions)
            self.nextTrivia = 0
        randomTrivia = self.triviaQuestions[self.nextTrivia]
        self.nextTrivia += 1
        triviaEmbed = Embed(colour=self.colour)
        triviaEmbed.title = randomTrivia[0]
        triviaEmbed.description = f"A. {randomTrivia[1]}\nB. {randomTrivia[2]}\nC. {randomTrivia[3]}\nD. {randomTrivia[4]}"
        triviaEmbed.set_footer(text=f"{len(self.triviaQuestions)} questions")
        return triviaEmbed, int(randomTrivia[5])

    # Function to create final trivia embed
    def finalTrivia(self, triviaEmbed, correctInd, guess):
        description = triviaEmbed.description.split("\n")
        reactions = {
            1: "🇦",
            2: "🇧",
            3: "🇨",
            4: "🇩"
        }
        newDescription = ""
        for count, answer in enumerate(description):
            if count+1 == correctInd:
                temp = answer + " ✅"
            else:
                temp = answer + " ❌"
            if guess != None:
                if reactions[count+1] == str(guess[0]):
                    temp += f" ⬅ {guess[1]} guessed"
            newDescription += temp + "\n"
        finalObj = Embed(colour=self.colour)
        finalObj.title = triviaEmbed.title
        finalObj.description = newDescription
        finalObj.set_footer(text=f"{len(self.triviaQuestions)} questions")
        return finalObj

    # Function to grab choices info from the wiki
    def choiceGrabber(self):
        # Create soup
        soup = BeautifulSoup(requests.get("https://life-is-strange.fandom.com/wiki/Game_Statistics_(Season_1)").content, features="lxml")
        # Grab all choice results
        episodeCount = 0
        choices = []
        for count, choice in enumerate(soup.find_all("td")):
            try:
                # New episode so change the episode count and the major variable
                if choice.b.text == "Principal Wells" or choice.b.text == "Kate's Question" or choice.b.text == "Handicap Fund" or choice.b.text == "Chloe's Request" or choice.b.text == "Sacrifice Arcadia Bay":
                    episodeCount += 1
                    major = True
                # Done with major so change to minor
                if choice.b.text == "Daniel" or choice.b.text == "Max's Plant" or choice.b.text == "Blue Jay" or choice.b.text == "David":
                    major = False
                title = choice.b.text
                # Test for final result since the HTML is kinda weird
                if title == "Sacrifice Arcadia Bay":
                    title = "Final Choice"
                # Create final dict
                result = {"episode": episodeCount, "major": major, "title": title}
                for choiceNumber, ulTag in enumerate(choice.find_all("ul")):
                    if choiceNumber != 1:
                        # On sacrifice choice so skip it (HTML weird)
                        text = ""
                    for liTag in ulTag.find_all("li"):
                        # Split the text and percentage up
                        splitted = liTag.text.split(" -")
                        if len(splitted) == 1:
                            # Text doesn't conform to the rest so extra stuff needed
                            splitted = liTag.text.split(".")
                            percentageCleaned = splitted[1].replace("\xa0", "").replace("—", "").strip()
                            text += f"{splitted[0]}. - {percentageCleaned}\n"
                        else:
                            percentageCleaned = splitted[1].replace("\xa0", "").strip()
                            text += f"{splitted[0]} - {percentageCleaned}\n"
                    if "sacrifice" not in text:
                        # More choices afterwards so add another newline
                        text += "\n"
                    # Add final text to result
                    result["text"] = text
                # Add result dict to final
                choices.append(result)
            except AttributeError:
                pass
        # Separate the list of dictionaries into episodes
        result = defaultdict(list)
        for dic in choices:
            result[dic["episode"]].append(dic)
        self.choicesTable = list(result.values())

    # Function to create a choice embed page
    def choicePageMaker(self, count, episode):
        episodeEmbed = Embed(title=f"Episode {count} Choices", colour=self.colour)
        majorString = "".join([choice["text"] for choice in episode if choice["major"]])
        minorString = "".join([choice["text"] for choice in episode if not choice["major"]])
        episodeEmbed.add_field(name="Major Choices", value=majorString)
        episodeEmbed.add_field(name="Minor Choices", value=minorString)
        return episodeEmbed

    # trivia command with a cooldown of 1 use every 60 seconds per guild
    @commands.command(help="Displays a trivia question which can be answered via the emojis. It will timeout in 15 seconds. It has a cooldown of 60 seconds", usage="trivia")
    @commands.cooldown(1, 60, commands.BucketType.guild)
    async def trivia(self, ctx):
        # Grab random trivia
        triviaObj, correctIndex = self.triviaMaker()
        triviaMessage = await ctx.channel.send(embed=triviaObj)
        # Add relations
        await triviaMessage.add_reaction("🇦")
        await triviaMessage.add_reaction("🇧")
        await triviaMessage.add_reaction("🇨")
        await triviaMessage.add_reaction("🇩")
        # Wait for the user's reaction
        # Make sure the bot's reactions aren't counted
        await asyncio.sleep(1)
        try:
            reaction = await self.client.wait_for("reaction_add", timeout=15)
            # Edit the embed with the results
            resultEmbed = self.finalTrivia(triviaObj, correctIndex, reaction)
            await triviaMessage.edit(embed=resultEmbed)
        except asyncio.TimeoutError:
            resultEmbed = self.finalTrivia(triviaObj, correctIndex, None)
            await triviaMessage.edit(embed=resultEmbed)

    # choices command with a cooldown of 1 use every 45 seconds per guild
    @commands.command(help="Displays the different choices in the game and their responses. It has a cooldown of 30 seconds", description="\nArguments:\nEpisode Number - Either 1, 2, 3, 4 or 5. This argument is optional as not including it will display all choices", usage="choices (episode number)")
    @commands.cooldown(1, 0, commands.BucketType.guild)
    async def choices(self, ctx, *epNumber):
        if len(epNumber) == 0:
            # Display all choices with a paginator
            pages = []
            for count, episode in enumerate(self.choicesTable):
                pages.append(self.choicePageMaker(count+1, episode))
            # Create paginator
            paginator = Paginator(ctx, self.client)
            paginator.addPages(pages)
            await paginator.start()
        elif len(epNumber) == 1:
            # Only display specific episode number
            episodeNum = epNumber[0]
            # Run checks to make sure argument is correct
            if episodeNum.isdigit():
                episodeNum = int(episodeNum)
                if episodeNum >= 1 and episodeNum <= 5:
                    # Create embed page
                    await ctx.channel.send(embed=self.choicePageMaker(episodeNum, self.choicesTable[episodeNum-1]))
                else:
                    await ctx.channel.send("Not a valid episode number")
            else:
                await ctx.channel.send("Episode number is not a number")
        else:
            # Too many arguments
            await ctx.channel.send("Too many arguments")

    # question command with a cooldown of 1 use every 15 seconds per guild
    @commands.command(help="Displays a random question for users to answer. It has a cooldown of 15 seconds", usage="question")
    @commands.cooldown(1, 15, commands.BucketType.guild)
    async def question(self, ctx):
        if self.nextQuestion == len(self.questionArray):
            # All questions done
            random.shuffle(self.questionArray)
            self.nextQuestion = 0
        randomQuestion = self.questionArray[self.nextQuestion]
        self.nextQuestion += 1
        questionEmbed = Embed(title=randomQuestion,  colour=self.colour)
        questionEmbed.set_footer(text=f"{len(self.questionArray)} questions")
        await ctx.channel.send(embed=questionEmbed)

    # Function to run channelCheck for trivia
    async def cog_check(self, ctx):
        if str(ctx.command) == "trivia":
            return Utils.channelCheck(ctx, self.allowedIDsTrivia)
        elif str(ctx.command) == "choices":
            return Utils.channelCheck(ctx, self.allowedIDsChoices)
        elif str(ctx.command) == "question":
            return Utils.channelCheck(ctx, self.allowedIDsQuestion)

    # Catch any cog errors
    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            if str(ctx.command) == "trivia":
                textChannelAllowed = [self.client.get_channel(channel) for channel in self.allowedIDsTrivia]
            elif str(ctx.command) == "choices":
                textChannelAllowed = [self.client.get_channel(channel) for channel in self.allowedIDsChoices]
            elif str(ctx.command) == "question":
                textChannelAllowed = [self.client.get_channel(channel) for channel in self.allowedIDsQuestion]
            if all(element is None for element in textChannelAllowed):
                await ctx.channel.send(f"No channels added. Use {ctx.prefix}channel to add some")
            else:
                guildAllowed = ", ".join([channel.mention for channel in filter(None, textChannelAllowed) if channel.guild.id == ctx.guild.id])
                await ctx.channel.send(f"This command is only allowed in {guildAllowed}")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.channel.send(f"Command is on cooldown, try again in {round(error.retry_after, 2)} seconds")
        Utils.errorWrite(error)


# Function which initialises the General cog
def setup(client):
    client.add_cog(General(client))