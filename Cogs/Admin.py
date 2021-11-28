# Builtin
from typing import Tuple, Union, List
# Pip
from discord import Embed, Colour, TextChannel, VoiceChannel
from discord.ext import commands
# Custom
from Helpers.Utils import Utils


# Custom check for administrator permissions or owner
def adminOrOwner():
    async def predicate(ctx: commands.Context) -> bool:
        if ctx.author.permissions_in(ctx.channel).administrator:
            return True
        else:
            if ctx.author.id == 538399052895748100:
                return True
            raise commands.MissingPermissions(["Administrator"])
    return commands.check(predicate)


# Cog to manage admin commands
class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.colour = Colour.orange()

    # Function to verify a channel command
    def channelVerify(self, ctx: commands.Context, sect: str, chnlMent: str) -> Tuple[Union[bool, str], Union[str, None], Union[int, None]]:
        if sect is None and chnlMent is None:
            # Too little arguments
            return "Missing arguments", None, None
        else:
            # Correct amount of arguments
            if sect.lower() in Utils.IDs:
                # Section exists
                channelID = int("".join([str(num) for num in chnlMent if num.isdigit()]))
                if self.bot.get_channel(channelID).guild.id == ctx.guild.id:
                    # Valid channel
                    return True, sect.lower(), channelID
                else:
                    # Not a valid channel
                    return "Invalid channel for guild", None, None
            else:
                # Section doesn't exist
                validSections = "/".join(Utils.IDs.keys())
                return f"Section not found. Try {validSections}", None, None

    # Function which runs once the bot is setup and running
    async def startup(self) -> None:
        pass

    # stop command to stop the bot
    @commands.command(help="Stops the bot", usage="stop", brief="Bot Bidness")
    @commands.is_owner()
    async def stop(self, ctx: commands.Context) -> None:
        await ctx.channel.send("Stopping bot")
        await self.bot.close()

    # botRefresh command
    @commands.command(aliases=["br"], help="Refreshes stored variables used by the bot", usage="botRefresh|br", brief="Bot Bidness")
    @commands.is_owner()
    async def botRefresh(self, ctx: commands.Context) -> None:
        await Utils.commandDebugEmbed(ctx.channel, "Refreshing extensions")
        # List to store extension names
        extensions = Utils.extensions
        # Unload all extensions
        for extension in extensions:
            self.bot.unload_extension(extension)
        # Load all extensions
        for extension in extensions:
            self.bot.load_extension(extension)
        await Utils.commandDebugEmbed(ctx.channel, "Finished refreshing extensions")

    # channelRefresh command with a cooldown of 1 use every 20 seconds per guild
    @commands.command(aliases=["cr"], help=f"Refreshes channel IDs. It has a cooldown of {Utils.short} seconds", usage="channelRefresh|cr", brief="Bot Bidness")
    @commands.cooldown(1, Utils.short, commands.BucketType.guild)
    @adminOrOwner()
    async def channelRefresh(self, ctx: commands.Context) -> None:
        await Utils.commandDebugEmbed(ctx.channel, "Refreshing channel IDs")
        Utils.restrictor.IDs = await Utils.restrictor.getIDs()
        await Utils.commandDebugEmbed(ctx.channel, "Finished channel IDs")

    # Function to run channelCheck for Admin
    async def cog_check(self, ctx: commands.Context) -> bool:
        return await Utils.restrictor.commandCheck(ctx)

    # Catch any cog errors
    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        await Utils.errorHandler(ctx, error)


# Function which initialises the Admin cog
def setup(bot: commands.Bot) -> None:
    bot.add_cog(Admin(bot))
