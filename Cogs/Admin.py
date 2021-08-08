# Pip
from discord.ext import commands
from discord import Embed
from discord import Colour
# Custom
from Utils import Utils

# Custom check for administrator permissions or owner
def adminOrOwner():
    async def predicate(ctx):
        if ctx.author.permissions_in(ctx.channel).administrator:
            return True
        else:
            if ctx.author.id == 538399052895748100:
                return True
            raise commands.MissingPermissions(["Administrator"])
    return commands.check(predicate)


# Cog to manage admin commands
class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.colour = Colour.orange()

    # Function to verify a channel command
    def channelVerify(self, ctx, sect, chnlMent):
        if sect is None and chnlMent is None:
            # Too little arguments
            return "Missing arguments", None, None
        else:
            # Correct amount of arguments
            print(sect.lower())
            if sect.lower() in Utils.IDs:
                # Section exists
                channelID = int("".join([str(num) for num in chnlMent if num.isdigit()]))
                if self.client.get_channel(channelID).guild.id == ctx.guild.id:
                    # Valid channel
                    return True, sect.lower(), channelID
                else:
                    # Not a valid channel
                    return "Invalid channel for guild", None, None
            else:
                # Section doesn't exist
                validSections = "/".join(Utils.IDs.keys())
                return f"Section not found. Try {validSections}", None, None

    # stop command to stop the bot
    @commands.command(help="Stops the bot", usage="stop", brief="Bot Stuff")
    @commands.is_owner()
    async def stop(self, ctx):
        await ctx.channel.send("Stopping bot")
        await self.client.close()

    # Base function to initialise the channel group commands with a cooldown of 6 seconds
    @commands.group(invoke_without_command=True, help=f"Group command for adding and removing allowed channels. This command has subcommands. It has a cooldown of {Utils.superShort} seconds", usage="channel", brief="Bot Stuff")
    @commands.cooldown(1, Utils.superShort, commands.BucketType.guild)
    @adminOrOwner()
    async def channel(self, ctx):
        await ctx.send_help(ctx.command)

    # channel add command with a cooldown of 1 use every 20 seconds per guild
    @channel.command(help=f"Adds a channel to a section's allowed channels. It has a cooldown of {Utils.short} seconds", description="\nArguments:\nSection Name - Either bot stuff/fanfic/general/choices/image/trivia\nChannel - Mention of the channel which you want to add", usage="channel add (section name) (channel)", brief="Bot Stuff")
    @commands.cooldown(1, Utils.short, commands.BucketType.guild)
    @adminOrOwner()
    async def add(self, ctx, section=None, channelMent=None):
        # Run verifier
        result, sect, ID = self.channelVerify(ctx, section, channelMent)
        if result is True:
            # Arguments are valid
            tempDict = Utils.IDs
            if ID in tempDict[sect][str(ctx.guild.id)]:
                # Channel already added
                await ctx.channel.send("Channel is already added")
            else:
                # Channel not added
                newRow = tempDict[sect][str(ctx.guild.id)]
                if newRow[0] == -1:
                    del newRow[0]
                newRow.append(ID)
                tempDict[sect][str(ctx.guild.id)] = newRow
                # Write changes
                Utils.idWriter(tempDict)
                await ctx.channel.send("Changes applied")
        else:
            # Arguments are invalid
            await ctx.channel.send(result)

    # channel remove command with a cooldown of 1 use every 20 seconds per guild
    @channel.command(help=f"Removes a channel from a section's allowed channels. It has a cooldown of {Utils.short} seconds", description="\nArguments:\nSection Name - Either bot stuff/fanfic/general/choices/image/trivia\nChannel - Mention of the channel which you want to add", usage="channel remove (section name) (channel)", brief="Bot Stuff")
    @commands.cooldown(1, Utils.short, commands.BucketType.guild)
    @adminOrOwner()
    async def remove(self, ctx, section=None, channelMent=None):
        # Run verifier
        result, sect, ID = self.channelVerify(ctx, section, channelMent)
        if result is True:
            # Arguments are valid
            tempDict = Utils.IDs
            if ID not in tempDict[sect][str(ctx.guild.id)]:
                # Channel not added
                await ctx.channel.send("Channel is not added")
            else:
                # Channel added
                newRow = tempDict[sect][str(ctx.guild.id)]
                newRow.remove(ID)
                if len(newRow) == 0:
                    newRow.append(-1)
                tempDict[sect][str(ctx.guild.id)] = newRow
                # Write changes
                Utils.idWriter(tempDict)
                await ctx.channel.send("Changes applied")
        else:
            # Arguments are invalid
            await ctx.channel.send(result)

    # channel list command with a cooldown of 1 use every 20 seconds per guild
    @channel.command(help=f"Lists all the channels a section is allowed in. It has a cooldown of {Utils.short} seconds", usage="channel list", brief="Bot Stuff")
    @commands.cooldown(1, Utils.short, commands.BucketType.guild)
    async def list(self, ctx):
        # Create embed
        listEmbed = Embed(title="Restricted Categories/Commmands", colour=self.colour)
        for key, value in Utils.IDs.items():
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

    # botRefresh command
    @commands.command(aliases=["br"], help="Refreshes stored variables used by the bot", usage="botRefresh|br", brief="Bot Stuff")
    @commands.is_owner()
    async def botRefresh(self, ctx):
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

    # channelRefresh command with a cooldown of 1 use every 20 seconds per guild
    @commands.command(aliases=["cr"], help=f"Refreshes channel IDs. It has a cooldown of {Utils.short} seconds", usage="channelRefresh|cr", brief="Bot Stuff")
    @commands.cooldown(1, Utils.short, commands.BucketType.guild)
    @adminOrOwner()
    async def channelRefresh(self, ctx):
        await ctx.channel.send("Refreshing channel IDs")
        Utils.restrictor.IDs = Utils.initIDs()
        await ctx.channel.send("Finished channel IDs")

    # Function to run channelCheck for Admin
    async def cog_check(self, ctx):
        return await Utils.restrictor.commandCheck(ctx)

    # Catch any cog errors
    async def cog_command_error(self, ctx, error):
        await Utils.errorHandler(ctx, error)


# Function which initialises the Admin cog
def setup(client):
    client.add_cog(Admin(client))
