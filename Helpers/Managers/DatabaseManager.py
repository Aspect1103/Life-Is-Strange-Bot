# Builtin
from pathlib import Path
# Pip
import asqlite


# DatabaseManager class to streamline database operations
class DatabaseManager:
    # Initialise variables
    def __init__(self, databasePath: Path) -> None:
        self.path = databasePath
        self.connection = None
        self.cursor = None

    # Function to connect to the database
    async def connect(self):
        async with asqlite.connect(str(self.path)) as self.connection:
            async with self.connection.cursor() as self.cursor:
                pass
