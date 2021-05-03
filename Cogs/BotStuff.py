# Pip
from discord.ext import commands
from discord import Embed
from discord import Colour
# Custom
from Utils import Utils
from Utils.Paginator import Paginator

# Attributes for the help command
attributes = {
    "cooldown": commands.Cooldown(1, 5, commands.BucketType.user),
    "help": "Displays the help command. It has a cooldown of 5 seconds"
}


# Custom check function for administrator or bot owner
def adminOrOwner():
    def predicate(ctx):
        for permission in ctx.author.guild_permissions:
            if permission[0] == "administrator":
                return permission[1] or ctx.author.id == 538399052895748100
    return commands.check(predicate)


# Cog to manage bot commands
class BotStuff(commands.Cog, name="Bot Stuff"):
    def __init__(self, client):
        self.client = client
        self.colour = Colour.orange()
        self.allowedIDs = None
        self.client.help_command = Help(command_attrs=attributes)
        self.client.help_command.cog = self
        self.botInit()

    # Function to initialise fanfic variables
    def botInit(self):
        # Setup allowed channel IDs
        self.allowedIDs = Utils.allowedIDs["bot"]

    # Function to verify a channel command
    def channelVerify(self, ctx, args):
        if len(args) < 2:
            # Too little arguments
            return "Missing arguments", None
        if len(args) > 2:
            # Too many arguments
            return "Too many arguments", None
        else:
            # Correct amount of arguments
            if args[0] in Utils.allowedIDs:
                # Section exists
                channelID = int("".join([str(num) for num in args[1] if num.isdigit()]))
                if self.client.get_channel(channelID).guild.id == ctx.guild.id:
                    # Valid channel
                    return True, channelID
                else:
                    # Not a valid channel
                    return "Invalid channel for guild", None
            else:
                # Section doesn't exist
                validSections = "/".join(Utils.allowedIDs.keys())
                return f"Section not found. Try {validSections}", None

    # stop command
    @commands.command(aliases=["stop"], help="Stops the bot", usage="stop_s|stop")
    @commands.is_owner()
    async def stop_s(self, ctx):
        await ctx.channel.send("Stopping bot")
        await self.client.close()

    # Base function to initialise the channel group commands
    @commands.group(invoke_without_command=True, help="Group command for adding and removing allowed channels. This command has subcommads. It has a cooldown of 10 seconds", usage="channel")
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @adminOrOwner()
    async def channel(self, ctx):
        pass

    # channel add command with a cooldown of 1 use every 10 seconds per guild
    @channel.command(help="Adds a channel to a section's allowed channels. It has a cooldown of 10 seconds", description="Arguments: Section Name - Either fanfic/trivia/image/help\nChannel - Mention of the channel which you want to add", usage="channel add (section name) (channel)")
    @adminOrOwner()
    async def add(self, ctx, *args):
        # Run verifier
        result, ID = self.channelVerify(ctx, args)
        if result is True:
            # Arguments are valid
            tempDict = Utils.allowedIDs
            if ID in tempDict[args[0]]:
                # Channel already added
                await ctx.channel.send("Channel is already added")
            else:
                # Channel not added
                newRow = tempDict[args[0]]
                newRow.append(ID)
                tempDict[args[0]] = newRow
                # Write changes
                Utils.idWriter(tempDict)
                await ctx.channel.send("Changes applied. Please refresh the bot")
        else:
            # Arguments are invalid
            await ctx.channel.send(result)

    # channel remove command with a cooldown of 1 use every 10 seconds per guild
    @channel.command(help="Removes a channel from a section's allowed channels. It has a cooldown of 10 seconds", description="Arguments: Section Name - Either fanfic/trivia/image/help\nChanne - Mention of the channel which you want to remove", usage="channel remove (section name) (channel)")
    @adminOrOwner()
    async def remove(self, ctx, *args):
        # Run verifier
        result, ID = self.channelVerify(ctx, args)
        if result is True:
            # Arguments are valid
            tempDict = Utils.allowedIDs
            if not ID in tempDict[args[0]]:
                # Channel not added
                await ctx.channel.send("Channel is not added")
            else:
                # Channel added
                newRow = tempDict[args[0]]
                newRow.remove(ID)
                tempDict[args[0]] = newRow
                # Write changes
                Utils.idWriter(tempDict)
                await ctx.channel.send("Changes applied. Please refresh the bot")
        else:
            # Arguments are invalid
            await ctx.channel.send(result)

    # channel list command with a cooldown of 1 use every 10 seconds per guild
    @channel.command(help="Lists all the channels a section is allowed in. It has a cooldown of 10 seconds", usage="channel list")
    async def list(self, ctx):
        # Create embed
        listEmbed = Embed(title="Restricted Categories", colour=self.colour)
        for key, value in Utils.allowedIDs.items():
            textChannelAllowed = [self.client.get_channel(channel) for channel in value]
            if len([element for element in filter(None, textChannelAllowed) if element.guild.id == ctx.guild.id]) == 0:
                listEmbed.add_field(name=f"{key.capitalize()} Category", value=f"Not setup yet. Use {ctx.prefix}channel to add some", inline=False)
            else:
                guildAllowed = ", ".join([channel.mention for channel in filter(None, textChannelAllowed) if channel.guild.id == ctx.guild.id])
                listEmbed.add_field(name=f"{key.capitalize()} Category", value=guildAllowed, inline=False)
        # Send embed
        await ctx.channel.send(embed=listEmbed)

    # refresh command with a cooldown of 1 use every 30 seconds per guild
    @commands.command(help="Refreshes stored variables used by the bot. The cooldown does not currently work, but please do not over-use this command", usage="refresh")
    @adminOrOwner()
    async def refresh(self, ctx):
        await ctx.channel.send("Refreshing extensions")
        # List to store extension names
        extensions = Utils.extensions
        # Unload all extensions
        for extension in extensions:
            self.client.unload_extension(extension)
        # Refresh allowed IDs
        Utils.allowedIDs = Utils.initIDs()
        # Load all extensions
        for extension in extensions:
            self.client.load_extension(extension)
        await ctx.channel.send("Finished refreshing extensions")

    # about command with a cooldown of 1 use every 10 seconds per guild
    @commands.command(help="Displays information about the bot. It has a cooldown of 10 seconds", usage="about")
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

    # Function to run channelCheck for trivia
    async def cog_check(self, ctx):
        return Utils.channelCheck(ctx, self.allowedIDs)

    # Catch any cog errors
    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.channel.send(f"Command is on cooldown, try again in {round(error.retry_after, 2)} seconds")
        elif isinstance(error, commands.NotOwner):
            await ctx.channel.send("You are not owner")
        elif isinstance(error, commands.CheckFailure):
            textChannelAllowed = [self.client.get_channel(channel) for channel in self.allowedIDs]
            if all(element is None for element in textChannelAllowed):
                await ctx.channel.send(f"No channels added. Use {ctx.prefix}channel to add some or you do not have the sufficient permissions to run this command")
            else:
                guildAllowed = ", ".join([channel.mention for channel in filter(None, textChannelAllowed) if channel.guild.id == ctx.guild.id])
                await ctx.channel.send(f"This command is only allowed in {guildAllowed} or you do not have the sufficient permissions to run this command")
        Utils.errorWrite(error)


# Cog to manage the help command
class Help(commands.HelpCommand):
    # Initialise attributes
    def __init__(self, **options):
        super().__init__(**options)
        self.allowedIDs = Utils.allowedIDs["bot"]
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
                    helpEmbed.add_field(name=f"{cog.qualified_name} Cog", value="\n".join(commandSignatures), inline=False)
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


# Function which initialises the Admin cog
def setup(client):
    client.add_cog(BotStuff(client))