# Builtin
from itertools import chain, groupby
# Pip
from discord.ext.commands import Context
from discord import Member
from discord import Client
from discord import Embed
from discord import Colour


# Connect4 class to play connect 4 in a discord channel
class Connect4:
    # Initialise variables
    def __init__(self, ctx: Context, client: Client, colour: Colour):
        if isinstance(ctx, Context) and isinstance(client, Client):
            self._ctx = ctx
            self._client = client
        else:
            raise TypeError("Invalid parameters")
        self.colour = colour
        self._player1 = self._ctx.author
        self._nextPlayer = self._player1
        self._grid = [[0 for _ in range(7)] for _ in range(6)]
        self._reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "⏹️"]
        self._playing = True
        self._player2 = None
        self._message = None
        self._gameEmbed = None
        self._lastIndex = None
        self._winner = None

    # Function to update the game board
    def _updateBoard(self):
        result = "1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣\n"
        for row in self._grid:
            for item in row:
                if item == 0:
                    result += "🔵"
                elif item == 1:
                    result += "🟡"
                elif item == 2:
                    result += "🔴"
            result += "\n"
        self._gameEmbed.description = result
        if self._winner is not None:
            if self._winner == "Draw":
                self._gameEmbed.title = "Game Over. It's A Draw"
            elif self._winner == "Surrender":
                self._gameEmbed.title = f"Game Over. {self._nextPlayer.name} Surrendered"
            else:
                self._gameEmbed.title = f"Game Over. {self._winner} Won"
        else:
            self._gameEmbed.title = f"{self._nextPlayer.name}'s Turn"

    # Function to check the next move
    def _checkMove(self, reaction, user):
        return reaction.message.id == self._message.id and user.id == self._nextPlayer.id and str(reaction) in self._reactions

    # Function to find the new available row in a column and update it
    def _rowUpdater(self, columnNumber):
        availableRows = [i for i in range(len(self._grid)) if self._grid[i][columnNumber] == 0]
        if len(availableRows) != 0:
            self._lastIndex = (availableRows[-1], columnNumber)
            if self._nextPlayer == self._player1:
                self._grid[self._lastIndex[0]][self._lastIndex[1]] = 1
            else:
                self._grid[self._lastIndex[0]][self._lastIndex[1]] = 2
            return True
        else:
            return False

    # Function to check for wins
    def _winChecker(self):
        # Function to check for consecutive numbers
        def consecutiveCheck(row):
            totalConsecutive = 0
            if self._nextPlayer == self._player1:
                valueToCheck = 1
            else:
                valueToCheck = 2
            for value in row:
                if value == valueToCheck:
                    totalConsecutive += 1
                else:
                    totalConsecutive = 0
                if totalConsecutive >= 4:
                    return True
            return False
        # Function to check for vertical wins
        def verticalCheck():
            verticalRow = [row[self._lastIndex[1]] for row in self._grid]
            return consecutiveCheck(verticalRow)
        # Function to check for horizontal wins
        def horizontalCheck():
            horizontalRow = self._grid[self._lastIndex[0]]
            return consecutiveCheck(horizontalRow)
        # Function to check for diagonal wins
        def diagonalCheck():
            return False
        return verticalCheck() or horizontalCheck() or diagonalCheck()

    # Function to get positive and negative diagonals
    def _getDiagonals(self):
        positiveDiagonal = [self._grid[self._lastIndex[0]][self._lastIndex[1]]]

        for j in range(len(self._grid[0])-(self._lastIndex[1]+1)):
            positiveDiagonal.append(self._grid[self._lastIndex[0]-(j+1)][self._lastIndex[0]-2+j])

    # Function to manage the connect 4 moves
    async def _manager(self, reaction):
        if reaction == "1️⃣":
            return self._rowUpdater(0)
        elif reaction == "2️⃣":
            return self._rowUpdater(1)
        elif reaction == "3️⃣":
            return self._rowUpdater(2)
        elif reaction == "4️⃣":
            return self._rowUpdater(3)
        elif reaction == "5️⃣":
            return self._rowUpdater(4)
        elif reaction == "6️⃣":
            return self._rowUpdater(5)
        elif reaction == "7️⃣":
            return self._rowUpdater(6)
        elif reaction == "⏹️":
            self._playing = False

    # Function to send the initial embed message for other players to react to
    async def _sendInitialEmbed(self):
        initialEmbed = Embed(title="Connect 4 Request", description=f"{self._player1.mention} wants to play connect 4. React to this message if you want to challenge them", colour=self.colour)
        self._message = await self._ctx.send(embed=initialEmbed)
        await self._message.add_reaction("✅")

    # Function to play the game
    async def start(self, user: Member):
        self._player2 = user
        self._gameEmbed = Embed(title="Connect 4", description=f"{self._player1.mention} vs {self._player2.mention}", colour=self.colour)
        self._updateBoard()
        await self._message.clear_reactions()
        await self._message.edit(embed=self._gameEmbed)
        for reaction in self._reactions:
            await self._message.add_reaction(reaction)
        while self._playing:
            await self._message.edit(embed=self._gameEmbed)
            reaction, user = await self._client.wait_for("reaction_add", check=self._checkMove)
            await self._message.remove_reaction(reaction, user)
            foundRow = await self._manager(str(reaction))
            if foundRow:
                win = self._winChecker()
                if win:
                    self._playing = False
                    self._winner = self._nextPlayer.name
                else:
                    if self._nextPlayer == self._player1:
                        self._nextPlayer = self._player2
                    else:
                        self._nextPlayer = self._player1
                self._updateBoard()
            else:
                flattened = list(chain.from_iterable(self._grid))
                if all(value != 0 for value in flattened):
                    self._winner = "Draw"
                elif not self._playing:
                    self._winner = "Surrender"
                self._updateBoard()
        await self._message.clear_reactions()
        await self._message.edit(embed=self._gameEmbed)
