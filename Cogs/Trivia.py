# Import libraries
from discord.ext import commands
from discord import Embed
from discord import Colour
from datetime import datetime
import csv
import os
import random
import asyncio
import json

# Path variables
rootDirectory = os.path.join(os.path.dirname(__file__), os.pardir)
triviaPath = os.path.join(rootDirectory, "TextFiles", "trivia.txt")
idPath = os.path.join(rootDirectory, "TextFiles", "IDs.txt")


# Cog to manage trivia commands
class Trivia(commands.Cog):
    # Initialise the client
    def __init__(self, client):
        self.client = client
        self.nextTrivia = 0
        self.allowedIDs = None
        self.triviaQuestions = None
        self.triviaInit()

    # Function to initialise trivia variables
    def triviaInit(self):
        # Create trivia questions array
        temp = []
        with open(triviaPath, "r") as file:
            reader = csv.reader(file, delimiter="/")
            for line in reader:
                temp.append(line)
        random.shuffle(temp)
        self.triviaQuestions = temp

        # Load allowed channel IDs
        with open(idPath, "r") as file:
            self.allowedIDs = json.loads(file.read())["trivia"]

    # Function to check if a command is in the correct channel
    def channelCheck(self, ctx):
        return ctx.channel.id in self.allowedIDs

    # Function to create trivia questions
    def triviaMaker(self):
        if self.nextTrivia == len(self.triviaQuestions):
            # All questions done
            self.triviaQuestions = random.shuffle(self.triviaQuestions)
            self.nextTrivia = 0
        randomTrivia = self.triviaQuestions[self.nextTrivia]
        self.nextTrivia += 1
        triviaEmbed = Embed(colour=Colour.purple())
        triviaEmbed.title = randomTrivia[0]
        triviaEmbed.description = f"A. {randomTrivia[1]}\nB. {randomTrivia[2]}\nC. {randomTrivia[3]}\nD. {randomTrivia[4]}"
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
        finalObj = Embed(colour=Colour.purple())
        finalObj.title = triviaEmbed.title
        finalObj.description = newDescription
        return finalObj

    # trivia command with a cooldown of 1 use every 60 seconds per guild
    @commands.command(help="Displays a trivia question which can be answered via the emojis. It will timeout in 15 seconds. It has a cooldown of 60 seconds")
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

    # Function to run channelCheck for s?trivia
    async def cog_check(self, ctx):
        return self.channelCheck(ctx)

    # Catch any cog errors
    async def cog_command_error(self, ctx, error):
        errorPath = os.path.join(rootDirectory, "BotFiles", "error.txt")
        if isinstance(error, commands.CheckFailure):
            textChannelAllowed = [self.client.get_channel(channel) for channel in self.allowedIDs]
            guildAllowed = ", ".join([channel.mention for channel in filter(None, textChannelAllowed)])
            await ctx.channel.send(f"This command is only allowed in {guildAllowed}")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.channel.send(f"Command is on cooldown, try again in {round(error.retry_after, 2)} seconds")
        with open(errorPath, "a") as file:
            file.write(f"{datetime.now()}, {error}\n")


# Function which initialises the Trivia cog
def setup(client):
    client.add_cog(Trivia(client))