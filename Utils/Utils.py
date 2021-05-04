# Builtin
from datetime import datetime
import os
import json


# Function to create allowedIDs
def initIDs():
    with open(idPath, "r") as file:
        return json.loads(file.read())


# Function to write changes to IDs.txt
def idWriter(newDict):
    with open(idPath, "w") as file:
        jsonString = json.dumps(newDict)
        file.write(jsonString)


# Function to check if a command is in the correct channel
def channelCheck(ctx, allowedIDs):
    return ctx.channel.id in allowedIDs


# Function to write messages to error.txt
def errorWrite(error):
    with open(errorPath, "a") as file:
        file.write(f"{datetime.now()}, {error}\n")


# Script variables
rootDirectory = os.path.join(os.path.dirname(__file__), os.pardir)
idPath = os.path.join(rootDirectory, "TextFiles", "IDs.txt")
errorPath = os.path.join(rootDirectory, "BotFiles", "error.txt")
allowedIDs = initIDs()
extensions = ["Cogs.Life Is Strange", "Cogs.Fanfic", "Cogs.General", "Cogs.Miscellaneous", "Cogs.Admin"]