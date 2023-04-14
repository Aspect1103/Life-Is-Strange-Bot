from __future__ import annotations

# Builtin
import random
from pathlib import Path
from typing import Union

# Pip
from discord import Embed, Colour, Cog
from discord.appinfo import AppInfo
from discord.ext import commands, bridge

# Custom
from lis_bot.helpers.utils import utils

# Attributes for the help command
attributes = {
    "cooldown": commands.CooldownMapping(
        commands.Cooldown(1, utils.superShort), commands.BucketType.guild,
    ),
    "help": f"Displays the help command. It has a cooldown of {utils.superShort} seconds",
    "description": "\nArguments:\nCog/Group/Command name - The name of the cog/group/command which you want help on",
    "usage": "help [cog/group/command name]",
    "brief": "Bot Bidness",
}

# Path variables
rootDirectory = Path(__file__).parent.parent
questionPath = (
    rootDirectory.joinpath("resources").joinpath("files").joinpath("questions.txt")
)
gunPath = rootDirectory.joinpath("resources").joinpath("files").joinpath("gunLines.txt")


# Cog to manage miscellaneous commands
class Miscellaneous(Cog):
    # Initialise the bot
    def __init__(self, bot: bridge.Bot) -> None:
        self.bot = bot
        self.colour = Colour.orange()
        self.questionArray = [
            line.replace("\n", "")
            for line in open(questionPath, encoding="utf").readlines()
        ]
        self.nextQuestion = None
        self.gunLines = None

    # Function which runs once the bot is set up and running
    async def startup(self) -> None:
        # Create dictionary for each guild to store variables
        self.nextQuestion = {guild.id: 0 for guild in self.bot.guilds}
        # Create gun lines list
        lines = []
        for line in open(gunPath).readlines():
            if "/RARE" in line:
                line = line.replace("/RARE", "")
                lines.extend([line, line])
            else:
                line = line.replace("\n", "")
                lines.append(line)
        self.gunLines = lines

    # bum command with a cooldown of 1 use every 5 seconds per user
    @bridge.bridge_command(description="Displays a hypnotic gif")
    @commands.cooldown(1, utils.superShort, commands.BucketType.guild)
    async def bum(
        self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext],
    ) -> None:
        await ctx.respond("https://giphy.com/gifs/midland-l4FsJgbbeKQC8MGBy")

    # murica command with a cooldown of 1 use every 5 seconds per user
    @bridge.bridge_command(description="Displays a patriot")
    @commands.cooldown(1, utils.superShort, commands.BucketType.guild)
    async def murica(
        self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext],
    ) -> None:
        await ctx.respond("https://tenor.com/view/merica-gif-9091003")

    # puppy command with a cooldown of 1 use every 5 seconds per user
    @bridge.bridge_command(description="Displays a cute puppy")
    @commands.cooldown(1, utils.superShort, commands.BucketType.guild)
    async def puppy(
        self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext],
    ) -> None:
        await ctx.respond("https://www.youtube.com/watch?v=j5a0jTc9S10")

    # pizza command with a cooldown of 1 use every 5 seconds per user
    @bridge.bridge_command(description="Displays a delicious pizza")
    @commands.cooldown(1, utils.superShort, commands.BucketType.guild)
    async def pizza(
        self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext],
    ) -> None:
        await ctx.respond(
            "https://tenor.com/view/pizza-party-dance-dancing-gif-10213545",
        )

    # joyce command with a cooldown of 1 use every 5 seconds per user
    @bridge.bridge_command(
        description="Displays either a cup of coffee, a cup of tea, some belgian waffles or some bacon",
    )
    @commands.cooldown(1, utils.superShort, commands.BucketType.guild)
    async def joyce(
        self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext],
    ) -> None:
        gifs = [
            "https://tenor.com/view/coffee-coffee-cup-hot-hot-coffee-gif-16748161",
            "https://tenor.com/view/cup-of-tea-teapot-cuppa-hot-cup-of-tea-scalding-hot-gif-17825685",
            "https://tenor.com/view/waffles-food-syrup-honey-breakfast-gif-10931785",
            "https://tenor.com/view/bacon-gif-4287744",
            "https://tenor.com/view/eggs-breakfast-cooking-gif-14913289",
            "https://tenor.com/view/pour-in-food52-omelet-yummy-gif-19595825",
        ]
        await ctx.respond(f"Joyce: Incoming!\n{random.choice(gifs)}")

    # bang command with a cooldown of 1 use every 5 seconds per user
    @bridge.bridge_command(description="Fires Chloe's gun")
    @commands.cooldown(1, utils.superShort, commands.BucketType.guild)
    async def bang(
        self,
        ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext],
        message=None,
    ):
        if message is None:
            await ctx.respond(random.choice(self.gunLines))
        else:
            if (
                str(self.bot.owner_id) in str(message)
                and ctx.author.id != self.bot.owner_id
            ):
                # Message is mention of myself and I did not call the command
                await ctx.respond(
                    "**You cannot shoot God. Now die.** *Throws lightning bolt*",
                )
            else:
                # Message is just text
                await ctx.respond(random.choice(self.gunLines))

    # question command with a cooldown of 1 use every 20 seconds per guild
    @bridge.bridge_command(
        description="Displays a random question for users to answer",
    )
    @commands.cooldown(1, utils.short, commands.BucketType.guild)
    async def question(
        self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext],
    ) -> None:
        if self.nextQuestion[ctx.guild.id] == len(self.questionArray):
            # All questions done
            random.shuffle(self.questionArray)
            self.nextQuestion[ctx.guild.id] = 0
        randomQuestion: str = self.questionArray[self.nextQuestion[ctx.guild.id]]
        self.nextQuestion[ctx.guild.id] += 1
        questionEmbed = Embed(title=randomQuestion, colour=self.colour)
        questionEmbed.set_footer(text=f"{len(self.questionArray)} questions")
        await ctx.respond(embed=questionEmbed)

    # about command with a cooldown of 1 use every 20 seconds per guild
    @bridge.bridge_command(
        description=f"Displays information about the bot. It has a cooldown of {utils.short} seconds",
    )
    @commands.cooldown(1, utils.short, commands.BucketType.guild)
    async def about(
        self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext],
    ) -> None:
        # Create embed
        botInfo: AppInfo = await self.bot.application_info()
        aboutEmbed = Embed(title=f"About {botInfo.name}", colour=self.colour)
        aboutEmbed.add_field(name="Developer", value=botInfo.owner.name, inline=True)
        aboutEmbed.add_field(name="Need Help?", value="Use /help", inline=True)
        aboutEmbed.add_field(
            name="GitHub Link",
            value="https://github.com/Aspect1103/Life-Is-Strange-Bot",
            inline=True,
        )
        aboutEmbed.set_image(
            url="https://cdn.vox-cdn.com/thumbor/MfcKIGSMdpBNX1zKzquqFK776io=/0x0:3500x2270/1200x800/filters:focal(1455x422:2015x982)/cdn.vox-cdn.com/uploads/chorus_image/image/68988445/LiS_Remastered_Collection_Art.0.jpg",
        )
        aboutEmbed.set_thumbnail(
            url="https://cdn.vox-cdn.com/thumbor/MfcKIGSMdpBNX1zKzquqFK776io=/0x0:3500x2270/1200x800/filters:focal(1455x422:2015x982)/cdn.vox-cdn.com/uploads/chorus_image/image/68988445/LiS_Remastered_Collection_Art.0.jpg",
        )
        aboutEmbed.set_footer(
            text="Have a suggestion to improve the bot? DM me!",
            icon_url="https://cdn.vox-cdn.com/thumbor/MfcKIGSMdpBNX1zKzquqFK776io=/0x0:3500x2270/1200x800/filters:focal(1455x422:2015x982)/cdn.vox-cdn.com/uploads/chorus_image/image/68988445/LiS_Remastered_Collection_Art.0.jpg",
        )
        # Send embed
        await ctx.respond(embed=aboutEmbed)

    # Function to run channelCheck for Miscellaneous
    async def cog_check(
        self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext],
    ) -> bool:
        return await utils.restrictor.commandCheck(ctx)

    # Catch any cog errors
    async def cog_command_error(
        self,
        ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext],
        error: commands.CommandError,
    ) -> None:
        await utils.errorHandler(ctx, error)


# Function which initialises the Miscellaneous cog
def setup(bot: bridge.Bot) -> None:
    bot.add_cog(Miscellaneous(bot))
