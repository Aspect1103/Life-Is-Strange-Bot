# Builtin
from typing import List, Tuple
from pathlib import Path
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
        self.connection = await asqlite.connect(str(self.path))

    # Function for executing sql statements that don't return anything
    async def execute(self, statement: str) -> None:
        async with self.connection.cursor() as executeCursor:
            await executeCursor.execute(statement)

    # Function for executing many sql statements that don't return anything
    async def executeMany(self, statement: str, arr: List[Tuple[int]]) -> None:
        async with self.connection.cursor() as executeManyCursor:
            await executeManyCursor.executemany(statement, arr)

    # Function for fetching data from the database
    async def fetch(self, statement: str) -> List[Tuple[int]]:
        async with self.connection.cursor() as fetchCursor:
            executed = await fetchCursor.execute(statement)
            result = await executed.fetchall()
            return [tuple(row) for row in result]
