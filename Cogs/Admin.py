# Builtin
from typing import Tuple, Union
# Pip
from discord import Colour, Bot, Cog, command, ApplicationContext
from discord.ext import commands
# Custom
from Helpers.Utils import Utils


# Custom check for administrator permissions or owner
def adminOrOwner():
    async def predicate(ctx: ApplicationContext) -> bool:
        if ctx.author.permissions_in(ctx.channel).administrator:
            return True
        else:
            if ctx.author.id == 538399052895748100:
                return True
            raise commands.MissingPermissions(["Administrator"])
    return commands.check(predicate)


# Cog to manage admin commands
class Admin(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.colour = Colour.orange()

    # Function to verify a channel command
    def channelVerify(self, ctx: ApplicationContext, sect: str, chnlMent: str) -> Tuple[Union[bool, str], Union[str, None], Union[int, None]]:
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
    @command(description="Stops the bot", check=commands.is_owner)
    async def stop(self, ctx: ApplicationContext) -> None:
        await ctx.respond("Stopping bot")
        await self.bot.close()

    # botRefresh command
    @command(description="Refreshes stored variables used by the bot", check=commands.is_owner)
    async def botrefresh(self, ctx: ApplicationContext) -> None:
        interaction = await ctx.respond("Refreshing extensions")
        # Unload all extensions
        for extension in Utils.extensions:
            self.bot.unload_extension(extension)
        # Load all extensions
        for extension in Utils.extensions:
            self.bot.load_extension(extension)
        message = await interaction.original_message()
        await message.edit("Refreshed extensions")

    # channelRefresh command with a cooldown of 1 use every 20 seconds per guild
    @command(description=f"Refreshes channel IDs", check=adminOrOwner)
    @commands.cooldown(1, Utils.short, commands.BucketType.guild)
    async def channelrefresh(self, ctx: ApplicationContext) -> None:
        Utils.restrictor.IDs = await Utils.restrictor.getIDs()
        await ctx.respond("Refreshed channel IDs")

    # Function to run channelCheck for Admin
    async def cog_check(self, ctx: ApplicationContext) -> bool:
        return await Utils.restrictor.commandCheck(ctx)

    # Catch any cog errors
    async def cog_command_error(self, ctx: ApplicationContext, error: commands.CommandError) -> None:
        await Utils.errorHandler(ctx, error)


# Function which initialises the Admin cog
def setup(bot: Bot) -> None:
    bot.add_cog(Admin(bot))
