import wavelink
import discord
from discord.ext import commands
from discord import app_commands
from discord import Embed
from wavelink import Queue

class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = {}
        self.vc = {}

    group = app_commands.Group(name="music", description="music stuff")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload):
        await self.play_next_track(guild=payload.player.guild)

    @group.command(name="play", description="song name or the link")
    async def music(self, interaction: discord.Interaction, search: str):
        if not interaction.guild.voice_client:
            self.vc[interaction.guild.id] = ""
            self.vc[interaction.guild.id] = await interaction.user.voice.channel.connect(cls=wavelink.Player)
        if interaction.guild.id not in self.queue:
            self.queue[interaction.guild.id] = Queue()

        vc = self.vc[interaction.guild.id]
        queue = self.queue[interaction.guild.id]

        tracks: wavelink.Search = await wavelink.Playable.search(search)
        if not tracks:
            return await interaction.response.send_message(f'It was not possible to find the song: `{search}`')
        track: wavelink.Playable = tracks[0]
        queue.put(track)

        self.music_channel = interaction.channel
        if not vc.playing:
            embed = Embed(title="🎵 Song added to the queue.", description=f'`{track.title}` was added to the queue.')
            await interaction.response.send_message(embed=embed)
            await self.play_next_track(guild=interaction.guild)
        else:
            embed = Embed(title="🎵 Song added to the queue.", description=f'`{track.title}` was added to the queue.')
            await interaction.response.send_message(embed=embed)
        
    async def play_next_track(self, guild):
        vc = self.vc[guild.id]
        queue = self.queue[guild.id]

        if not queue.is_empty:
            next_track = queue.get()
            await vc.play(next_track)
            embed = Embed(title="🎵 playing now", description=f'`{next_track.title}` is playing now.')
            await self.music_channel.send(embed=embed)

    @group.command(name="stop", description="stop the everything")
    async def stop(self, interaction: discord.Interaction):
        vc = self.vc[interaction.guild.id]
        await vc.stop()
        embed = Embed(title="⏹️ Music stopped", description="The music has been stopped.")
        await interaction.response.send_message(embed=embed)
        await vc.disconnect()

    @group.command(name="pause", description="pause everything")
    async def pause(self, interaction: discord.Interaction):
        vc = self.vc[interaction.guild.id]
        await vc.pause(True)
        embed = Embed(title="⏸️ Music paused", description="The music has been paused")
        await interaction.response.send_message(embed=embed)

    @group.command(name="resume", description="pause everything")
    async def resume(self, interaction: discord.Interaction):
        vc = self.vc[interaction.guild.id]
        await vc.pause(False)
        embed = Embed(title="▶️ Music Resumed", description="The music has been resumed.")
        await interaction.response.send_message(embed=embed)

    @group.command(name="skip", description="skip song")
    async def skip(self, interaction: discord.Interaction):
        vc = self.vc[interaction.guild.id]
        queue = self.queue[interaction.guild.id]

        if not self.queue.is_empty:
            await vc.stop()
            next_track = queue.pop()
            await vc.play(next_track)
            embed = Embed(title="⏭️ Song skipped", description=f'Playing the next song in the queue: `{next_track.title}`.')
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("There are no songs in the queue to skip")

    @group.command(name="queue", description="list queue")
    async def queue(self, interaction: discord.Interaction):
        queue = self.queue[interaction.guild.id]
        if not queue:
            embed = Embed(title="📜 Playlist", description="The queue is empty.")
            await interaction.response.send_message(embed=embed)
        else:
            queue_list = "\n".join([f"- {track.title}" for track in queue])
            embed = Embed(title="📜 Playlist", description=queue_list)
            await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(music(bot))