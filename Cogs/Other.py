# Import libraries
from discord.ext import commands
from datetime import datetime
from discord import Embed
from discord import Colour
import os

# Path variables
rootDirectory = os.path.join(os.path.dirname(__file__), os.pardir)
# Attributes for the help command
attributes = {
    "cooldown": commands.Cooldown(1, 5, commands.BucketType.user),
    "help": "Displays the help command. It has a cooldown of 5 seconds"
}


# Cog to manage other commands
class Other(commands.Cog):
    # Initialise the client
    def __init__(self, client):
        self.client = client
        self.client.help_command = Help(command_attrs=attributes)
        self.client.help_command.cog = self

    # bum command with a cooldown of 1 use every 10 seconds
    @commands.command(help="Displays a hypnotic gif. It has a cooldown of 10 seconds")
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def bum(self, ctx):
        await ctx.channel.send("https://giphy.com/gifs/midland-l4FsJgbbeKQC8MGBy")

    # murica command with a cooldown of 1 use every 10 seconds
    @commands.command(help="Displays a patriot. It has a cooldown of 10 seconds")
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def murica(self, ctx):
        await ctx.channel.send("https://tenor.com/view/merica-gif-9091003")

    # Catch any cog errors
    async def cog_command_error(self, ctx, error):
        errorPath = os.path.join(rootDirectory, "BotFiles", "error.txt")
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.channel.send(f"Command is on cooldown, try again in {round(error.retry_after, 2)} seconds")
        with open(errorPath, "a") as file:
            file.write(f"{datetime.now()}, {error}\n")


# Cog to manage the help command
class Help(commands.HelpCommand):
    # Function to get the command signature (the actual command)
    def get_command_signature(self, command):
        return f"{command.qualified_name} {command.signature} - {command.help}"

    # Function to create aliases string
    def create_alises(self, command):
        aliases = None
        if len(command.aliases) > 0:
            aliases = "Aliases: " + ", ".join(command.aliases)
        return aliases

    # Function to display help on the entire bot
    async def send_bot_help(self, mapping):
        helpEmbed = Embed(title="Help", colour=Colour.teal())
        helpEmbed.set_footer(text=f"Prefix: {self.clean_prefix}")
        # Get iterable dict of each cog and their commands
        for cog, commands in mapping.items():
            commandSignatures = [self.get_command_signature(command) for command in commands]
            # Test if there are any commands. If so, add field
            if commandSignatures:
                helpEmbed.add_field(name=cog.qualified_name, value="\n".join(commandSignatures), inline=False)
        # Send the embed
        channel = self.get_destination()
        await channel.send(embed=helpEmbed)

    # Function to display help on a specific cog
    async def send_cog_help(self, cog):
        # Create embed
        cogHelpEmbed = Embed(title=f"{cog.qualified_name} Help", colour=Colour.teal())
        cogHelpEmbed.set_footer(text=f"Prefix: {self.clean_prefix}")
        for command in cog.get_commands():
            # Create aliases string
            aliases = self.create_alises(command)
            if aliases != None:
                cogHelpEmbed.add_field(name=command.qualified_name, value=f"{command.help}\n\n{aliases}", inline=False)
            else:
                cogHelpEmbed.add_field(name=command.qualified_name, value=f"{command.help}", inline=False)
        # Send embed
        channel = self.get_destination()
        await channel.send(embed=cogHelpEmbed)

    # Function to display help on a specific command
    async def send_command_help(self, command):
        # Create aliases
        aliases = self.create_alises(command)
        # Create embed
        commandHelpEmbed = Embed(title=f"{command.qualified_name} Help", colour=Colour.teal())
        if aliases != None:
            commandHelpEmbed.set_footer(text=aliases)
        if command.description == "":
            commandHelpEmbed.add_field(name=command.help, value="No arguments")
        else:
            commandHelpEmbed.add_field(name=command.name, value=command.description)
        # Send embed
        channel = self.get_destination()
        await channel.send(embed=commandHelpEmbed)

    # Function to handle help error messages
    async def send_error_message(self, error):
        # Create embed
        errorEmbed = Embed(title="Help Error", description=error, colour=Colour.teal())
        # Send embed
        channel = self.get_destination()
        await channel.send(embed=errorEmbed)



# Function which initialises the Secrets cog
def setup(client):
    client.add_cog(Other(client))
