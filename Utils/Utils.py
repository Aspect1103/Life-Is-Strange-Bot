# Builtin
from datetime import datetime
import os
import json
# Custom
from .Restrictor import Restrictor


# Function to create allowedIDs
def initIDs():
    with open(idPath, "r") as file:
        return json.loads(file.read())


# Function to write changes to IDs.txt
def idWriter(newDict):
    with open(idPath, "w") as file:
        jsonString = json.dumps(newDict, indent=4)
        file.write(jsonString)


# Function to write messages to error.txt
def errorWrite(error):
    with open(errorPath, "a") as file:
        file.write(f"{datetime.now()}, {error}\n")


# Script variables
extensions = ["Cogs.Life Is Strange", "Cogs.Fanfic", "Cogs.General", "Cogs.Miscellaneous", "Cogs.Admin"]

# Path variables
rootDirectory = os.path.join(os.path.dirname(__file__), os.pardir)
idPath = os.path.join(rootDirectory, "TextFiles", "IDs.txt")
errorPath = os.path.join(rootDirectory, "BotFiles", "error.txt")

# Restrictor class initialisation
IDs = initIDs()
commandGroups = {
    "bot stuff": ["stop", "channel", "channel add", "channel remove", "channel list", "botRefresh", "channelRefresh", "about"],
    "fanfic": ["quote", "nextQuote", "searchQuote", "outline", "works"],
    "general": ["question", "connect4", "tictactoe"],
    "life is strange": ["choices", "memory"],
    "image": ["art"],
    "trivia": ["trivia"]
}
restrictor = Restrictor(IDs, commandGroups)

# Cooldown variables
