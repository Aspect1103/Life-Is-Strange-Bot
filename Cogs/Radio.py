# Builtin
import asyncio
import random
# Pip
from discord.channel import TextChannel, VoiceChannel
from discord.ext import commands
from discord import VoiceRegion
from discord import Embed
from discord import Colour
from wavelink.ext import spotify
import wavelink
# Custom
from Helpers.Utils import Utils
import Config


# Cog to manage radio commands
class Radio(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.colour = Colour.from_rgb(255, 192, 203)
        self.tracks = wavelink.Queue()
        self.nextTrack = 0
        self.trackCounter = 0
        self.textChannels = {}
        self.client.loop.create_task(self.initWavelink())

    # Initialise the wavelink client
    async def initWavelink(self):
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

    # Runs when a track starts playing
    @commands.Cog.listener()
    async def on_wavelink_track_start(self, player: wavelink.Player, track: wavelink.Track):
        self.trackCounter += 1
        self.nextTrack += 1
        await self.textChannels[player.guild.id].send(track.title)
        print(self.trackCounter)
        print(self.nextTrack)
        # update embed detailing whats playing

    # Runs when a track stops playing
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason):
        if self.trackCounter == 2:
            self.trackCounter = 0
            await self.textChannels[player.guild.id].send("radio")
            # send radio text message
        await player.play(self.tracks[self.nextTrack])

    # connect command with a cooldown of 1 use every 60 seconds per guild
    @commands.command(help=f"Connects the bot to a voice channel. It has a cooldown of {Utils.long} seconds", usage="connect", brief="Radio")
    @commands.cooldown(1, Utils.long, commands.BucketType.guild)
    async def connect(self, ctx):
        # Verify that there is a text channel and a voice channel registered
        radioChannels = []
        for channelID in Utils.restrictor.IDs["radio"][str(ctx.guild.id)]:
            channel = self.client.get_channel(channelID)
            if type(channel) not in [type(temp) for temp in radioChannels]:
                radioChannels.append(channel)
        radioChannelTypes = [type(temp) for temp in radioChannels]
        if TextChannel in radioChannelTypes and VoiceChannel in radioChannelTypes:
            # Start radio
            voiceChannel = radioChannels[0] if type(radioChannels[0]) == VoiceChannel else radioChannels[1]
            textChannel = radioChannels[0] if type(radioChannels[0]) == TextChannel else radioChannels[1]
            self.textChannels[ctx.guild.id] = textChannel
            player = await voiceChannel.connect(cls=wavelink.Player)
            await player.play(self.tracks[self.nextTrack])
        else:
            await Utils.commandDebugEmbed(ctx.channel, f"Ensure there is both a text channel and a voice channel registered with {ctx.prefix}channel")

    # Function to run channelCheck for Radio
    async def cog_check(self, ctx):
        return await Utils.restrictor.commandCheck(ctx)

    # Catch any cog errors
    #async def cog_command_error(self, ctx, error):
    #    await Utils.errorHandler(ctx, error)


# Function which initialises the Radio cog
def setup(client):
    client.add_cog(Radio(client))
