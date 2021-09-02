# Builtin
import random
import copy
from typing import List
from datetime import datetime
# Pip
from discord import Embed, Colour, Reaction
from discord.ext.commands import Context, Bot
# Custom
from Helpers.Utils import Utils


# Sokoban class to play a randomly generated Sokoban game in a discord channel
class Sokoban:
    """
    Grid Numbers:
        0 - Empty space
        1 - Walls
        2 - Box
        3 - Destination
        4 - Player
    """
    def __init__(self, ctx: Context, bot: Bot, colour: Colour) -> None:
        self.ctx = ctx
        self.bot = bot
        self.colour = colour
        self.gameID = 5
        self.user = self.ctx.author
        self.gameEmojis = ["⬅️", "➡️", "⬆️", "⬇️", "🔁", "🛑"]
        self.gridEmojis = ["\U00002B1B", "\U0001F7EB", "\U0000274C", "\U0001F602"]
        self.wallColours = ["\U0001F7E6", "\U0001F7E5", "\U0001F7E7", "\U0001F7E8", "\U0001F7E9", "\U0001F7EA"]
        self.gameColour = random.choice(self.wallColours)
        self.lastActivity = datetime.now()
        self.isPlaying = True
        self.gameMessage = None
        self.orgPlayerPos = None
        self.playerPos = None
        self.orgGrid = None
        self.grid = None
        self.remainingBoxes = None
        self.level = None
        self.result = None

    # Function to return the game name
    def __repr__(self) -> str:
        return "Sokoban"

    # Function to check if a position for the grid is valid or not
    def positionChecker(self, grid: List[List[int]], positionX: int, positionY: int, isBox: bool = False) -> bool:
        # Check if the position is a corner (only for boxes)
        if isBox:
            if positionX < 2 or positionX > len(grid[0])-3 or positionY < 2 or positionY > len(grid)-3:
                # Position is corner
                return False
        # Check if the position is taken
        if grid[positionY][positionX] != 0:
            # Position is taken
            return False
        return True

    # Function to check if a box can move
    def checkBox(self, position: List[int]) -> bool:
        return False if self.grid[position[1]][position[0]] == 1 or self.grid[position[1]][position[0]] == 2 else True

    # Function to check if the new box position is a destination
    def checkDestination(self, position: List[int]) -> None:
        if self.grid[position[1]][position[0]] == 3:
            self.grid[position[1]][position[0]] = 1
            self.remainingBoxes -= 1
        else:
            self.grid[position[1]][position[0]] = 2

    # Function to check if the player has beaten the level
    def winCheck(self) -> None:
        if self.remainingBoxes == 0:
            self.isPlaying = False
            self.result = ("Win", None)

    # Function to get the title for the embed
    def getTitle(self) -> str:
        if self.isPlaying:
            return f"Sokoban - Level {self.level}"
        else:
            if self.result[0] == "Win":
                return "Sokoban - You Win!"
            elif self.result[0] == "Timeout":
                return "Sokoban - Timeout"
            elif self.result[0] == "Stop":
                return "Sokoban - Stopped"

    # Function to process a reaction from the gameManager
    def processReaction(self, reaction: Reaction) -> None:
        if str(reaction) == self.gameEmojis[0] and self.grid[self.playerPos[1]][self.playerPos[0]-1] != 1:
            if self.grid[self.playerPos[1]][self.playerPos[0]-1] == 2:
                if self.checkBox([self.playerPos[0]-2, self.playerPos[1]]):
                    self.checkDestination([self.playerPos[0]-2, self.playerPos[1]])
                    self.grid[self.playerPos[1]][self.playerPos[0]-1] = 0
                    self.playerPos = [self.playerPos[0]-1, self.playerPos[1]]
            else:
                self.playerPos = [self.playerPos[0]-1, self.playerPos[1]]
        elif str(reaction) == self.gameEmojis[1] and self.grid[self.playerPos[1]][self.playerPos[0]+1] != 1:
            if self.grid[self.playerPos[1]][self.playerPos[0]+1] == 2:
                if self.checkBox([self.playerPos[0]+2, self.playerPos[1]]):
                    self.checkDestination([self.playerPos[0]+2, self.playerPos[1]])
                    self.grid[self.playerPos[1]][self.playerPos[0]+1] = 0
                    self.playerPos = [self.playerPos[0]+1, self.playerPos[1]]
            else:
                self.playerPos = [self.playerPos[0]+1, self.playerPos[1]]
        elif str(reaction) == self.gameEmojis[2] and self.grid[self.playerPos[1]-1][self.playerPos[0]] != 1:
            if self.grid[self.playerPos[1]-1][self.playerPos[0]] == 2:
                if self.checkBox([self.playerPos[0], self.playerPos[1]-2]):
                    self.checkDestination([self.playerPos[0], self.playerPos[1]-2])
                    self.grid[self.playerPos[1]-1][self.playerPos[0]] = 0
                    self.playerPos = [self.playerPos[0], self.playerPos[1]-1]
            else:
                self.playerPos = [self.playerPos[0], self.playerPos[1]-1]
        elif str(reaction) == self.gameEmojis[3] and self.grid[self.playerPos[1]+1][self.playerPos[0]] != 1:
            if self.grid[self.playerPos[1]+1][self.playerPos[0]] == 2:
                if self.checkBox([self.playerPos[0], self.playerPos[1]+2]):
                    self.checkDestination([self.playerPos[0], self.playerPos[1]+2])
                    self.grid[self.playerPos[1]+1][self.playerPos[0]] = 0
                    self.playerPos = [self.playerPos[0], self.playerPos[1]+1]
            else:
                self.playerPos = [self.playerPos[0], self.playerPos[1]+1]
        elif str(reaction) == self.gameEmojis[4]:
            self.grid = self.orgGrid
            self.playerPos = self.orgPlayerPos
        elif str(reaction) == self.gameEmojis[5]:
            self.isPlaying = False
            self.result = ("Stop", None)
        self.winCheck()

    # Function to initialise the grid and related variables
    async def initGrid(self) -> None:
        # Create width, height and box count variables
        user = await Utils.database.fetchUser("SELECT * FROM gameScores WHERE guildID = ? and userID = ? and gameID = ?", (self.ctx.guild.id, self.ctx.author.id, self.gameID), "gameScores")
        gridWidth = 7
        gridHeight = 6
        boxCount = 1
        self.level = user[3]+1
        for i in range(self.level//20):
            gridWidth += 2
            gridHeight += 1
            boxCount += 1
        if gridWidth > 15:
            gridWidth = 15
            gridHeight = 10
            boxCount = 5
        # Create empty grid
        tempGrid = [[0 for _ in range(gridWidth)] for _ in range(gridHeight)]
        # Add in walls
        tempGrid[0] = [1]*gridWidth
        tempGrid[gridHeight-1] = [1]*gridWidth
        for row in range(gridHeight):
            tempGrid[row][0] = 1
            tempGrid[row][gridWidth-1] = 1
        # Create box positions
        for _ in range(boxCount):
            boxPositionX = random.randint(0, gridWidth-1)
            boxPositionY = random.randint(0, gridHeight-1)
            while not self.positionChecker(tempGrid, boxPositionX, boxPositionY, True):
                boxPositionX = random.randint(0, gridWidth-1)
                boxPositionY = random.randint(0, gridHeight-1)
            tempGrid[boxPositionY][boxPositionX] = 2
        # Create box destinations
        for _ in range(boxCount):
            destinationPositionX = random.randint(0, gridWidth-1)
            destinationPositionY = random.randint(0, gridHeight-1)
            while not self.positionChecker(tempGrid, destinationPositionX, destinationPositionY):
                destinationPositionX = random.randint(0, gridWidth-1)
                destinationPositionY = random.randint(0, gridHeight-1)
            tempGrid[destinationPositionY][destinationPositionX] = 3
        # Create player position
        playerPositionX = random.randint(0, gridWidth-1)
        playerPositionY = random.randint(0, gridHeight-1)
        while not self.positionChecker(tempGrid, playerPositionX, playerPositionY):
            playerPositionX = random.randint(0, gridWidth-1)
            playerPositionY = random.randint(0, gridHeight-1)
        self.orgPlayerPos = [playerPositionX, playerPositionY]
        self.playerPos = self.orgPlayerPos
        self.orgGrid = tempGrid
        # Stop overwriting of self.grid
        self.grid = copy.deepcopy(self.orgGrid)
        self.remainingBoxes = boxCount

    # Function to update the board
    async def embedUpdate(self) -> None:
        sokobanEmbed = Embed(title=self.getTitle(), colour=self.colour)
        tempDescription = ""
        # Stop overwriting of self.grid
        temp = copy.deepcopy(self.grid)
        temp[self.playerPos[1]][self.playerPos[0]] = 4
        for row in temp:
            for column in row:
                if column == 0:
                    tempDescription += self.gridEmojis[0]
                elif column == 1:
                    tempDescription += self.gameColour
                elif column == 2:
                    tempDescription += self.gridEmojis[1]
                elif column == 3:
                    tempDescription += self.gridEmojis[2]
                elif column == 4:
                    tempDescription += self.gridEmojis[3]
            tempDescription += "\n"
        sokobanEmbed.description = tempDescription
        await self.gameMessage.edit(embed=sokobanEmbed)

    # Function to update the scores
    async def updateScores(self) -> None:
        user = await Utils.database.fetchUser("SELECT * FROM gameScores WHERE guildID = ? and userID = ? and gameID = ?", (self.ctx.guild.id, self.user.id, self.gameID), "gameScores")
        if self.result[0] == "Win":
            user[3] += 1
        await Utils.database.execute("UPDATE gameScores SET score = ? WHERE guildID = ? and userID = ? and gameID = ?", (user[3], user[0], user[1], user[2]))
