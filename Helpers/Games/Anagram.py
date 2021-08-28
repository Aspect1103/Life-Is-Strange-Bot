# Builtin
import random
from datetime import datetime
from pathlib import Path
# Pip
from discord import Colour, Embed, Reaction
from discord.ext.commands import Context, Bot
# Custom
from Helpers.Utils import Utils

# Path variables
rootDirectory = Path(__file__).parent.parent.parent
lisWordsPath = rootDirectory.joinpath("Resources").joinpath("Files").joinpath("lisWords.txt")


# Anagram class to play a LiS anagram puzzle game
class Anagram:
    # Initialise variables
    def __init__(self, ctx: Context, client: Bot, color: Colour) -> None:
        self.ctx = ctx
        self.client = client
        self.colour = color
        self.ID = 4
        self.words = self.words = [word.replace("\n", "") for word in open(lisWordsPath, "r").readlines()]
        self.chosenWord = random.choice(self.words).lower()
        self.anagram = self.setupAnagram()
        self.user = self.ctx.author
        self.startTime = datetime.now()
        self.lastActivity = self.startTime
        self.gameEmojis = ["🛑"]
        self.guesses = []
        self.totalGuesses = 0
        self.isPlaying = True
        self.gameMessage = None
        self.result = None

    # Function to return the game name
    def __repr__(self) -> str:
        return "Anagram"

    # Function to setup the anagram
    def setupAnagram(self) -> str:
        temp = list(self.chosenWord)
        random.shuffle(temp)
        return "".join(temp)

    # Create the title for the embed
    def createTitle(self) -> str:
        if self.isPlaying:
            return f"Anagram - {self.anagram.capitalize()}"
        else:
            if self.result == "Win":
                return f"You Win. {self.anagram.capitalize()} Is An Anagram Of {self.chosenWord.capitalize()}"
            else:
                return f"You Lose. {self.anagram.capitalize()} Is An Anagram Of {self.chosenWord.capitalize()}"

    # Function to process a reaction from the gameManager
    def processReaction(self, _: Reaction) -> None:
        self.isPlaying = False
        self.result = "Lose"

    # Update the embed
    async def embedUpdate(self) -> None:
        # Update the embed with the total guesses
        anagramEmbed = Embed(title=self.createTitle(), colour=self.colour)
        if len(self.guesses) == 0:
            anagramEmbed.add_field(name="Guesses Words", value="None Yet")
        else:
            anagramEmbed.add_field(name="Guesses Words", value=", ".join(self.guesses))
        anagramEmbed.add_field(name="Total Guesses", value=str(self.totalGuesses))
        if not self.isPlaying:
            totalTime = datetime.now()-self.startTime
            anagramEmbed.add_field(name="Total Time", value=f"{str(round(totalTime.total_seconds(), 2))} Seconds")
        await self.gameMessage.edit(embed=anagramEmbed)

    # Make a guess of the anagram
    async def guess(self, word: str) -> None:
        if word is None:
            await Utils.commandDebugEmbed(self.ctx.channel, "Make sure a character is being guessed")
        else:
            self.lastActivity = datetime.now()
            self.guesses.append(word.capitalize())
            self.totalGuesses += 1
            userGuess = word.lower()
            if userGuess == self.chosenWord:
                self.isPlaying = False
                self.result = "Win"
            await self.embedUpdate()
