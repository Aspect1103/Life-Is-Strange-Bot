from __future__ import annotations

# Builtin
from pathlib import Path
from sqlite3 import Row
from typing import Union

# Pip
import asqlite


# DatabaseManager class to streamline database operations
class DatabaseManager:
    # Initialise variables
    def __init__(self, databasePath: Path) -> None:
        self.path = str(databasePath)

    # Function for executing sql statements that don't return anything
    async def execute(
        self, statement: str, params: Union[tuple[int, ...], int],
    ) -> None:
        async with asqlite.connect(self.path) as connection:
            async with connection.cursor() as executeCursor:
                await executeCursor.execute(statement, params)

    # Function for executing many sql statements that don't return anything
    async def executeMany(self, statement: str, arr: list[tuple[int, ...]]) -> None:
        async with asqlite.connect(self.path) as connection:
            async with connection.cursor() as executeManyCursor:
                await executeManyCursor.executemany(statement, arr)

    # Function for fetching data from the database
    async def fetch(
        self, statement: str, params: Union[tuple[int, ...], int],
    ) -> list[tuple[int, int, int, int, int, int]]:
        async with asqlite.connect(self.path) as connection:
            async with connection.cursor() as fetchCursor:
                await fetchCursor.execute(statement, params)
                result: list[Row] = await fetchCursor.fetchall()
                return [tuple(row) for row in result]

    # Function for fetching a user's data from the database (or adding a new row)
    async def fetchUser(
        self, statement: str, params: tuple[int, ...], table: str,
    ) -> list[int]:
        result = await self.fetch(statement, params)
        if len(result) == 0:
            if table == "triviaScores":
                result = (params[0], params[1], 0, 0, 0, 0)
                await self.execute(
                    "INSERT INTO triviaScores values(?, ?, ?, ?, ?, ?)", result,
                )
            elif table == "sokoban":
                result = (params[0], params[1], 0)
                await self.execute("INSERT INTO sokoban values(?, ?, ?)", result)
            return list(result)
        else:
            return list(result[0])
