# Builtin
from pathlib import Path
import random
# Pip
from discord.channel import TextChannel, VoiceChannel
from wavelink.ext import spotify
from discord.ext import commands
from discord import VoiceRegion
from discord import Colour
from discord import Embed
import discord.utils
import wavelink
import pendulum
# Custom
from Helpers.Utils import Utils
import Config

# Path variables
rootDirectory = Path(__file__).parent.parent
radioPath = rootDirectory.joinpath("Resources").joinpath("Files").joinpath("radioLines.txt")


# Cog to manage radio commands
class Radio(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.colour = Colour.from_rgb(255, 192, 203)
        self.tracks = wavelink.Queue()
        self.trackCounter = None
        self.nextTrack = None
        self.textChannel = None
        self.infoMessage = None
        self.radioLines = None
        self.client.loop.create_task(self.wavelinkInit())

    # Function to get a voiceClient
    def getVoiceClient(self, guild):
        return discord.utils.get(self.client.voice_clients, guild=guild)

    # Function to determine if the bot is connected to a voice channel
    def isConnected(self, guild):
        return self.getVoiceClient(guild) is not None

    # Initialise the wavelink client
    async def wavelinkInit(self):
        # Create a wavelink node to play music
        await self.client.wait_until_ready()
        await wavelink.NodePool.create_node(bot=self.client,
                                            host="lava.link",
                                            port=80,
                                            password="anything as a password",
                                            region=VoiceRegion.london,
                                            spotify_client=spotify.SpotifyClient(client_id=Config.spotifyID, client_secret=Config.spotifySecret),
                                            identifier="LiSBot")

        # Grab all songs and randomise them
        self.tracks = [partialTrack async for partialTrack in spotify.SpotifyTrack.iterator(query="6jCdO6RGfNw4siuCKpIBgM", partial_tracks=True)]
        random.shuffle(self.tracks)

        # Create dictionary for each guild to store variables
        self.trackCounter = {guild.id: 0 for guild in self.client.guilds}
        self.nextTrack = {guild.id: 0 for guild in self.client.guilds}
        self.textChannel = {guild.id: None for guild in self.client.guilds}
        self.infoMessage = {guild.id: None for guild in self.client.guilds}

        # Setup radio lines array
        self.radioLines = [line.replace("\n", "") for line in open(radioPath, "r", encoding="utf8").readlines()]

    # Function to send a radio line to the text channel
    async def sendRadioLine(self, guildID):
        await self.textChannel[guildID].send(embed=Embed(title="Today's Announcement From 104.3 KRCT's Steph Gingrich:", description=random.choice(self.radioLines), colour=self.colour))

    # Function to disconnect the bot from a voice channel
    async def stopBot(self, guild):
        # Get the voice client
        voiceClient = self.getVoiceClient(guild)
        # Stop the song then disconnect the bot
        await voiceClient.stop()
        await voiceClient.disconnect(force=False)
        # Reset the variables
        self.trackCounter[guild.id] = 0
        self.nextTrack[guild.id] = 0
        self.textChannel[guild.id] = None
        self.infoMessage[guild.id] = None

    # Runs when a track starts playing
    @commands.Cog.listener()
    async def on_wavelink_track_start(self, player: wavelink.Player, track: wavelink.Track):
        # Increment the guild counters
        self.trackCounter[player.guild.id] += 1
        self.nextTrack[player.guild.id] += 1
        # Display details on the currently running song
        titleAuthor = self.tracks[self.nextTrack[player.guild.id]-1].query.split(" - ")
        infoEmbed = Embed(title=f"Now Playing: {titleAuthor[0]} by {titleAuthor[1]}", colour=self.colour)
        infoEmbed.add_field(name="Link", value=track.uri, inline=True)
        infoEmbed.add_field(name="Duration", value=str(pendulum.duration(seconds=track.duration)), inline=True)
        infoEmbed.set_image(url=f"https://i.ytimg.com/vi/{track.identifier}/0.jpg")
        await self.infoMessage[player.guild.id].edit(embed=infoEmbed)

    # Runs when a track stops playing
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason):
        # Test if 5 songs have played. If so, send a radio line
        if self.trackCounter[player.guild.id] == 5:
            self.trackCounter[player.guild.id] = 0
            await self.sendRadioLine(player.guild.id)
            self.infoMessage[player.guild.id] = await self.textChannel[player.guild.id].send(embed=Embed(title="Initialising, please wait", colour=self.colour))
        # Play the next song
        await player.play(self.tracks[self.nextTrack[player.guild.id]])

    # # Runs when a member changes their voicestate
    # @commands.Cog.listener()
    # async def on_voice_state_update(self, member, before, after):
    #     # Test if the bot is connected and if the member is the bot
    #     if self.isConnected(member.guild) and member.id != self.client.user.id:
    #         # Test if there is only 1 member left (will have to be bot)
    #         voiceClientChannel = self.getVoiceClient(member.guild).channel
    #         if len(voiceClientChannel.members) == 1:
    #             # Wait 5 minutes and then disconnect if there is still inactivity
    #             await Utils.commandDebugEmbed(self.textChannel[member.guild.id], f"Warning! Bot will disconnect in 1 minute due to inactivity. Please join {voiceClientChannel.mention} to stop this")
    #             await asyncio.sleep(60)
    #             # Test again if there is only 1 member
    #             if len(voiceClientChannel.members) == 1:
    #                 await self.stopBot(member.guild)

    # connect command with a cooldown of 1 use every 60 seconds per guild
    @commands.command(help=f"Connects the bot to a voice channel. It has a cooldown of {Utils.long} seconds", usage="connect", brief="Radio")
    @commands.cooldown(1, 0, commands.BucketType.guild)
    async def connect(self, ctx):
        # Test if the bot is already connected
        if not self.isConnected(ctx.guild):
            # Verify that there is a text channel and a voice channel registered
            radioChannels = []
            for channelID in Utils.restrictor.IDs["radio"][str(ctx.guild.id)]:
                channel = self.client.get_channel(channelID)
                if type(channel) not in [type(temp) for temp in radioChannels]:
                    radioChannels.append(channel)
            radioChannelTypes = [type(temp) for temp in radioChannels]
            if TextChannel in radioChannelTypes and VoiceChannel in radioChannelTypes:
                # Grab text and voice channels
                voiceChannel = radioChannels[0] if type(radioChannels[0]) == VoiceChannel else radioChannels[1]
                textChannel = radioChannels[0] if type(radioChannels[0]) == TextChannel else radioChannels[1]
                self.textChannel[ctx.guild.id] = textChannel
                # Connect the bot to the voice channel then send a starting radio line and info embed
                player = await voiceChannel.connect(cls=wavelink.Player)
                await self.sendRadioLine(ctx.guild.id)
                self.infoMessage[ctx.guild.id] = await textChannel.send(embed=Embed(title="Initialising, please wait", colour=self.colour))
                # Play music
                await player.play(self.tracks[self.nextTrack[player.guild.id]])
            else:
                await Utils.commandDebugEmbed(ctx.channel, f"Ensure there is both a text channel and a voice channel registered with {ctx.prefix}channel")
        else:
            await Utils.commandDebugEmbed(ctx.channel, f"Bot is already connected to a voice channel. Please use {ctx.prefix}disconnnect to disconnect it")

    # disconnect command with a cooldown of 1 use every 60 seconds per guild
    @commands.command(help=f"Disconnects the bot from a voice channel. It has a cooldown of {Utils.long} seconds", usage="disconnect", brief="Radio")
    @commands.cooldown(1, 0, commands.BucketType.guild)
    async def disconnect(self, ctx):
        # Test if the bot is already connected
        if self.isConnected(ctx.guild):
            await self.stopBot(ctx.guild)
        else:
            await Utils.commandDebugEmbed(ctx.channel, f"Bot is not connected to a voice channel. Please use {ctx.prefix}connect to connect it to one")

    # Function to run channelCheck for Radio
    async def cog_check(self, ctx):
        return await Utils.restrictor.commandCheck(ctx)

    # Catch any cog errors
    #async def cog_command_error(self, ctx, error):
    #    await Utils.errorHandler(ctx, error)


# Function which initialises the Radio cog
def setup(client):
    client.add_cog(Radio(client))
