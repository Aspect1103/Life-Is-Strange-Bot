# Builtin
from datetime import datetime
from pathlib import Path
import random
# Pip
from discord.ext.commands import Context, Bot
from discord import Colour, Embed, Reaction
# Custom
from Helpers.Utils import Utils

# Path variables
rootDirectory = Path(__file__).parent.parent.parent
lisWordsPath = rootDirectory.joinpath("Resources").joinpath("Files").joinpath("lisWords.txt")


# Hangman class to play LiS hangman in a discord channel
class Hangman:
    # Initialise variables
    def __init__(self, ctx: Context, bot: Bot, color: Colour) -> None:
        self.ctx = ctx
        self.bot = bot
        self.colour = color
        self.gameID = 3
        self.images = [
            "https://i.imgur.com/Lb0LwVY",
            "https://i.imgur.com/JrIiOGl",
            "https://i.imgur.com/88PPAod",
            "https://i.imgur.com/6SgiO13",
            "https://i.imgur.com/zBAK9xm",
            "https://i.imgur.com/3TYqwNV",
            "https://i.imgur.com/lNLX9GR"
        ]
        self.words = [word.replace("\n", "") for word in open(lisWordsPath, "r").readlines()]
        self.guessedLetters = []
        self.chosenWord = random.choice(self.words).lower()
        self.title = ["-"]*len(self.chosenWord)
        self.gameEmojis = ["🛑"]
        self.user = self.ctx.author
        self.lastActivity = datetime.now()
        self.totalTries = 6
        self.incorrectGuesses = 0
        self.correctGuesses = 0
        self.guesses = 0
        self.isPlaying = True
        self.gameMessage = None
        self.result = None

    # Function to return the game name
    def __repr__(self) -> str:
        return "Hangman"

    # Create the title for the embed
    def createTitle(self) -> str:
        if self.isPlaying:
            temp = "".join(self.title).capitalize()
            return f"Connect 4 - {temp}"
        else:
            if self.result == "Win":
                return f"You Win. The Correct Word Was {self.chosenWord.capitalize()}"
            else:
                return f"You Lose. The Correct Word Was {self.chosenWord.capitalize()}"

    # Check for a win or lose
    def winCheck(self) -> None:
        if "".join(self.title) == self.chosenWord:
            self.isPlaying = False
            self.result = "Win"
        elif self.incorrectGuesses == self.totalTries:
            self.isPlaying = False
            self.result = "Lose"

    # Function to process a reaction from the gameManager
    def processReaction(self, _: Reaction) -> None:
        self.isPlaying = False
        self.result = "Lose"

    # Update the embed
    async def embedUpdate(self) -> None:
        # Update the message with the guessed letter, try count and the new image
        hangmanEmbed = Embed(title=self.createTitle(), colour=self.colour)
        if len(self.guessedLetters) == 0:
            hangmanEmbed.add_field(name="Guessed Letters", value="None Yet")
        else:
            hangmanEmbed.add_field(name="Guessed Letters", value=",".join(self.guessedLetters))
        hangmanEmbed.add_field(name="Incorrect Guesses", value=str(self.incorrectGuesses))
        hangmanEmbed.add_field(name="Total Guesses", value=str(self.guesses))
        hangmanEmbed.set_image(url=self.images[self.incorrectGuesses])
        await self.gameMessage.edit(embed=hangmanEmbed)

    # Make a guess of one of the characters
    async def guess(self, guessCharacter: str) -> None:
        if guessCharacter is None:
            await Utils.commandDebugEmbed(self.ctx.channel, "Make sure a character is being guessed")
        else:
            self.lastActivity = datetime.now()
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
