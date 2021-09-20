# Builtin
from pathlib import Path
from sqlite3 import Row
from typing import List, Tuple, Union
# Pip
import asqlite


# DatabaseManager class to streamline database operations
class DatabaseManager:
    # Initialise variables
    def __init__(self, databasePath: Path) -> None:
        self.path = databasePath
        self.connection = None

    # Function to connect to the database
    async def connect(self) -> None:
        self.connection: asqlite.Connection = await asqlite.connect(str(self.path))

    # Function for executing sql statements that don't return anything
    async def execute(self, statement: str, params: Union[Tuple[int, ...], int]) -> None:
        async with self.connection.cursor() as executeCursor:
            await executeCursor.execute(statement, params)

    # Function for executing many sql statements that don't return anything
    async def executeMany(self, statement: str, arr: List[Tuple[int, ...]]) -> None:
        async with self.connection.cursor() as executeManyCursor:
            await executeManyCursor.executemany(statement, arr)

    # Function for fetching data from the database
    async def fetch(self, statement: str, params: Union[Tuple[int, ...], int]) -> List[Tuple[int, int, int, int, int, int]]:
        async with self.connection.cursor() as fetchCursor:
            await fetchCursor.execute(statement, params)
            result: List[Row] = await fetchCursor.fetchall()
            return [tuple(row) for row in result]

    # Function for fetching a user's data from the database (or adding a new row)
    async def fetchUser(self, statement: str, params: Tuple[int, ...], table: str) -> List[int]:
        result = await self.fetch(statement, params)
        if len(result) == 0:
            if table == "triviaScores":
                result = (params[0], params[1], 0, 0, 0, 0)
                await self.execute("INSERT INTO triviaScores values(?, ?, ?, ?, ?, ?)", result)
            elif table == "sokoban":
                result = (params[0], params[1], 0)
                await self.execute("INSERT INTO sokoban values(?, ?, ?)", result)
            return list(result)
        else:
            return list(result[0])
