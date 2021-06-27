# Builtin
import os
import random
# Pip
from discord.ext.commands import Context
from discord import Client
from discord import Colour
from discord import Embed

# Path variables
rootDirectory = os.path.join(os.path.dirname(__file__), os.pardir)
hangmanWordsPath = os.path.join(rootDirectory, "Resources", "hangman.txt")


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
        self.images = [
            "https://imgur.com/Lb0LwVY",
            "https://imgur.com/JrIiOGl",
            "https://imgur.com/88PPAod",
            "https://imgur.com/6SgiO13",
            "https://imgur.com/zBAK9xm",
            "https://imgur.com/3TYqwNV",
            "https://imgur.com/lNLX9GR"
        ]
        self.words = [word.replace("\n", "") for word in open(hangmanWordsPath, "r").readlines()]
        self.message = None
        self.chosenWord = None
        self.isPlaying = True
        self.guessedLetters = []
        self.incorrectGuesses = 0

    # Create hangman embed title
    def createTitle(self):
        result = ["-"]*len(self.chosenWord)
        for letter in self.guessedLetters:
            if letter in self.chosenWord:
                # Find index in self.chosenWord
                result[self.chosenWord.index(letter)] = letter
        return "".join(result)

    # Function to check a reaction
    def checkMove(self, reaction, user):
        return reaction.message.id == self.message.id and str(reaction) == "🛑"

    # Start the game
    async def start(self):
        # Grab random word and create initial message
        self.chosenWord = list(self.words[random.randint(0, len(self.words)-1)])
        self.message = await self.ctx.channel.send(embed=Embed(title="Initialising, please wait", colour=self.colour))
        await self.message.add_reaction("🛑")
        await self.embedUpdate()
        while self.isPlaying:
            reaction, user = await self.client.wait_for("reaction_add", check=self.checkMove)
            self.isPlaying = False
            await self.message.clear_reactions()

    # Update the embed
    async def embedUpdate(self):
        # Update the message with guessed letter, try count and the new image
        hangmanEmbed = Embed(title=self.createTitle(), colour=self.colour)
        if len(self.guessedLetters) == 0:
            hangmanEmbed.add_field(name="Guessed Letters", value="None Yet")
        else:
            hangmanEmbed.add_field(name="Guessed Letters", value=",".join(self.guessedLetters))
        hangmanEmbed.add_field(name="Tries Left", value=str(6-self.incorrectGuesses))
        hangmanEmbed.set_image(url=self.images[self.incorrectGuesses])
        await self.message.edit(embed=hangmanEmbed)

    # Make a guess of one of the characters
    async def guess(self):
        pass
