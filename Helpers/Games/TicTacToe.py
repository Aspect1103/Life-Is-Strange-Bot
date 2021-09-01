# Builtin
from typing import List
from datetime import datetime
# Pip
from discord.ext.commands import Context, Bot
from discord import Embed, Colour, Reaction


# TicTacToe class to play tic tac toe in a discord channel
class TicTacToe:
    # Initialise variables
    def __init__(self, ctx: Context, client: Bot, color: Colour) -> None:
        self.ctx = ctx
        self.client = client
        self.colour = color
        self.gameID = 1
        self.player1 = self.ctx.author
        self.nextPlayer = self.player1
        self.lastActivity = datetime.now()
        self.grid = [[0 for i in range(3)] for j in range(3)]
        self.iconEmojis = ["🟦", "❌", "⭕"]
        self.gameEmojis = ["↖️", "⬆️", "↗️", "⬅️", "⏺️", "➡️", "↙️", "⬇️", "↘️", "🛑"]
        self.isPlaying = True
        self.changeMade = False
        self.player2 = None
        self.gameMessage = None
        self.result = None

    # Function to return the game name
    def __repr__(self) -> str:
        return "TicTacToe"

    # Function to manage moves made by the player
    def moveManager(self, reaction: str) -> None:
        if reaction == self.gameEmojis[0]:
            self.addMove([0, 0])
        elif reaction == self.gameEmojis[1]:
            self.addMove([0, 1])
        elif reaction == self.gameEmojis[2]:
            self.addMove([0, 2])
        elif reaction == self.gameEmojis[3]:
            self.addMove([1, 0])
        elif reaction == self.gameEmojis[4]:
            self.addMove([1, 1])
        elif reaction == self.gameEmojis[5]:
            self.addMove([1, 2])
        elif reaction == self.gameEmojis[6]:
            self.addMove([2, 0])
        elif reaction == self.gameEmojis[7]:
            self.addMove([2, 1])
        elif reaction == self.gameEmojis[8]:
            self.addMove([2, 2])
        elif reaction == self.gameEmojis[9]:
            self.isPlaying = False
            self.switchPlayer()
            self.result = ["Win", self.nextPlayer]

    # Function to update the 2D array with new moves
    def addMove(self, index: List[int]) -> None:
        if self.grid[index[0]][index[1]] == 0:
            self.changeMade = True
            if self.nextPlayer == self.player1:
                self.grid[index[0]][index[1]] = 1
            else:
                self.grid[index[0]][index[1]] = 2

    # Function to test for a draw
    def drawCheck(self) -> None:
        temp = [item for row in self.grid for item in row]
        if all(item != 0 for item in temp):
            self.isPlaying = False
            self.result = ["Draw", self.nextPlayer]

    # Function to check for wins
    def winChecker(self) -> None:
        checks = [
            # Horizontal checks
            self.grid[0][0] == self.grid[0][1] == self.grid[0][2] and self.grid[0][0] != 0 and self.grid[0][1] != 0 and self.grid[0][2] != 0,
            self.grid[1][0] == self.grid[1][1] == self.grid[1][2] and self.grid[1][0] != 0 and self.grid[1][1] != 0 and self.grid[1][2] != 0,
            self.grid[2][0] == self.grid[2][1] == self.grid[2][2] and self.grid[2][0] != 0 and self.grid[2][1] != 0 and self.grid[2][2] != 0,
            # Vertical checks
            self.grid[0][0] == self.grid[1][0] == self.grid[2][0] and self.grid[0][0] != 0 and self.grid[1][0] != 0 and self.grid[2][0] != 0,
            self.grid[0][1] == self.grid[1][1] == self.grid[2][1] and self.grid[0][1] != 0 and self.grid[1][1] != 0 and self.grid[2][1] != 0,
            self.grid[0][2] == self.grid[1][2] == self.grid[2][2] and self.grid[0][2] != 0 and self.grid[1][2] != 0 and self.grid[2][2] != 0,
            # Diagonal checks
            self.grid[0][0] == self.grid[1][1] == self.grid[2][2] and self.grid[0][0] != 0 and self.grid[1][1] != 0 and self.grid[2][2] != 0,
            self.grid[0][2] == self.grid[1][1] == self.grid[2][0] and self.grid[0][2] != 0 and self.grid[1][1] != 0 and self.grid[2][0] != 0
        ]
        if any([check for check in checks]):
            self.isPlaying = False
            self.result = ["Win", self.nextPlayer]

    # Function to determine who goes next
    def switchPlayer(self) -> None:
        if self.nextPlayer == self.player1:
            self.nextPlayer = self.player2
        else:
            self.nextPlayer = self.player1

    # Function to process a reaction from the gameManager
    def processReaction(self, reaction: Reaction) -> None:
        self.lastActivity = datetime.now()
        self.moveManager(str(reaction))
        if self.isPlaying:
            if self.changeMade:
                self.changeMade = False
                self.drawCheck()
                self.winChecker()
                self.switchPlayer()

    # Function to update the board
    async def embedUpdate(self) -> None:
        board = ""
        for row in self.grid:
            for item in row:
                if item == 0:
                    board += self.iconEmojis[0]
                elif item == 1:
                    board += self.iconEmojis[1]
                elif item == 2:
                    board += self.iconEmojis[2]
            board += "\n"
        gameEmbed = Embed(description=board, colour=self.colour)
        if self.isPlaying:
            gameEmbed.title = f"TicTacToe - {self.nextPlayer}'s Turn"
        else:
            if self.result[0] == "Win":
                gameEmbed.title = f"Game Over! {self.result[1]} Won"
            elif self.result[0] == "Draw":
                gameEmbed.title = f"Game Over! It's A Draw"
            else:
                gameEmbed.title = f"Game Over!"
        await self.gameMessage.edit(embed=gameEmbed)
