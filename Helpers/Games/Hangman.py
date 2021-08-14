# Builtin
from datetime import datetime
from pathlib import Path
import asyncio
import random
# Pip
from discord.ext.commands import Context
from discord import Client
from discord import Colour
from discord import Embed
# Custom
from Helpers.Utils import Utils

# Path variables
rootDirectory = Path(__file__).parent.parent.parent
hangmanWordsPath = rootDirectory.joinpath("Resources").joinpath("Files").joinpath("hangman.txt")
imagePath = rootDirectory.joinpath("Resources").joinpath("Images").joinpath("Hangman")


# Hangman class to play LiS hangman in a discord channel
class Hangman:
    # Initialise variables
    def __init__(self, ctx: Context, client: Client, color: Colour):
        self.ctx = ctx
        self.client = client
        self.colour = color
        self.images = [
            imagePath.joinpath("1.png"),
            imagePath.joinpath("2.png"),
            imagePath.joinpath("3.png"),
            imagePath.joinpath("4.png"),
            imagePath.joinpath("5.png"),
            imagePath.joinpath("6.png"),
            imagePath.joinpath("7.png")
        ]
        self.words = [word.replace("\n", "") for word in open(hangmanWordsPath, "r").readlines()]
        self.guessedLetters = []
        self.chosenWord = random.choice(self.words).lower()
        self.title = ["-"]*len(self.chosenWord)
        self.user = self.ctx.author
        self.lastGuess = datetime.now()
        self.totalTries = 6
        self.incorrectGuesses = 0
        self.correctGuesses = 0
        self.guesses = 0
        self.isPlaying = True
        self.timeout = None
        self.gameMessage = None
        self.result = None

    # Function to return the game name
    def __repr__(self):
        return "Hangman"

    # Check a reaction
    def checkMove(self, reaction, user):
        return reaction.message.id == self.gameMessage.id and self.user.id == user.id and str(reaction) == "🛑"

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
        hangmanEmbed.set_image(url=str(self.images[self.incorrectGuesses]))
        await self.gameMessage.edit(embed=hangmanEmbed)

    # Start the game
    async def start(self):
        # Send initial message and then wait for a stop response
        self.gameMessage = await self.ctx.channel.send(embed=Embed(title="Initialising, please wait", colour=self.colour))
        await self.gameMessage.add_reaction("🛑")
        await self.embedUpdate()
        while self.isPlaying:
            # Test if the game has been idle for 5 minutes
            if Utils.gameActivity(self.lastGuess):
                self.isPlaying = False
                await Utils.commandDebugEmbed(self.ctx.channel, False, "Game has timed out")
            else:
                try:
                    reaction, user = await self.client.wait_for("reaction_add", timeout=1, check=self.checkMove)
                    self.isPlaying = False
                except asyncio.TimeoutError:
                    continue
        # Game has either timed out or user has stopped it
        if self.result is None:
            self.result = False
            await self.embedUpdate()

    # Make a guess of one of the characters
    async def guess(self, guessCharacter):
        if guessCharacter is None:
            await self.ctx.channel.send("Make sure a character is being guessed")
        else:
            self.lastGuess = datetime.now()
            userGuess = guessCharacter.lower()
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
