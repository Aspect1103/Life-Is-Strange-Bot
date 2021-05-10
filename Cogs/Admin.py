# Pip
from discord.ext import commands
from discord import Embed
from discord import Colour
# Custom
from Utils.Restrictor import Restrictor
from Utils import Utils


# Cog to manage admin commands
class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.colour = Colour.orange()
        self.commandGroups = {"stop": "bot stuff", "channel": "bot stuff", "channel add": "bot stuff", "channel remove": "bot stuff", "channel list": "bot stuff", "refresh": "bot stuff"}
        self.restrictor = Restrictor(self.client, self.commandGroups)
        self.allowedIDs = None

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
    @commands.command(help="Stops the bot", usage="stop", brief="Bot Stuff")
    @commands.is_owner()
    async def stop(self, ctx):
        print(ctx.command)
        await ctx.channel.send("Stopping bot")
        await self.client.close()

    # Base function to initialise the channel group commands
    @commands.group(invoke_without_command=True, help="Group command for adding and removing allowed channels. This command has subcommads. It has a cooldown of 10 seconds", usage="channel", brief="Bot Stuff")
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.is_owner()
    async def channel(self, ctx):
        pass

    # channel add command with a cooldown of 1 use every 10 seconds per guild
    @channel.command(help="Adds a channel to a section's allowed channels. It has a cooldown of 10 seconds", description=f"Arguments: Section Name - Either admin/fanfic/general/choices/image/trivia\nChannel - Mention of the channel which you want to add", usage="channel add (section name) (channel)", brief="Bot Stuff")
    @commands.is_owner()
    async def add(self, ctx, *args):
        # Run verifier
        result, ID = self.channelVerify(ctx, args)
        if result is True:
            # Arguments are valid
            tempDict = Utils.allowedIDs
            if ID in tempDict[args[0]][str(ctx.guild.id)]:
                # Channel already added
                await ctx.channel.send("Channel is already added")
            else:
                # Channel not added
                newRow = tempDict[args[0]][str(ctx.guild.id)]
                if newRow[0] == -1:
                    del newRow[0]
                newRow.append(ID)
                tempDict[args[0]][str(ctx.guild.id)] = newRow
                # Write changes
                Utils.idWriter(tempDict)
                await ctx.channel.send("Changes applied. Please refresh the bot")
        else:
            # Arguments are invalid
            await ctx.channel.send(result)

    # channel remove command with a cooldown of 1 use every 10 seconds per guild
    @channel.command(help="Removes a channel from a section's allowed channels. It has a cooldown of 10 seconds", description="Arguments: Section Name - Either admin/fanfic/general/choices/image/trivia\nChannel - Mention of the channel which you want to remove", usage="channel remove (section name) (channel)", brief="Bot Stuff")
    @commands.is_owner()
    async def remove(self, ctx, *args):
        # Run verifier
        result, ID = self.channelVerify(ctx, args)
        if result is True:
            # Arguments are valid
            tempDict = Utils.allowedIDs
            if not ID in tempDict[args[0]][str(ctx.guild.id)]:
                # Channel not added
                await ctx.channel.send("Channel is not added")
            else:
                # Channel added
                newRow = tempDict[args[0]][str(ctx.guild.id)]
                newRow.remove(ID)
                if len(newRow) == 0:
                    newRow.append(-1)
                tempDict[args[0]][str(ctx.guild.id)] = newRow
                # Write changes
                Utils.idWriter(tempDict)
                await ctx.channel.send("Changes applied. Please refresh the bot")
        else:
            # Arguments are invalid
            await ctx.channel.send(result)

    # channel list command with a cooldown of 1 use every 10 seconds per guild
    @channel.command(help="Lists all the channels a section is allowed in. It has a cooldown of 10 seconds", usage="channel list", brief="Bot Stuff")
    async def list(self, ctx):
        # Create embed
        listEmbed = Embed(title="Restricted Categories/Commmands", colour=self.colour)
        for key, value in Utils.allowedIDs.items():
            if value[str(ctx.guild.id)][0] == -1:
                # Command/category allowed everywhere not restricted
                listEmbed.add_field(name=f"{key.title()}", value="This command is allowed everywhere. Enjoy!", inline=False)
            else:
                # Command/category restricted
                textChannelAllowed = [self.client.get_channel(channel) for channel in value[str(ctx.guild.id)]]
                if len([element for element in filter(None, textChannelAllowed)]) == 0:
                    listEmbed.add_field(name=f"{key.title()}", value=f"Not setup yet. Use {ctx.prefix}channel to add some", inline=False)
                else:
                    guildAllowed = ", ".join([channel.mention for channel in filter(None, textChannelAllowed)])
                    listEmbed.add_field(name=f"{key.title()}", value=guildAllowed, inline=False)
        # Send embed
        await ctx.channel.send(embed=listEmbed)

    # refresh command with a cooldown of 1 use every 30 seconds per guild
    @commands.command(help="Refreshes stored variables used by the bot. The cooldown does not currently work, but please do not over-use this command", usage="refresh", brief="Bot Stuff")
    @commands.is_owner()
    async def refresh(self, ctx):
        await ctx.channel.send("Refreshing extensions")
        # List to store extension names
        extensions = Utils.extensions
        # Unload all extensions
        for extension in extensions:
            self.client.unload_extension(extension)
        # Load all extensions
        for extension in extensions:
            self.client.load_extension(extension)
        await ctx.channel.send("Finished refreshing extensions")

    # Function to run channelCheck for trivia
    async def cog_check(self, ctx):
        result = await self.restrictor.commandCheck(ctx)
        return result

    # Catch any cog errors
    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            result = await self.restrictor.grabAllowed(ctx)
            await ctx.channel.send(result)
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.channel.send(f"Command is on cooldown, try again in {round(error.retry_after, 2)} seconds")
        elif isinstance(error, commands.NotOwner):
            await ctx.channel.send("You are not owner")
        Utils.errorWrite(error)


# Function which initialises the Admin cog
def setup(client):
    client.add_cog(Admin(client))