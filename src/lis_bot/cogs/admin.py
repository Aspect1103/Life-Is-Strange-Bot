# Builtin
from typing import Tuple, Union
# Pip
from discord import Colour, Cog, Message
from discord.ext import commands, bridge
# Custom
from lis_bot.helpers.utils import utils


# Custom check for administrator permissions or owner
def adminOrOwner():
    async def predicate(ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext]) -> bool:
        if ctx.author.permissions_in(ctx.channel).administrator:
            return True
        else:
            if ctx.author.id == 538399052895748100:
                return True
            raise commands.MissingPermissions(["Administrator"])
    return commands.check(predicate)


# Cog to manage admin commands
class Admin(Cog):
    def __init__(self, bot: bridge.Bot) -> None:
        self.bot = bot
        self.colour = Colour.orange()

    # Function to verify a channel command
    def channelVerify(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext], sect: str, chnlMent: str) -> Tuple[Union[bool, str], Union[str, None], Union[int, None]]:
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

    # Function which runs once the bot is set up and running
    async def startup(self) -> None:
        pass

    # stop command to stop the bot
    @bridge.bridge_command(description="Stops the bot")
    @commands.is_owner()
    async def stop(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext]) -> None:
        await ctx.respond("Stopping bot")
        await self.bot.close()

    # botrefresh command
    @bridge.bridge_command(aliases=["br"], description="Refreshes stored variables used by the bot")
    @commands.is_owner()
    async def botrefresh(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext]) -> None:
        message: Message = await ctx.respond("Refreshing extensions")
        # Unload all extensions
        for extension in Utils.extensions:
            self.bot.unload_extension(extension)
        # Load all extensions
        for extension in Utils.extensions:
            self.bot.load_extension(extension)
        try:
            message = await message.original_message()
        except AttributeError:
            pass
        await message.edit(content="Refreshed extensions")

    # channelrefresh command with a cooldown of 1 use every 20 seconds per guild
    @bridge.bridge_command(aliases=["cr"], description=f"Refreshes channel IDs")
    @adminOrOwner()
    @commands.cooldown(1, Utils.short, commands.BucketType.guild)
    async def channelrefresh(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext]) -> None:
        Utils.restrictor.IDs = await Utils.restrictor.getIDs()
        await ctx.respond("Refreshed channel IDs")

    # Function to run channelCheck for Admin
    async def cog_check(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext]) -> bool:
        return await Utils.restrictor.commandCheck(ctx)

    # Catch any cog errors
    async def cog_command_error(self, ctx: Union[bridge.BridgeApplicationContext, bridge.BridgeExtContext], error: commands.CommandError) -> None:
        await Utils.errorHandler(ctx, error)


# Function which initialises the Admin cog
def setup(bot: bridge.Bot) -> None:
    bot.add_cog(Admin(bot))
