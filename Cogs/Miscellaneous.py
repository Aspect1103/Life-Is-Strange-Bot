# Builtin
import os
# Pip
from discord.ext import commands
from discord import Embed
from discord import Colour
# Custom
from Utils import Utils
from Utils.Paginator import Paginator

# Path variables
rootDirectory = os.path.join(os.path.dirname(__file__), os.pardir)
# Attributes for the help command
attributes = {
    "cooldown": commands.Cooldown(1, 5, commands.BucketType.user),
    "help": "Displays the help command. It has a cooldown of 5 seconds"
}


# Cog to manage miscellaneous commands
class Miscellaneous(commands.Cog):
    # Initialise the client
    def __init__(self, client):
        self.client = client
        self.client.help_command = Help(command_attrs=attributes)
        self.client.help_command.cog = self

    # bum command with a cooldown of 1 use every 10 seconds per guild
    @commands.command(help="Displays a hypnotic gif. It has a cooldown of 10 seconds", usage="bum")
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def bum(self, ctx):
        await ctx.channel.send("https://giphy.com/gifs/midland-l4FsJgbbeKQC8MGBy")

    # murica command with a cooldown of 1 use every 10 seconds per guild
    @commands.command(help="Displays a patriot. It has a cooldown of 10 seconds", usage="murica")
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def murica(self, ctx):
        await ctx.channel.send("https://tenor.com/view/merica-gif-9091003")

    # puppy command with a cooldown of 1 use every 10 seconds per guild
    @commands.command(help="Displays a cute puppy. It has a cooldown of 10 seconds", usage="murica")
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def puppy(self, ctx):
        await ctx.channel.send("https://www.youtube.com/watch?v=j5a0jTc9S10")

    # pizza command with a cooldown of 1 use every 10 seconds per guild
    @commands.command(help="Displays a delicious pizza. It has a cooldown of 10 seconds", usage="pizza")
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def pizza(self, ctx):
        await ctx.channel.send("https://tenor.com/view/pizza-party-dance-dancing-gif-10213545")

    # about command with a cooldown of 1 use every 10 seconds per guild
    @commands.command(help="Displays information about the bot", usage="about")
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def about(self, ctx):
        # Create embed
        botInfo = await self.client.application_info()
        aboutEmbed = Embed(title=f"About {ctx.me.name}", colour=Colour.orange())
        aboutEmbed.add_field(name="Developer", value=botInfo.owner, inline=True)
        aboutEmbed.add_field(name="Need Help?", value=f"Use {ctx.prefix}help", inline=True)
        aboutEmbed.add_field(name="GitHub Link", value="https://github.com/Aspect1103/Life-Is-Strange-Bot", inline=True)
        aboutEmbed.set_image(url="https://cdn.vox-cdn.com/thumbor/MfcKIGSMdpBNX1zKzquqFK776io=/0x0:3500x2270/1200x800/filters:focal(1455x422:2015x982)/cdn.vox-cdn.com/uploads/chorus_image/image/68988445/LiS_Remastered_Collection_Art.0.jpg")
        aboutEmbed.set_thumbnail(url="https://cdn.vox-cdn.com/thumbor/MfcKIGSMdpBNX1zKzquqFK776io=/0x0:3500x2270/1200x800/filters:focal(1455x422:2015x982)/cdn.vox-cdn.com/uploads/chorus_image/image/68988445/LiS_Remastered_Collection_Art.0.jpg")
        aboutEmbed.set_footer(text="Have a suggestion to improve the bot? DM me!", icon_url="https://cdn.vox-cdn.com/thumbor/MfcKIGSMdpBNX1zKzquqFK776io=/0x0:3500x2270/1200x800/filters:focal(1455x422:2015x982)/cdn.vox-cdn.com/uploads/chorus_image/image/68988445/LiS_Remastered_Collection_Art.0.jpg")
        # Send embed
        await ctx.channel.send(embed=aboutEmbed)

    # Catch any cog errors
    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.channel.send(f"Command is on cooldown, try again in {round(error.retry_after, 2)} seconds")
        Utils.errorWrite(error)


# Cog to manage the help command
class Help(commands.HelpCommand):
    # Initialise attributes
    def __init__(self, **options):
        super().__init__(**options)
        self.allowedIDs = Utils.allowedIDs["help"]
        self.colour = Colour.orange()

    # Function to get the command signature (the actual command)
    def get_command_signature(self, command):
        return f"`{self.clean_prefix}{command.qualified_name}` - {command.help}"

    # Function to create aliases string
    def create_alises(self, command):
        aliases = None
        if len(command.aliases) > 0:
            aliases = "Aliases: " + ", ".join(command.aliases)
        return aliases

    # Function to check and determine the end channel for the help command
    def channelCheck(self):
        if Utils.channelCheck(self.context, self.allowedIDs):
            # Current channel is correct
            return True, self.context.bot.get_channel(self.context.channel.id)
        else:
            # Current channel is wrong
            textChannelAllowed = [self.context.bot.get_channel(channel) for channel in self.allowedIDs]
            if len([channel for channel in filter(None, textChannelAllowed) if channel.guild.id == self.context.guild.id]) == 0:
                return False, f"No channels added. Use {self.clean_prefix}channel to add some"
            else:
                guildAllowed = ", ".join([channel.mention for channel in filter(None, textChannelAllowed) if channel.guild.id == self.context.guild.id])
                return False, f"This command is only allowed in {guildAllowed}"

    # Function to display help on the entire bot
    async def send_bot_help(self, mapping):
        # Test if the current channel is correct
        valid, result = self.channelCheck()
        if valid:
            # Create embed list
            pages = []
            # Get iterable dict of each cog and their commands
            pageCount = 0
            for cog, commands in mapping.items():
                pageCount += 1
                commandSignatures = [self.get_command_signature(command) for command in commands]
                # Test if there are any commands. If so, add field
                if commandSignatures:
                    # Create embed
                    helpEmbed = Embed(title=f"Page {pageCount}/{len(mapping.items()) - 1}", colour=self.colour)
                    helpEmbed.add_field(name=f"{cog.qualified_name} Category", value="\n".join(commandSignatures), inline=False)
                    helpEmbed.set_footer(text=f"{len(commands)} commands. Requested by {self.context.author}")
                    pages.append(helpEmbed)
            # Create paginator
            paginator = Paginator(self.context, self.context.bot)
            paginator.addPages(pages)
            await paginator.start()
        else:
            await self.get_destination().send(result)

    # Function to display help on a specific cog
    async def send_cog_help(self, cog):
        # Test if the current channel is correct
        valid, result = self.channelCheck()
        if valid:
            # Create embed
            cogHelpEmbed = Embed(title=f"{cog.qualified_name} Help", colour=self.colour)
            cogHelpEmbed.set_footer(text=f"{len(cog.get_commands())} commands. Requested by {self.context.author}")
            for command in cog.get_commands():
                # Create aliases string
                aliases = self.create_alises(command)
                if aliases != None:
                    cogHelpEmbed.add_field(name=f"{self.clean_prefix}{command.qualified_name}", value=f"{command.help}\n\n{aliases}", inline=False)
                else:
                    cogHelpEmbed.add_field(name=f"{self.clean_prefix}{command.qualified_name}", value=f"{command.help}", inline=False)
            # Send embed
            channel = self.get_destination()
            await channel.send(embed=cogHelpEmbed)
        else:
            await self.get_destination().send(result)

    # Function to display help on a specific group
    async def send_group_help(self, group):
        # Test if the current channel is correct
        valid, result = self.channelCheck()
        if valid:
            # Create embed
            groupHelpEmbed = Embed(title=f"{group.qualified_name} Help", colour=self.colour)
            groupHelpEmbed.set_footer(text=f"{len(group.commands)} commands. Requested by {self.context.author}")
            for command in group.commands:
                # Create aliases string
                aliases = self.create_alises(command)
                if aliases != None:
                    groupHelpEmbed.add_field(name=f"{self.clean_prefix}{command.qualified_name}", value=f"{command.help}\n\n{aliases}", inline=False)
                else:
                    groupHelpEmbed.add_field(name=f"{self.clean_prefix}{command.qualified_name}", value=f"{command.help}", inline=False)
            # Send embed
            channel = self.get_destination()
            await channel.send(embed=groupHelpEmbed)
        else:
            await self.get_destination().send(result)

    # Function to display help on a specific command
    async def send_command_help(self, command):
        # Test if the current channel is correct
        valid, result = self.channelCheck()
        if valid:
            # Create aliases
            aliases = self.create_alises(command)
            # Create embed
            commandHelpEmbed = Embed(title=f"{self.clean_prefix}{command.qualified_name} Help", colour=self.colour)
            commandHelpEmbed.set_footer(text=f"Requested by {self.context.author}")
            if aliases != None:
                commandHelpEmbed.set_footer(text=aliases)
            if command.description == "":
                commandHelpEmbed.add_field(name=command.help, value=f"No arguments\n\nUsage: {self.clean_prefix}{command.usage}")
            else:
                commandHelpEmbed.add_field(name=command.help, value=f"{command.description}\n\nUsage: {self.clean_prefix}{command.usage}")
            # Send embed
            channel = self.get_destination()
            await channel.send(embed=commandHelpEmbed)
        else:
            await self.get_destination().send(result)

    # Function to handle help error messages
    async def send_error_message(self, error):
        # Send error message (since error is a string)
        channel = self.get_destination()
        await channel.send(error)
        Utils.errorWrite(error)


# Function which initialises the Miscellaneous cog
def setup(client):
    client.add_cog(Miscellaneous(client))
