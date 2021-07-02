# Builtin
import asyncio
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
            "https://imgur.com/Lb0LwVY.png",
            "https://imgur.com/JrIiOGl.png",
            "https://imgur.com/88PPAod.png",
            "https://imgur.com/6SgiO13.png",
            "https://imgur.com/zBAK9xm.png",
            "https://imgur.com/3TYqwNV.png",
            "https://imgur.com/lNLX9GR.png"
        ]
        self.words = [word.replace("\n", "") for word in open(hangmanWordsPath, "r").readlines()]
        self.guessedLetters = []
        self.chosenWord = random.choice(self.words).lower()
        self.title = ["-"]*len(self.chosenWord)
        self.totalTries = 6
        self.incorrectGuesses = 0
        self.correctGuesses = 0
        self.guesses = 0
        self.isPlaying = True
        self.user = self.ctx.author
        self.message = None
        self.result = None

    # Check a reaction
    def checkMove(self, reaction, user):
        return reaction.message.id == self.message.id and self.user.id == user.id and str(reaction) == "🛑"

    # Create the title for the embed
    def createTitle(self):
        if self.isPlaying:
            return "".join(self.title).capitalize()
        else:
            if self.result:
                return f"You Win. The Correct Word Was {self.chosenWord.capitalize()}"
            else:
                return f"You Lose. The Correct Word Was {self.chosenWord.capitalize()}"

    # Check for a win or lose
    def winCheck(self):
        if "".join(self.title) == self.chosenWord:
            self.isPlaying = False
            self.result = True
        elif self.incorrectGuesses == self.totalTries:
            self.isPlaying = False
            self.result = False

    # Update the embed
    async def embedUpdate(self):
        # Update the message with guessed letter, try count and the new image
        hangmanEmbed = Embed(title=self.createTitle(), colour=self.colour)
        if len(self.guessedLetters) == 0:
            hangmanEmbed.add_field(name="Guessed Letters", value="None Yet")
        else:
            hangmanEmbed.add_field(name="Guessed Letters", value=",".join(self.guessedLetters))
        hangmanEmbed.add_field(name="Incorrect Guesses", value=str(self.incorrectGuesses))
        hangmanEmbed.add_field(name="Total Guesses", value=str(self.guesses))
        hangmanEmbed.set_image(url=self.images[self.incorrectGuesses])
        await self.message.edit(embed=hangmanEmbed)

    # Start the game
    async def start(self):
        # Send initial message and then wait for a stop response
        self.message = await self.ctx.channel.send(embed=Embed(title="Initialising, please wait", colour=self.colour))
        await self.message.add_reaction("🛑")
        await self.embedUpdate()
        while self.isPlaying:
            try:
                reaction, user = await self.client.wait_for("reaction_add", timeout=0.5, check=self.checkMove)
                self.isPlaying = False
                self.result = False
                await self.embedUpdate()
            except asyncio.TimeoutError:
                continue

    # Make a guess of one of the characters
    async def guess(self, args):
        if len(args) == 0 or len(args) > 1:
            await self.ctx.channel.send("Make sure there is only one character being guessed")
        else:
            userGuess = args[0].lower()
            self.guesses += 1
            self.guessedLetters.append(userGuess)
            correct = 0
            for count, letter in enumerate(self.chosenWord):
                if userGuess == letter:
                    correct += 1
                    self.correctGuesses += 1
                    self.title[count] = letter
            if correct == 0:
                self.incorrectGuesses += 1
            self.winCheck()
            await self.embedUpdate()
