# Pip
from discord.ext.commands import Context
from discord import Client
from discord import Embed
from discord import Colour


# Connect4 class to play connect 4 in a discord channel
class Connect4:
    # Initialise variables
    def __init__(self, ctx: Context, client: Client, color: Colour):
        if isinstance(ctx, Context) and isinstance(client, Client) and isinstance(color, Colour):
            self.ctx = ctx
            self.client = client
            self.colour = color
        else:
            raise TypeError("Invalid parameters")
        self.timeout = 300
        self.player1 = self.ctx.author
        self.player2 = None
        self.nextPlayer = self.player1
        self.grid = [[0 for i in range(7)] for j in range(6)]
        self.gameMessage = None
        self.iconEmojis = ["🔵", "🟡", "🔴"]
        self.gameEmojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "🛑"]
        self.isPlaying = True
        self.changeMade = False
        self.result = None

    # Function to return the game name
    def __repr__(self):
        return "Connect 4"

    # Function to setup ini send game reaction emojis
    async def sendEmojis(self):
        for emoji in self.gameEmojis:
            await self.gameMessage.add_reaction(emoji)

    # Function to update the board
    async def updateBoard(self):
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
            gameEmbed.title = f"Connect 4 - {self.nextPlayer}'s Turn"
        else:
            if self.result[0] == "Surrender":
                gameEmbed.title = f"Game Over! {self.result[1]} Surrendered"
            elif self.result[0] == "Win":
                gameEmbed.title = f"Game Over! {self.result[1]} Won"
            elif self.result[0] == "Draw":
                gameEmbed.title = f"Game Over! It's A Draw"
        await self.gameMessage.edit(embed=gameEmbed)

    # Start the game
    async def start(self):
        pass