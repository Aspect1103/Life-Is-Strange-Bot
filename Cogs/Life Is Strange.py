# Builtin
import json
import math
import random
from pathlib import Path
from typing import Tuple, Union, List, Dict
# Pip
from discord import Colour, Embed, File, Member, Message, Cog, ui, ButtonStyle, Interaction, option
from discord.ext import commands, bridge
# Custom
from Helpers.Utils import Utils
from Helpers.Utils.Paginator import Paginator

# Path variables
rootDirectory = Path(__file__).parent.parent
triviaPath = rootDirectory.joinpath("Resources").joinpath("Files").joinpath("trivia.json")
choicesPath = rootDirectory.joinpath("Resources").joinpath("Files").joinpath("choices.json")
memoryPath = rootDirectory.joinpath("Resources").joinpath("Screenshots").joinpath("LiS")
remasterMemoryPath = rootDirectory.joinpath("Resources").joinpath("Screenshots").joinpath("LiS Remaster")
tcMemoryPath = rootDirectory.joinpath("Resources").joinpath("Screenshots").joinpath("TC")
lis2MemoryPath = rootDirectory.joinpath("Resources").joinpath("Screenshots").joinpath("LiS2")
btsMemoryPath = rootDirectory.joinpath("Resources").joinpath("Screenshots").joinpath("BtS")
spiritMemoryPath = rootDirectory.joinpath("Resources").joinpath("Screenshots").joinpath("Captain Spirit")
btsRemasterMemoryPath = rootDirectory.joinpath("Resources").joinpath("Screenshots").joinpath("BtS Remaster")
wavelengthsMemoryPath = rootDirectory.joinpath("Resources").joinpath("Screenshots").joinpath("Wavelengths")
farewellMemoryPath = rootDirectory.joinpath("Resources").joinpath("Screenshots").joinpath("Farewell")


# Trivia class for trivia displaying
class TriviaView(ui.View):
    # Initialise variables
    def __init__(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext], bot: bridge.Bot, lifeIsStrangeCog, timeout: float = 15) -> None:
        super().__init__(timeout=timeout, disable_on_timeout=True)
        self.ctx = ctx
        self.bot = bot
        self.lifeIsStrangeCog = lifeIsStrangeCog
        self.message = None
        self.triviaObj = None
        self.correctOption = None

    @ui.button(emoji="🇦", style=ButtonStyle.primary, custom_id="1")
    async def aButton(self, button: ui.Button, interaction: Interaction) -> None:
        await self.message.edit(embed=self.lifeIsStrangeCog.finalTrivia(self.triviaObj, self.correctOption, interaction))
        await interaction.response.send_message(f"You reacted to {button.emoji}", ephemeral=True)
        await self.postTrivia(interaction)

    @ui.button(emoji="🇧", style=ButtonStyle.primary, custom_id="2")
    async def bButton(self, button: ui.Button, interaction: Interaction) -> None:
        await self.message.edit(embed=self.lifeIsStrangeCog.finalTrivia(self.triviaObj, self.correctOption, interaction))
        await interaction.response.send_message(f"You reacted to {button.emoji}", ephemeral=True)
        await self.postTrivia(interaction)

    @ui.button(emoji="🇨", style=ButtonStyle.primary, custom_id="3")
    async def cButton(self, button: ui.Button, interaction: Interaction) -> None:
        await self.message.edit(embed=self.lifeIsStrangeCog.finalTrivia(self.triviaObj, self.correctOption, interaction))
        await interaction.response.send_message(f"You reacted to {button.emoji}", ephemeral=True)
        await self.postTrivia(interaction)

    @ui.button(emoji="🇩", style=ButtonStyle.primary, custom_id="4")
    async def dButton(self, button: ui.Button, interaction: Interaction) -> None:
        await self.message.edit(embed=self.lifeIsStrangeCog.finalTrivia(self.triviaObj, self.correctOption, interaction))
        await interaction.response.send_message(f"You reacted to {button.emoji}", ephemeral=True)
        await self.postTrivia(interaction)

    async def start(self, triviaObj, correctOption) -> None:
        self.triviaObj, self.correctOption = triviaObj, correctOption
        interaction: Interaction = await self.ctx.respond(embed=triviaObj, view=self)
        self.message: Message = await interaction.original_message()

    async def on_timeout(self) -> None:
        await self.message.edit(embed=self.lifeIsStrangeCog.finalTrivia(self.triviaObj, self.correctOption, None))
        await self.postTrivia(None)

    async def postTrivia(self, interaction) -> None:
        await self.lifeIsStrangeCog.updateTriviaScores(self.ctx, self.correctOption, interaction)
        self.stop()


# Cog to manage life is strange commands
class lifeIsStrange(Cog, name="LifeIsStrange"):
    # Initialise the bot
    def __init__(self, bot: bridge.Bot) -> None:
        self.bot = bot
        self.colour = Colour.purple()
        self.triviaReactions = {"🇦": 1, "🇧": 2, "🇨": 3, "🇩": 4}
        self.triviaQuestions = json.loads(open(triviaPath, "r").read())
        self.choicesTable = json.loads(open(choicesPath, "r").read())
        self.lisMemoryImages = list(memoryPath.glob("*"))
        self.remasterMemoryImages = list(remasterMemoryPath.glob("*"))
        self.tcMemoryImages = list(tcMemoryPath.glob("*"))
        self.lis2MemoryImages = list(lis2MemoryPath.glob("*"))
        self.btsMemoryImages = list(btsMemoryPath.glob("*"))
        self.spiritMemoryImages = list(spiritMemoryPath.glob("*"))
        self.btsRemasterMemoryImages = list(btsRemasterMemoryPath.glob("*"))
        self.wavelengthsMemoryImages = list(wavelengthsMemoryPath.glob("*"))
        self.farewellMemoryImages = list(farewellMemoryPath.glob("*"))
        self.memoryImages = self.lisMemoryImages + self.remasterMemoryImages + self.tcMemoryImages + self.lis2MemoryImages + self.btsMemoryImages
        self.dlcMemoryImages = self.spiritMemoryImages + self.wavelengthsMemoryImages + self.farewellMemoryImages
        self.allMemoryImages = self.lisMemoryImages + self.remasterMemoryImages + self.tcMemoryImages + self.lis2MemoryImages + self.btsMemoryImages + self.btsRemasterMemoryImages + self.spiritMemoryImages + self.wavelengthsMemoryImages + self.farewellMemoryImages
        # self.pastInputs = []
        # self.pastResponses = []
        self.nextTrivia = None
        random.shuffle(self.triviaQuestions)

    # Function which runs once the bot is set up and running
    async def startup(self) -> None:
        # Create dictionary for each guild to hold the trivia counter
        self.nextTrivia = {guild.id: 0 for guild in self.bot.guilds}

    # Function to create trivia questions
    def triviaMaker(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext]) -> Tuple[Embed, int]:
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
    def finalTrivia(self, triviaEmbed: Embed, correctOption: int, guess: Union[Interaction, None]) -> Embed:
        description = triviaEmbed.description.split("\n")
        newDescription = ""
        for count, option in enumerate(description):
            if count+1 == correctOption:
                temp = option + " ✅"
            else:
                temp = option + " ❌"
            if guess is not None:
                try:
                    if int(guess.custom_id) == count+1:
                        temp += f" \U00002B05 {guess.user.name}#{guess.user.discriminator} guessed"
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
    async def updateTriviaScores(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext], correctOption: int, guess: Union[Interaction, None]) -> None:
        # REMOVE THIS STUFF ONCE BUG FOUND
        orgUser = await Utils.database.fetchUser("SELECT * FROM triviaScores WHERE guildID = ? and userID = ?", (ctx.guild.id, ctx.author.id), "triviaScores")
        if guess is None:
            # No answer
            orgUser[2] -= 2
            orgUser[4] += 2
        else:
            # Get guess user's data
            guessUser = await Utils.database.fetchUser("SELECT * FROM triviaScores WHERE guildID = ? and userID = ?", (ctx.guild.id, guess.user.id), "triviaScores")
            if int(guess.custom_id) == correctOption:
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
            await Utils.database.execute(f"UPDATE triviaScores SET score = ?, pointsGained = ?, pointsLost = ? WHERE guildID = ? AND userID = ?", (guessUser[2], guessUser[3], guessUser[4], ctx.guild.id, guess.user.id))
        await Utils.database.execute(f"UPDATE triviaScores SET score = ?, pointsGained = ?, pointsLost = ? WHERE guildID = ? AND userID = ?", (orgUser[2], orgUser[3], orgUser[4], ctx.guild.id, ctx.author.id))
        await self.updateRanks(ctx.guild.id)

    # Function to update the ranks for a specific guild
    async def updateRanks(self, guildID: int) -> None:
        guildUsers = await Utils.database.fetch("SELECT * FROM triviaScores WHERE guildID = ?", (guildID, ))
        sortedRanks = [(count+1, row[0], row[1]) for count, row in enumerate(Utils.rankSort(guildUsers, 2))]
        await Utils.database.executeMany("UPDATE triviaScores SET rank = ? WHERE guildID = ? AND userID = ?", sortedRanks)

    # Function to remove a user from the triviaScores database when they leave
    @Cog.listener()
    async def on_member_remove(self, member: Member) -> None:
        await Utils.database.execute("DELETE FROM triviaScores WHERE guildID = ? and userID = ?", (member.guild.id, member.id))

    # trivia command with a cooldown of 1 use every 60 seconds per guild
    @bridge.bridge_command(description=f"Displays a trivia question which can be answered via the emojis. Times out in 15 seconds")
    @commands.cooldown(1, Utils.long, commands.BucketType.guild)
    async def trivia(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext]) -> None:
        triviaView = TriviaView(ctx, self.bot, self)
        await triviaView.start(*self.triviaMaker(ctx))

    # triviascore command with a cooldown of 1 use every 20 seconds per guild
    @bridge.bridge_command(aliases=["ts"], description=f"Displays a user's trivia score")
    @option("targetuser", Member, description="A mention of the person who's trivia score you want. Returns the author's trivia score by default", default=None)
    @commands.cooldown(1, Utils.short, commands.BucketType.guild)
    async def triviascore(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext], targetuser: Member = None) -> None:
        if targetuser is None:
            targetUser = ctx.author
        else:
            try:
                targetUser = await self.bot.fetch_user(targetuser.id)
            except commands.MemberNotFound:
                targetUser = ctx.author
        user = await Utils.database.fetch("SELECT * FROM triviaScores WHERE guildID = ? AND userID = ?", (ctx.guild.id, targetUser.id))
        userObj = await self.bot.fetch_user(targetUser.id)
        if len(user) == 0:
            # User not in database
            await Utils.commandDebugEmbed(ctx, f"{userObj.mention} hasn't answered any questions. Run /trivia to answer some")
        else:
            # User in database
            totalUsers = await Utils.database.fetch("SELECT * FROM triviaScores WHERE guildID = ?", (ctx.guild.id, ))
            triviaScoreEmbed = Embed(title=f"{userObj.name}'s Trivia Score", colour=self.colour)
            triviaScoreEmbed.description = f"Rank: **{user[0][5]}/{len(totalUsers)}**\nScore: **{user[0][2]}**\nPoints Gained: **{user[0][3]}**\nPoints Lost: **{user[0][4]}**"
            triviaScoreEmbed.set_thumbnail(url=userObj.avatar.url)
            await ctx.respond(embed=triviaScoreEmbed)

    # trivialeaderboard command with a cooldown of 1 use every 45 seconds per guild
    @bridge.bridge_command(aliases=["tl"], description=f"Displays the server's trivia scores leaderboard")
    @option("pageno", str, description="The page of the leaderboard that you want to see. Displays the 1st page by default", default="1")
    @commands.cooldown(1, Utils.medium, commands.BucketType.guild)
    async def trivialeaderboard(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext], pageno: str = "1") -> None:
        if pageno.isdigit():
            guildUsers = await Utils.database.fetch("SELECT * FROM triviaScores WHERE guildID = ?", (ctx.guild.id, ))
            guildUsers = Utils.rankSort(guildUsers, 2)
            scoreList = [item[2] for item in guildUsers]
            maxPage = math.ceil(len(guildUsers)/10)
            splittedList = Utils.listSplit(guildUsers, 10, maxPage)
            pageno = int(pageno)
            if maxPage != 0:
                if 1 <= pageno <= maxPage:
                    # Valid page number so display embed
                    triviaLeaderboardEmbed = Embed(title=f"{ctx.guild.name}'s Trivia Leaderboard", colour=self.colour)
                    leaderboardDescription = ""
                    for user in splittedList[pageno - 1]:
                        userName = await self.bot.fetch_user(user[1])
                        leaderboardDescription += f"{user[5]}. {userName}. (Score: **{user[2]}** | Points Gained: **{user[3]}** | Points Lost: **{user[4]}**)\n"
                    if leaderboardDescription == "":
                        leaderboardDescription = "No users added. Run /trivia to add some"
                    triviaLeaderboardEmbed.description = leaderboardDescription
                    triviaLeaderboardEmbed.set_footer(text=f"Top 10 Average Score: {round(sum(scoreList[:10]) / len(scoreList[:10]))} | Total Average Score: {round(sum(scoreList) / len(scoreList))} | Total User Count: {len(guildUsers)} | Page {pageno} of {maxPage}")
                    await ctx.respond(embed=triviaLeaderboardEmbed)
                else:
                    # Number not in range
                    await Utils.commandDebugEmbed(ctx, f"Invalid page number. Pick a number between 1 and {maxPage}")
            else:
                # No users in database
                await Utils.commandDebugEmbed(ctx, f"No users registered. Run /trivia to register some")
        else:
            # Argument is not a number
            await Utils.commandDebugEmbed(ctx, f"Invalid argument. Pick a valid number")

    # choices command with a cooldown of 1 use every 60 seconds per guild
    @bridge.bridge_command(description=f"Displays the different choices in the game and their responses")
    @option("epnumber", int, description="Either 1, 2, 3, 4 or 5. Displays all choices by default", default=None)
    @commands.cooldown(1, Utils.long, commands.BucketType.guild)
    async def choices(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext], epnumber: int = None) -> None:
        if epnumber is None:
            # Display all choices with a paginator
            pages = []
            for count, episode in enumerate(self.choicesTable):
                pages.append(self.choicePageMaker(count+1, episode))
            # Create paginator
            paginator = Paginator(ctx, self.bot)
            paginator.addPages(pages)
            await paginator.start()
        else:
            episodeNum = int(epnumber)
            if 1 <= episodeNum <= 5:
                # Create embed page
                await ctx.respond(embed=self.choicePageMaker(episodeNum, self.choicesTable[episodeNum-1]))
            else:
                await Utils.commandDebugEmbed(ctx, "Not a valid episode number")

    # lismemory command with a cooldown of 1 use every 20 seconds per guild
    @bridge.bridge_command(aliases=["lm"], description=f"Displays a random Life is Strange screenshot")
    @commands.cooldown(1, Utils.short, commands.BucketType.guild)
    async def lismemory(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext]) -> None:
        await ctx.respond(file=File(random.choice(self.lisMemoryImages)))

    # remastermemory command with a cooldown of 1 use every 20 seconds per guild
    @bridge.bridge_command(aliases=["rm"], description=f"Displays a random Life is Strange Remastered screenshot")
    @commands.cooldown(1, Utils.short, commands.BucketType.guild)
    async def remastermemory(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext]) -> None:
        await ctx.respond(file=File(random.choice(self.remasterMemoryImages)))

    # tcmemory command with a cooldown of 1 use every 20 seconds per guild
    @bridge.bridge_command(aliases=["tm"], description=f"Displays a random Life is Strange True Colors screenshot")
    @commands.cooldown(1, Utils.short, commands.BucketType.guild)
    async def tcmemory(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext]) -> None:
        await ctx.respond(file=File(random.choice(self.tcMemoryImages)))

    # lis2memory command with a cooldown of 1 use every 20 seconds per guild
    @bridge.bridge_command(aliases=["l2m"], description=f"Displays a random Life is Strange 2 screenshot")
    @commands.cooldown(1, Utils.short, commands.BucketType.guild)
    async def lis2memory(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext]) -> None:
        await ctx.respond(file=File(random.choice(self.lis2MemoryImages)))

    # btsmemory command with a cooldown of 1 use every 20 seconds per guild
    @bridge.bridge_command(aliases=["bm"], description=f"Displays a random Life is Strange Before the Storm screenshot")
    @commands.cooldown(1, Utils.short, commands.BucketType.guild)
    async def btsmemory(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext]) -> None:
        await ctx.respond(file=File(random.choice(self.btsMemoryImages)))

    # spiritmemory command with a cooldown of 1 use every 20 seconds per guild
    @bridge.bridge_command(aliases=["sm"], description=f"Displays a random Captain Spirit screenshot")
    @commands.cooldown(1, Utils.short, commands.BucketType.guild)
    async def spiritmemory(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext]) -> None:
        await ctx.respond(file=File(random.choice(self.spiritMemoryImages)))

    # btsremastermemory command with a cooldown of 1 use every 20 seconds per guild
    @bridge.bridge_command(aliases=["brm"], description=f"Displays a random Life is Strange Before the Storm Remastered screenshot")
    @commands.cooldown(1, Utils.short, commands.BucketType.guild)
    async def btsremastermemory(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext]) -> None:
        await ctx.respond(file=File(random.choice(self.btsRemasterMemoryImages)))

    # wavelengthsmemory command with a cooldown of 1 use every 20 seconds per guild
    @bridge.bridge_command(aliases=["wm"], description=f"Displays a random Life is Strange Wavelengths screenshot")
    @commands.cooldown(1, Utils.short, commands.BucketType.guild)
    async def wavelengthsmemory(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext]) -> None:
        await ctx.respond(file=File(random.choice(self.wavelengthsMemoryImages)))

    # farewellmemory command with a cooldown of 1 use every 20 seconds per guild
    @bridge.bridge_command(aliases=["fm"], description=f"Displays a random Life is Strange Farewell screenshot")
    @commands.cooldown(1, Utils.short, commands.BucketType.guild)
    async def farewellmemory(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext]) -> None:
        await ctx.respond(file=File(random.choice(self.farewellMemoryImages)))

    # lismemory command with a cooldown of 1 use every 20 seconds per guild
    @bridge.bridge_command(aliases=["m"], description=f"Displays a random Life is Strange screenshot from any Life is Strange game")
    @commands.cooldown(1, Utils.short, commands.BucketType.guild)
    async def memory(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext]) -> None:
        await ctx.respond(file=File(random.choice(self.memoryImages)))

    # dlcmemory command with a cooldown of 1 use every 20 seconds per guild
    @bridge.bridge_command(aliases=["dm"], description=f"Displays a random Life is Strange DLC screenshot")
    @commands.cooldown(1, Utils.short, commands.BucketType.guild)
    async def dlcmemory(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext]) -> None:
        await ctx.respond(file=File(random.choice(self.dlcMemoryImages)))

    # allmemory command with a cooldown of 1 use every 20 seconds per guild
    @bridge.bridge_command(aliases=["am"], description=f"Displays a random screenshot from any Life is Strange game including DLCs")
    @commands.cooldown(1, Utils.short, commands.BucketType.guild)
    async def allmemory(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext]) -> None:
        await ctx.respond(file=File(random.choice(self.allMemoryImages)))

    # # image command with a cooldown of 1 use every 45 seconds per guild
    # @commands.command(help=f"Displays a random Life is Strange art piece using tags. It has a cooldown of {Utils.short} seconds", description="\nArguments:\nTags - A Life is Strange tag to search for. If none are provided, a random image is fetched", usage="image [tag1] [tag2] ...", brief="Image")
    # @commands.cooldown(1, Utils.short, commands.BucketType.guild)
    # async def art(self, ctx: commands.Context, *args) -> None:
    #     searchParams = "tags LIKE '%/lifeisstrange/%'" if len(args) == 0 else " AND ".join([f"tags LIKE '%/{tag}/%'" for tag in args])
    #     result = await Utils.database.fetch(f"SELECT * FROM images WHERE {searchParams} ORDER BY RANDOM() LIMIT 1", ())
    #     result = list(result)[0]
    #     tagString = result[1].split("/")
    #     imageEmbed = Embed(title="Random Life is Strange Image", colour=self.colour)
    #     imageEmbed.url = result[0]
    #     imageEmbed.add_field(name="Tags", value=", ".join(tagString[1:len(tagString)-1]))
    #     imageEmbed.set_image(url=result[0])
    #     await ctx.channel.send(embed=imageEmbed)
    #
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
    async def cog_check(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext]) -> bool:
        return await Utils.restrictor.commandCheck(ctx)

    # Catch any cog errors
    async def cog_command_error(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext], error: commands.CommandError) -> None:
        await Utils.errorHandler(ctx, error)


# Function which initialises the life is strange cog
def setup(bot: bridge.Bot) -> None:
    bot.add_cog(lifeIsStrange(bot))
