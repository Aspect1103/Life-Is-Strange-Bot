# Builtin
import random
import re
from typing import Union, Mapping, List
# Pip
from discord import Embed, Colour
from discord.appinfo import AppInfo
from discord.ext import commands
# Custom
from Helpers.Utils import Utils
from Helpers.Utils.Paginator import Paginator

# Attributes for the help command
attributes = {
    "cooldown": commands.Cooldown(1, Utils.superShort, commands.BucketType.user),
    "help": f"Displays the help command. It has a cooldown of {Utils.superShort} seconds",
    "description": "\nArguments:\nCog/Group/Command name - The name of the cog/group/command which you want help on",
    "usage": "help [cog/group/command name]",
    "brief": "Bot Bidness"
}


# Cog to manage miscellaneous commands
class Miscellaneous(commands.Cog):
    # Initialise the bot
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.colour = Colour.orange()
        self.bot.help_command = Help(command_attrs=attributes)
        self.bot.help_command.cog = self

    # Function which runs once the bot is setup and running
    async def startup(self) -> None:
        pass

    # bum command with a cooldown of 1 use every 5 seconds per user
    @commands.command(help=f"Displays a hypnotic gif. It has a cooldown of {Utils.superShort} seconds", usage="bum")
    @commands.cooldown(1, Utils.superShort, commands.BucketType.user)
    async def bum(self, ctx: commands.Context) -> None:
        await ctx.channel.send("https://giphy.com/gifs/midland-l4FsJgbbeKQC8MGBy")

    # murica command with a cooldown of 1 use every 5 seconds per user
    @commands.command(help=f"Displays a patriot. It has a cooldown of {Utils.superShort} seconds", usage="murica")
    @commands.cooldown(1, Utils.superShort, commands.BucketType.user)
    async def murica(self, ctx: commands.Context) -> None:
        await ctx.channel.send("https://tenor.com/view/merica-gif-9091003")

    # puppy command with a cooldown of 1 use every 5 seconds per user
    @commands.command(help=f"Displays a cute puppy. It has a cooldown of {Utils.superShort} seconds", usage="murica")
    @commands.cooldown(1, Utils.superShort, commands.BucketType.user)
    async def puppy(self, ctx: commands.Context) -> None:
        await ctx.channel.send("https://www.youtube.com/watch?v=j5a0jTc9S10")

    # pizza command with a cooldown of 1 use every 5 seconds per user
    @commands.command(help=f"Displays a delicious pizza. It has a cooldown of {Utils.superShort} seconds", usage="pizza")
    @commands.cooldown(1, Utils.superShort, commands.BucketType.user)
    async def pizza(self, ctx: commands.Context) -> None:
        await ctx.channel.send("https://tenor.com/view/pizza-party-dance-dancing-gif-10213545")

    # joyce command with a cooldown of 1 use every 5 seconds per user
    @commands.command(help=f"Displays either a cup of coffee, a cup of tea, some belgian waffles or some bacon. It has a cooldown of {Utils.superShort} seconds", usage="joyce")
    @commands.cooldown(1, Utils.superShort, commands.BucketType.user)
    async def joyce(self, ctx: commands.Context) -> None:
        gifs = [
            "https://tenor.com/view/coffee-coffee-cup-hot-hot-coffee-gif-16748161",
            "https://tenor.com/view/cup-of-tea-teapot-cuppa-hot-cup-of-tea-scalding-hot-gif-17825685",
            "https://tenor.com/view/waffles-food-syrup-honey-breakfast-gif-10931785",
            "https://tenor.com/view/bacon-gif-4287744",
            "https://tenor.com/view/eggs-breakfast-cooking-gif-14913289",
            "https://tenor.com/view/pour-in-food52-omelet-yummy-gif-19595825"
        ]
        await ctx.channel.send(f"Joyce: Incoming!\n{random.choice(gifs)}")

    # about command with a cooldown of 1 use every 20 seconds per guild
    @commands.command(help=f"Displays information about the bot. It has a cooldown of {Utils.short} seconds", usage="about", brief="Bot Bidness")
    @commands.cooldown(1, Utils.short, commands.BucketType.guild)
    async def about(self, ctx: commands.Context) -> None:
        # Create embed
        botInfo: AppInfo = await self.bot.application_info()
        aboutEmbed = Embed(title=f"About {ctx.me.name}", colour=self.colour)
        aboutEmbed.add_field(name="Developer", value=botInfo.owner, inline=True)
        aboutEmbed.add_field(name="Need Help?", value=f"Use {ctx.prefix}help", inline=True)
        aboutEmbed.add_field(name="GitHub Link", value="https://github.com/Aspect1103/Life-Is-Strange-Bot", inline=True)
        aboutEmbed.set_image(url="https://cdn.vox-cdn.com/thumbor/MfcKIGSMdpBNX1zKzquqFK776io=/0x0:3500x2270/1200x800/filters:focal(1455x422:2015x982)/cdn.vox-cdn.com/uploads/chorus_image/image/68988445/LiS_Remastered_Collection_Art.0.jpg")
        aboutEmbed.set_thumbnail(url="https://cdn.vox-cdn.com/thumbor/MfcKIGSMdpBNX1zKzquqFK776io=/0x0:3500x2270/1200x800/filters:focal(1455x422:2015x982)/cdn.vox-cdn.com/uploads/chorus_image/image/68988445/LiS_Remastered_Collection_Art.0.jpg")
        aboutEmbed.set_footer(text="Have a suggestion to improve the bot? DM me!", icon_url="https://cdn.vox-cdn.com/thumbor/MfcKIGSMdpBNX1zKzquqFK776io=/0x0:3500x2270/1200x800/filters:focal(1455x422:2015x982)/cdn.vox-cdn.com/uploads/chorus_image/image/68988445/LiS_Remastered_Collection_Art.0.jpg")
        # Send embed
        await ctx.channel.send(embed=aboutEmbed)

    # Function to run channelCheck for Miscellaneous
    async def cog_check(self, ctx: commands.Context) -> bool:
        return await Utils.restrictor.commandCheck(ctx)

    # Catch any cog errors
    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        await Utils.errorHandler(ctx, error)


# Cog to manage the help command
class Help(commands.HelpCommand):
    # Initialise attributes
    def __init__(self, **options) -> None:
        super().__init__(**options)
        self.colour = Colour.orange()

    # Function to get the command signature (the actual command)
    def get_command_signature(self, command: commands.Command) -> str:
        return f"`{self.clean_prefix}{command.qualified_name}` - {command.help}"

    # Function to create aliases string
    def createAliases(self, command: commands.Command) -> str:
        aliases = None
        if len(command.aliases) > 0:
            aliases = "Aliases: " + ", ".join([f"{self.clean_prefix}{comm}" for comm in command.aliases])
        return aliases

    # Function to get a cog name and separate it if needed
    def getCogName(self, name):
        return " ".join(re.split("(?=[A-Z])", name))

    # Function to check and determine the end channel for the help command
    async def channelCheck(self) -> Union[None, str]:
        return None if await Utils.restrictor.commandCheck(self.context) else await Utils.restrictor.grabAllowed(self.context)

    # Function to display help on the entire bot
    async def send_bot_help(self, mapping: Mapping[commands.Cog, List[Union[commands.Command, commands.Group, commands.HelpCommand]]]) -> None:
        # Test if the current channel is correct
        result = await self.channelCheck()
        if result is None:
            # Create embed list
            pages = []
            # Create home page
            homepageEmbed = Embed(title=f"Life Is Strange Bot", description="```<> = Required argument\n[] = Optional argument```", colour=self.colour)
            homepageEmbed.set_thumbnail(url="https://cdn.vox-cdn.com/thumbor/MfcKIGSMdpBNX1zKzquqFK776io=/0x0:3500x2270/1200x800/filters:focal(1455x422:2015x982)/cdn.vox-cdn.com/uploads/chorus_image/image/68988445/LiS_Remastered_Collection_Art.0.jpg")
            pages.append(homepageEmbed)
            # Get iterable dict of each cog and their commands
            pageCount = 0
            for cog, commandList in mapping.items():
                pageCount += 1
                commandSignatures = [self.get_command_signature(command) for command in commandList]
                # Test if there are any commands. If so, add field
                if commandSignatures:
                    # Create embed
                    helpEmbed = Embed(title=f"Page {pageCount}/{len(mapping.items()) - 1}", colour=self.colour)
                    helpEmbed.add_field(name=f"{self.getCogName(cog.qualified_name)} Cog", value="\n".join(commandSignatures), inline=False)
                    helpEmbed.set_footer(text=f"{len(commandList)} commands")
                    pages.append(helpEmbed)
                    # Append cog to the home page
                    pages[0].add_field(name=f"{self.getCogName(cog.qualified_name)}", value=f"For more information type:\n`{self.clean_prefix}help {cog.qualified_name}`")
            # Create paginator
            paginator = Paginator(self.context, self.context.bot)
            paginator.addPages(pages)
            await paginator.start()
        else:
            await Utils.commandDebugEmbed(self.get_destination(), result)

    # Function to display help on a specific cog
    async def send_cog_help(self, cog: commands.Cog) -> None:
        # Test if the current channel is correct
        result = await self.channelCheck()
        if result is None:
            # Create embed
            cogHelpEmbed = Embed(title=f"{self.getCogName(cog.qualified_name)} Help", colour=self.colour)
            cogHelpEmbed.set_footer(text=f"{len(cog.get_commands())} commands")
            for command in cog.get_commands():
                # Create aliases string
                aliases = self.createAliases(command)
                if aliases is not None:
                    cogHelpEmbed.add_field(name=f"{self.clean_prefix}{command.qualified_name}", value=f"{command.help}\n\n{aliases}", inline=False)
                else:
                    cogHelpEmbed.add_field(name=f"{self.clean_prefix}{command.qualified_name}", value=f"{command.help}", inline=False)
            # Send embed
            channel = self.get_destination()
            await channel.send(embed=cogHelpEmbed)
        else:
            await Utils.commandDebugEmbed(self.get_destination(), result)

    # Function to display help on a specific group
    async def send_group_help(self, group: commands.Group) -> None:
        # Test if the current channel is correct
        result = await self.channelCheck()
        if result is None:
            # Create aliases string
            aliases = self.createAliases(group)
            # Create embed
            groupHelpEmbed = Embed(title=f"{group.qualified_name} Help", colour=self.colour)
            groupHelpEmbed.set_footer(text=f"{len(group.commands)} commands")
            if aliases is not None:
                groupHelpEmbed.description = aliases
            for command in group.commands:
                groupHelpEmbed.add_field(name=f"{self.clean_prefix}{command.qualified_name}", value=f"{command.help}", inline=False)
            # Send embed
            channel = self.get_destination()
            await channel.send(embed=groupHelpEmbed)
        else:
            await Utils.commandDebugEmbed(self.get_destination(), result)

    # Function to display help on a specific command
    async def send_command_help(self, command: commands.Command) -> None:
        # Test if the current channel is correct
        result = await self.channelCheck()
        if result is None:
            # Create aliases string
            aliases = self.createAliases(command)
            # Create embed
            commandHelpEmbed = Embed(title=f"{self.clean_prefix}{command.qualified_name} Help", colour=self.colour)
            if aliases is not None:
                commandHelpEmbed.set_footer(text=aliases)
            if command.description == "":
                commandHelpEmbed.add_field(name=command.help, value=f"No arguments\n\nUsage: {self.clean_prefix}{command.usage}\n\nRestricted to {command.brief} section. See $channel list")
            else:
                commandHelpEmbed.add_field(name=command.help, value=f"{command.description}\n\nUsage: {self.clean_prefix}{command.usage}\n\nRestricted to {command.brief} section. See $channel list")
            # Send embed
            channel = self.get_destination()
            await channel.send(embed=commandHelpEmbed)
        else:
            await Utils.commandDebugEmbed(self.get_destination(), result)

    # Function to handle help error messages
    async def send_error_message(self, error: str) -> None:
        # Send error message
        await Utils.commandDebugEmbed(self.get_destination(), error)
        Utils.errorWrite(error)


# Function which initialises the Miscellaneous cog
def setup(bot: commands.Bot) -> None:
    bot.add_cog(Miscellaneous(bot))
