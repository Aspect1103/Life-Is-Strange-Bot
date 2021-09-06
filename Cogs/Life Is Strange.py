# Builtin
import asyncio
import json
import math
import random
from pathlib import Path
from typing import Optional, Tuple, Union, List, Dict
# Pip
from discord import Colour, Embed, File, Reaction, User, Member, Message
from discord.ext import commands
# Custom
from Helpers.Utils import Utils
from Helpers.Utils.Paginator import Paginator

# Path variables
rootDirectory = Path(__file__).parent.parent
triviaPath = rootDirectory.joinpath("Resources").joinpath("Files").joinpath("trivia.json")
choicesPath = rootDirectory.joinpath("Resources").joinpath("Files").joinpath("choices.json")
memoryPath = rootDirectory.joinpath("Resources").joinpath("Screenshots")


# Cog to manage life is strange commands
class lifeIsStrange(commands.Cog, name="LifeIsStrange"):
    # Initialise the bot
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.colour = Colour.purple()
        self.triviaReactions = {"🇦": 1, "🇧": 2, "🇨": 3, "🇩": 4}
        # self.pastInputs = []
        # self.pastResponses = []
        self.triviaQuestions = None
        self.nextTrivia = None
        self.choicesTable = None
        self.memoryImages = None
        self.lifeIsStrangeInit()
        self.bot.loop.create_task(self.startup())

    # Function to initialise life is strange variables
    def lifeIsStrangeInit(self) -> None:
        # Create trivia questions array
        self.triviaQuestions: List[Dict[str, str]] = json.loads(open(triviaPath, "r").read())
        random.shuffle(self.triviaQuestions)

        # Setup the choices table
        self.choicesTable: List[List[Dict[str, str]]] = json.loads(open(choicesPath, "r").read())

        # Setup memory images array
        self.memoryImages = list(memoryPath.glob("*"))

    # Function which runs once the bot is setup and running
    async def startup(self) -> None:
        await self.bot.wait_until_ready()
        # Create dictionary for each guild to hold the trivia counter
        self.nextTrivia = {guild.id: 0 for guild in self.bot.guilds}

    # Function to create trivia questions
    def triviaMaker(self, ctx: commands.Context) -> Tuple[Embed, int]:
        if self.nextTrivia[ctx.guild.id] == len(self.triviaQuestions):
            # All questions done
            random.shuffle(self.triviaQuestions)
            self.nextTrivia[ctx.guild.id] = 0
        randomTrivia: Dict[str, str] = self.triviaQuestions[self.nextTrivia[ctx.guild.id]]
        self.nextTrivia[ctx.guild.id] += 1
        triviaEmbed = Embed(colour=self.colour)
        triviaEmbed.title = randomTrivia["question"]
        triviaEmbed.description = f"""A. {randomTrivia["option 1"]}\nB. {randomTrivia["option 2"]}\nC. {randomTrivia["option 3"]}\nD. {randomTrivia["option 4"]}"""
        triviaEmbed.set_footer(text=f"{len(self.triviaQuestions)} questions")
        return triviaEmbed, int(randomTrivia["correct option"])

    # Function to create final trivia embed
    def finalTrivia(self, triviaEmbed: Embed, correctOption: int, guess: Union[Reaction, None]) -> Embed:
        description = triviaEmbed.description.split("\n")
        newDescription = ""
        for count, option in enumerate(description):
            if count+1 == correctOption:
                temp = option + " ✅"
            else:
                temp = option + " ❌"
            if guess is not None:
                try:
                    if self.triviaReactions[str(guess[0])] == count+1:
                        temp += f" \U00002B05 {str(guess[1])} guessed"
                except KeyError:
                    # Unknown emoji
                    pass
            newDescription += temp + "\n"
        finalObj = Embed(colour=self.colour)
        finalObj.title = triviaEmbed.title
        finalObj.description = newDescription
        finalObj.set_footer(text=f"{len(self.triviaQuestions)} questions")
        return finalObj

    # Function to create a choice embed page
    def choicePageMaker(self, count: int, episode: List[Dict[str, str]]) -> Embed:
        episodeEmbed = Embed(title=f"Episode {count} Choices", colour=self.colour)
        majorString = "".join([choice["text"] for choice in episode if choice["major"] == "Yes"])
        minorString = "".join([choice["text"] for choice in episode if choice["major"] == "No"])
        episodeEmbed.add_field(name="Major Choices", value=majorString)
        episodeEmbed.add_field(name="Minor Choices", value=minorString)
        return episodeEmbed

    # # Make a request to the huggingface model
    # def chatbotQuery(self, message):
    #     payload = {
    #         "inputs": {
    #             "past_user_inputs": self.pastInputs,
    #             "generated_responses": self.pastResponses,
    #             "text": message
    #         }, "parameters": {
    #             "max_length": 200,
    #             "temperature": 0.5,
    #             "top_k": 100,
    #             "top_p": 0.7
    #         }}
    #     return requests.post("https://api-inference.huggingface.co/models/Aspect11/DialoGPT-Medium-LiSBot",
    #                          headers={"Authorization": f"Bearer {Config.huggingfaceToken}"},
    #                          json=payload).json()

    # Function to update a user's trivia score
    async def updateTriviaScores(self, ctx: commands.Context, correctOption: int, guess: Union[Reaction, None]) -> None:
        orgUser = await Utils.database.fetchUser("SELECT * FROM triviaScores WHERE guildID = ? and userID = ?", (ctx.guild.id, ctx.author.id), "triviaScores")
        if guess is None:
            # No answer
            orgUser[2] -= 2
            orgUser[4] += 2
        else:
            # Get guess user's data
            guessUser = await Utils.database.fetchUser("SELECT * FROM triviaScores WHERE guildID = ? and userID = ?", (ctx.guild.id, ctx.author.id), "triviaScores")
            if self.triviaReactions[str(guess[0])] == correctOption:
                # Question correct
                if ctx.author.id == guessUser[1]:
                    # No steal
                    orgUser[2] += 2
                    orgUser[3] += 2
                else:
                    # Steal
                    orgUser[2] += 1
                    orgUser[3] += 1
                    guessUser[2] += 1
                    guessUser[3] += 1
            else:
                # Question incorrect
                if ctx.author.id == guessUser[1]:
                    # No steal
                    orgUser[2] -= 2
                    orgUser[4] += 2
                else:
                    # Steal
                    orgUser[2] -= 1
                    orgUser[4] += 1
                    guessUser[2] -= 1
                    guessUser[4] += 1
            await Utils.database.execute(f"UPDATE triviaScores SET score = ?, pointsGained = ?, pointsLost = ? WHERE guildID = ? AND userID = ?", (orgUser[2], orgUser[3], orgUser[4], ctx.guild.id, guess[1].id))
        await Utils.database.execute(f"UPDATE triviaScores SET score = ?, pointsGained = ?, pointsLost = ? WHERE guildID = ? AND userID = ?", (orgUser[2], orgUser[3], orgUser[4], ctx.guild.id, ctx.author.id))
        await self.updateRanks(ctx.guild.id)

    # Function to update the ranks for a specific guild
    async def updateRanks(self, guildID: int) -> None:
        guildUsers = await Utils.database.fetch("SELECT * FROM triviaScores WHERE guildID = ?", guildID)
        sortedRanks = [(count+1, row[0], row[1]) for count, row in enumerate(Utils.rankSort(guildUsers, 2))]
        await Utils.database.executeMany("UPDATE triviaScores SET rank = ? WHERE guildID = ? AND userID = ?", sortedRanks)

    # Function to remove a user from the triviaScores database when they leave
    @commands.Cog.listener()
    async def on_member_remove(self, member: Member) -> None:
        await Utils.database.execute("DELETE FROM triviaScores WHERE guildID = ? and userID = ?", (member.guild.id, member.id))

    # trivia command with a cooldown of 1 use every 60 seconds per guild
    @commands.command(help=f"Displays a trivia question which can be answered via the emojis. It will timeout in 15 seconds. It has a cooldown of {Utils.long} seconds", description="Scoring:\n\nNo answer = 2 points lost.\nCorrect answer and answered by the original command sender = 2 points gained.\nCorrect answer and answer stolen = 1 point gained for each person.\nIncorrect answer and answered by the original command sender = 2 points lost.\nIncorrect answer and answer stolen = 1 point lost for each person.", usage="trivia", brief="Trivia")
    @commands.cooldown(1, Utils.long, commands.BucketType.guild)
    async def trivia(self, ctx: commands.Context) -> None:
        def answerCheck(reaction: Reaction, user: User) -> bool:
            return user.id != self.bot.user.id and str(reaction) in self.triviaReactions
        # Grab random trivia
        triviaObj, correctOption = self.triviaMaker(ctx)
        triviaMessage: Message = await ctx.channel.send(embed=triviaObj)
        # Add relations
        for reaction in self.triviaReactions.keys():
            await triviaMessage.add_reaction(reaction)
        # Wait for the user's reaction and make sure the bot's reactions aren't counted
        reaction: Union[Reaction, None] = None
        while True:
            try:
                reaction = await self.bot.wait_for("reaction_add", timeout=15, check=answerCheck)
                # Edit the embed with the results
                resultEmbed = self.finalTrivia(triviaObj, correctOption, reaction)
                await triviaMessage.edit(embed=resultEmbed)
            except asyncio.TimeoutError:
                # Noone reacted
                resultEmbed = self.finalTrivia(triviaObj, correctOption, None)
                await triviaMessage.edit(embed=resultEmbed)
            break
        # Update trivia scores
        await self.updateTriviaScores(ctx, correctOption, reaction)
        await triviaMessage.clear_reactions()

    # triviaScore command with a cooldown of 1 use every 20 seconds per guild
    @commands.command(aliases=["ts"], help=f"Displays a user's trivia score. It has a cooldown of {Utils.short} seconds", description="\nArguments:\nTarget - A mention of the person who's trivia score you want. This argument is option as not including it will return the message author's trivia score", usage="triviaScore|ts [target]", brief="Trivia")
    @commands.cooldown(1, Utils.short, commands.BucketType.guild)
    async def triviaScore(self, ctx: commands.Context, target: Optional[str] = None) -> None:
        if target is None:
            targetUser = ctx.author
        else:
            try:
                targetUser = await commands.MemberConverter().convert(ctx, target)
            except commands.MemberNotFound:
                targetUser = ctx.author
        user = await Utils.database.fetch("SELECT * FROM triviaScores WHERE guildID = ? AND userID = ?", (ctx.guild.id, targetUser.id))
        userObj = await self.bot.fetch_user(targetUser.id)
        if len(user) == 0:
            # User not in database
            await Utils.commandDebugEmbed(ctx.channel, f"{userObj.mention} hasn't answered any questions. Run {ctx.prefix}trivia to answer some")
        else:
            # User in database
            totalUsers = await Utils.database.fetch("SELECT * FROM triviaScores WHERE guildID = ?", ctx.guild.id)
            triviaScoreEmbed = Embed(title=f"{userObj.name}'s Trivia Score", colour=self.colour)
            triviaScoreEmbed.description = f"Rank: **{user[0][5]}/{len(totalUsers)}**\nScore: **{user[0][2]}**\nPoints Gained: **{user[0][3]}**\nPoints Lost: **{user[0][4]}**"
            triviaScoreEmbed.set_thumbnail(url=userObj.avatar_url)
            await ctx.channel.send(embed=triviaScoreEmbed)

    # triviaLeaderboard command with a cooldown of 1 use every 45 seconds per guild
    @commands.command(aliases=["tl"], help=f"Displays the server's trivia scores leaderboard. It has a cooldown of {Utils.medium} seconds", description="\nArguments:\nPage Number - The page of the leaderboard that you want to see. This argument is optional as not including it will display the 1st page (top 10)", usage="triviaLeaderboard|tl [page number]", brief="Trivia")
    @commands.cooldown(1, Utils.medium, commands.BucketType.guild)
    async def triviaLeaderboard(self, ctx: commands.Context, pageNo: Optional[str] = "1") -> None:
        if pageNo.isdigit():
            guildUsers = await Utils.database.fetch("SELECT * FROM triviaScores WHERE guildID = ?", ctx.guild.id)
            guildUsers = Utils.rankSort(guildUsers, 2)
            scoreList = [item[2] for item in guildUsers]
            maxPage = math.ceil(len(guildUsers)/10)
            splittedList = Utils.listSplit(guildUsers, 10, maxPage)
            pageNo = int(pageNo)
            if maxPage != 0:
                if 1 <= pageNo <= maxPage:
                    # Valid page number so display embed
                    triviaLeaderboardEmbed = Embed(title=f"{ctx.guild.name}'s Trivia Leaderboard", colour=self.colour)
                    leaderboardDescription = ""
                    for user in splittedList[pageNo-1]:
                        userName = await self.bot.fetch_user(user[1])
                        leaderboardDescription += f"{user[5]}. {userName}. (Score: **{user[2]}** | Points Gained: **{user[3]}** | Points Lost: **{user[4]}**)\n"
                    if leaderboardDescription == "":
                        leaderboardDescription = f"No users added. Run {ctx.prefix}trivia to add some"
                    triviaLeaderboardEmbed.description = leaderboardDescription
                    triviaLeaderboardEmbed.set_footer(text=f"Top 10 Average Score: {round(sum(scoreList[:10]) / len(scoreList[:10]))} | Total Average Score: {round(sum(scoreList) / len(scoreList))} | Total User Count: {len(guildUsers)} | Page {pageNo} of {maxPage}")
                    await ctx.channel.send(embed=triviaLeaderboardEmbed)
                else:
                    # Number not in range
                    await Utils.commandDebugEmbed(ctx.channel, f"Invalid page number. Pick a number between 1 and {maxPage}")
            else:
                # No users in database
                await Utils.commandDebugEmbed(ctx.channel, f"No users registered. Run {ctx.prefix}trivia to register some")
        else:
            # Argument is not a number
            await Utils.commandDebugEmbed(ctx.channel, f"Invalid argument. Pick a valid number")

    # choices command with a cooldown of 1 use every 60 seconds per guild
    @commands.command(help=f"Displays the different choices in the game and their responses. It has a cooldown of {Utils.long} seconds", description="\nArguments:\nEpisode Number - Either 1, 2, 3, 4 or 5. This argument is optional as not including it will display all choices", usage="choices [episode number]", brief="Life Is Strange")
    @commands.cooldown(1, Utils.long, commands.BucketType.guild)
    async def choices(self, ctx: commands.Context, epNumber: Optional[int] = None) -> None:
        if epNumber is None:
            # Display all choices with a paginator
            pages = []
            for count, episode in enumerate(self.choicesTable):
                pages.append(self.choicePageMaker(count+1, episode))
            # Create paginator
            paginator = Paginator(ctx, self.bot)
            paginator.addPages(pages)
            await paginator.start()
        else:
            episodeNum = int(epNumber)
            if 1 <= episodeNum <= 5:
                # Create embed page
                await ctx.channel.send(embed=self.choicePageMaker(episodeNum, self.choicesTable[episodeNum-1]))
            else:
                await Utils.commandDebugEmbed(ctx.channel, "Not a valid episode number")

    # memory command with a cooldown of 1 use every 20 seconds per guild
    @commands.command(help=f"Displays a random Life is Strange image. It has a cooldown of {Utils.short} seconds", usage="memory", brief="Life Is Strange")
    @commands.cooldown(1, Utils.short, commands.BucketType.guild)
    async def memory(self, ctx: commands.Context) -> None:
        await ctx.channel.send(file=File(random.choice(self.memoryImages)))

    # # chatbot command with a cooldown of 1 use every 5 seconds per guild
    # @commands.command(help=f"Interacts with the LiS AI chatbot. It has a cooldown of {Utils.superShort} seconds", description="\nArguments:\nMessage - The message to send to the AI chatbot", usage="chatbot (message)", brief="Life Is Strange")
    # @commands.cooldown(1, Utils.superShort, commands.BucketType.guild)
    # async def chatbot(self, ctx, *args):
    #     async with ctx.channel.typing():
    #         req = self.chatbotQuery(" ".join(args))
    #         try:
    #             rounded = round(req["estimated_time"], 2)
    #             messageToSend = f"AI is starting up, try again in {round(rounded)} seconds"
    #         except KeyError:
    #             messageToSend = req["generated_text"]
    #             self.pastInputs.append(req["conversation"]["past_user_inputs"].pop(-1))
    #             self.pastResponses.append(req["conversation"]["generated_responses"].pop(-1))
    #     await ctx.channel.send(messageToSend)

    # Function to run channelCheck for Life Is Strange
    async def cog_check(self, ctx: commands.Context) -> bool:
        return await Utils.restrictor.commandCheck(ctx)

    # Catch any cog errors
    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        await Utils.errorHandler(ctx, error)


# Function which initialises the life is strange cog
def setup(bot: commands.Bot) -> None:
    bot.add_cog(lifeIsStrange(bot))
