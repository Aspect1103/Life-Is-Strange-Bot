# Builtin
import os
import random
import csv
import asyncio
import json
# Pip
from discord.ext import commands
from discord import Embed
from discord import Colour
from discord import File
# Custom
from Utils.Paginator import Paginator
from Utils import Utils

# Path variables
rootDirectory = os.path.join(os.path.dirname(__file__), os.pardir)
triviaPath = os.path.join(rootDirectory, "Resources", "trivia.txt")
choicesPath = os.path.join(rootDirectory, "Resources", "choices.txt")
errorPath = os.path.join(rootDirectory, "BotFiles", "error.txt")
memoryPath = os.path.join(rootDirectory, "Screenshots")


# Cog to manage life is strange commands
class lifeIsStrange(commands.Cog, name="Life Is Strange"):
    # Initialise the client
    def __init__(self, client):
        self.client = client
        self.colour = Colour.purple()
        self.nextTrivia = 0
        self.triviaQuestions = None
        self.choicesTable = None
        self.memoryImages = None
        self.lifeIsStrangeInit()

    # Function to initialise life is strange variables
    def lifeIsStrangeInit(self):
        # Create trivia questions array
        temp = list(csv.reader(open(triviaPath, "r"), delimiter="/"))
        random.shuffle(temp)
        self.triviaQuestions = temp

        # Setup the choices table
        self.choicesTable = json.loads(open(choicesPath, "r").read())

        # Setup memory images array
        self.memoryImages = os.listdir(memoryPath)

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

    # Function to create a choice embed page
    def choicePageMaker(self, count, episode):
        episodeEmbed = Embed(title=f"Episode {count} Choices", colour=self.colour)
        majorString = "".join([choice["text"] for choice in episode if choice["major"] == "Yes"])
        minorString = "".join([choice["text"] for choice in episode if choice["major"] == "No"])
        episodeEmbed.add_field(name="Major Choices", value=majorString)
        episodeEmbed.add_field(name="Minor Choices", value=minorString)
        return episodeEmbed

    # trivia command with a cooldown of 1 use every 60 seconds per guild
    @commands.command(help=f"Displays a trivia question which can be answered via the emojis. It will timeout in 15 seconds. It has a cooldown of {Utils.long} seconds", usage="trivia", brief="Trivia")
    @commands.cooldown(1, Utils.long, commands.BucketType.guild)
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
        await triviaMessage.clear_reactions()

    # choices command with a cooldown of 1 use every 60 seconds per guild
    @commands.command(help=f"Displays the different choices in the game and their responses. It has a cooldown of {Utils.long} seconds", description="\nArguments:\nEpisode Number - Either 1, 2, 3, 4 or 5. This argument is optional as not including it will display all choices", usage="choices (episode number)", brief="Life Is Strange")
    @commands.cooldown(1, Utils.long, commands.BucketType.guild)
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

    # memory command with a cooldown of 1 use every 20 seconds per guild
    @commands.command(help=f"Displays a random Life is Strange image. It has a cooldown of {Utils.short} seconds", usage="memory", brief="Life Is Strange")
    @commands.cooldown(1, Utils.short, commands.BucketType.guild)
    async def memory(self, ctx):
        randomImagePath = os.path.join(memoryPath, self.memoryImages[random.randint(0, len(self.memoryImages)-1)])
        await ctx.channel.send(file=File(randomImagePath))

    # Function to run channelCheck for Life Is Strange
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
        Utils.errorWrite(error)


# Function which initialises the life is strange cog
def setup(client):
    client.add_cog(lifeIsStrange(client))
