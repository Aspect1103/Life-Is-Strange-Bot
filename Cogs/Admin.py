from discord.ext import commands

# Cog to manage other commands
class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Function to stop the bot
    @commands.command(aliases=["stop"], help="Stops the bot")
    @commands.is_owner()
    async def stop_s(self, ctx):
        await ctx.channel.send("Stopping bot")
        await self.client.close()


# Function which initialises the Admin cog
def setup(client):
    client.add_cog(Admin(client))