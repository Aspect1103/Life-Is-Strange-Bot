# Builtin
import os
import random
# Pip
from discord.ext.commands import Context
from discord import Client
from discord import Colour

# Path variables
rootDirectory = os.path.join(os.path.dirname(__file__), os.pardir)
hangmanWordsPath = os.path.join(rootDirectory, "Resources", "hangman.txt")
hangmanImagePath = os.path.join(rootDirectory, "Resources", "hangmanImages")


# Hangman class to play LiS hangman in a discord channel
class Hangman:
    # Initialise variables
    def __init__(self, ctx: Context, client: Client, color: Colour):
        if isinstance(ctx, Context) and isinstance(client, Client) and isinstance(color, Colour):
            self.ctx = ctx
            self.client = client
            self.colour = color
        else:
            raise TypeError("Invalid parameters")
        self.images = os.listdir(hangmanImagePath)
        self.words = [word.replace("\n", "") for word in open(hangmanWordsPath, "r").readlines()]
        self.message = None
        self.chosenWord = None
        self.guessedLetters = []

    # Start the game
    async def start(self):
        pass

    # Make a guess of one of the characters
    async def guess(self):
        pass

    # Update the embed
    async def embedUpdate(self):
        pass
