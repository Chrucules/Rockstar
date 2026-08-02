import os

import discord
import wavelink
from discord.ext import commands

from utils.embeds import create_embed, error


LAVALINK_URI = os.getenv("ROCKSTAR_LAVALINK_URI")
LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD")


def format_duration(milliseconds: int) -> str:
    total_seconds = milliseconds // 1000
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)

    if hours:
        return f"{hours}:{minutes:02}:{seconds:02}"

    return f"{minutes}:{seconds:02}"


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    async def cog_load(self):
        if not LAVALINK_URI or not LAVALINK_PASSWORD:
            print("Missing Lavalink variables.")
            return

        node = wavelink.Node(
            uri=LAVALINK_URI,
            password=LAVALINK_PASSWORD
        )

        try:
            await wavelink.Pool.connect(
                nodes=[node],
                client=self.bot
            )

            print("Connected Rockstar to Lavalink.")

        except Exception as exc:
            print(f"Lavalink connection failed: {exc}")


    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload):
        print("Lavalink node is ready.")


    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload):
        player = payload.player

        if player.queue.is_empty:
            return

        next_track = player.queue.get()
        await player.play(next_track)


    async def get_player(
        self,
        interaction: discord.Interaction
    ):

        player = interaction.guild.voice_client

        if not isinstance(player, wavelink.Player):
            await interaction.response.send_message(
                embed=error(
                    "Rockstar is not connected to a voice channel."
                ),
                ephemeral=True
            )
            return None

        return player


    async def same_voice_channel(
        self,
        interaction: discord.Interaction,
        player: wavelink.Player
    ) -> bool:

        if not interaction.user.voice:
            await interaction.response.send_message(
                embed=error("Join a voice channel first."),
                ephemeral=True
            )
            return False

        if interaction.user.voice.channel != player.channel:
            await interaction.response.send_message(
                embed=error(
                    "You must be in Rockstar's voice channel."
                ),
                ephemeral=True
            )
            return False

        return True


    @discord.app_commands.command(
        name="play",
        description="Play or queue a song"
    )
    @discord.app_commands.describe(
        query="Song name or URL"
    )
    async def play(
        self,
        interaction: discord.Interaction,
        query: str
    ):

        if not interaction.user.voice:
            await interaction.response.send_message(
                embed=error("Join a voice channel first."),
                ephemeral=True
            )
            return

        await interaction.response.defer()

        player = interaction.guild.voice_client

        if player is None:
            player = await interaction.user.voice.channel.connect(
                cls=wavelink.Player
            )

        elif not isinstance(player, wavelink.Player):
            await interaction.followup.send(
                embed=error(
                    "Rockstar is using an unsupported voice connection."
                ),
                ephemeral=True
            )
            return

        elif player.channel != interaction.user.voice.channel:
            await interaction.followup.send(
                embed=error(
                    "You must be in Rockstar's voice channel."
                ),
                ephemeral=True
            )
            return

        try:
            results = await wavelink.Playable.search(query)

        except Exception as exc:
            await interaction.followup.send(
                embed=error(f"Search failed:\n`{exc}`"),
                ephemeral=True
            )
            return

        if not results:
            await interaction.followup.send(
                embed=error("No songs were found."),
                ephemeral=True
            )
            return

        if isinstance(results, wavelink.Playlist):
            tracks = list(results.tracks)

            for track in tracks:
                await player.queue.put_wait(track)

            if not player.playing:
                first_track = player.queue.get()
                await player.play(first_track)

            await interaction.followup.send(
                embed=create_embed(
                    "Playlist Added",
                    (
                        f"🎵 **{results.name}**\n\n"
                        f"Added `{len(tracks)}` songs\n"
                        f"Requested by {interaction.user.mention}"
                    )
                )
            )
            return

        track = results[0]

        if player.playing:
            await player.queue.put_wait(track)

            embed = create_embed(
                "Added to Queue",
                (
                    f"🎵 **[{track.title}]({track.uri})**\n\n"
                    f"Artist: `{track.author}`\n"
                    f"Duration: `{format_duration(track.length)}`\n"
                    f"Queue position: `{player.queue.count}`\n"
                    f"Requested by: {interaction.user.mention}"
                )
            )

        else:
            await player.play(track)

            embed = create_embed(
                "Now Playing",
                (
                    f"🎵 **[{track.title}]({track.uri})**\n\n"
                    f"Artist: `{track.author}`\n"
                    f"Duration: `{format_duration(track.length)}`\n"
                    f"Requested by: {interaction.user.mention}"
                )
            )

        if track.artwork:
            embed.set_thumbnail(url=track.artwork)

        await interaction.followup.send(embed=embed)


    @discord.app_commands.command(
        name="pause",
        description="Pause the current song"
    )
    async def pause(
        self,
        interaction: discord.Interaction
    ):

        player = await self.get_player(interaction)

        if player is None:
            return

        if not await self.same_voice_channel(interaction, player):
            return

        if not player.playing:
            await interaction.response.send_message(
                embed=error("Nothing is currently playing."),
                ephemeral=True
            )
            return

        await player.pause(True)

        await interaction.response.send_message(
            embed=create_embed(
                "Paused",
                "⏸ Music has been paused."
            )
        )


    @discord.app_commands.command(
        name="resume",
        description="Resume the current song"
    )
    async def resume(
        self,
        interaction: discord.Interaction
    ):

        player = await self.get_player(interaction)

        if player is None:
            return

        if not await self.same_voice_channel(interaction, player):
            return

        if not player.paused:
            await interaction.response.send_message(
                embed=error("The music is not paused."),
                ephemeral=True
            )
            return

        await player.pause(False)

        await interaction.response.send_message(
            embed=create_embed(
                "Resumed",
                "▶️ Music has resumed."
            )
        )


    @discord.app_commands.command(
        name="skip",
        description="Skip the current song"
    )
    async def skip(
        self,
        interaction: discord.Interaction
    ):

        player = await self.get_player(interaction)

        if player is None:
            return

        if not await self.same_voice_channel(interaction, player):
            return

        if not player.current:
            await interaction.response.send_message(
                embed=error("Nothing is currently playing."),
                ephemeral=True
            )
            return

        skipped = player.current

        await player.skip(force=True)

        await interaction.response.send_message(
            embed=create_embed(
                "Skipped",
                f"⏭ Skipped **{skipped.title}**."
            )
        )


    @discord.app_commands.command(
        name="queue",
        description="Show the music queue"
    )
    async def queue_command(
        self,
        interaction: discord.Interaction
    ):

        player = await self.get_player(interaction)

        if player is None:
            return

        tracks = list(player.queue)

        if not player.current and not tracks:
            await interaction.response.send_message(
                embed=error("The queue is empty."),
                ephemeral=True
            )
            return

        description = ""

        if player.current:
            description += (
                "▶️ **Now Playing**\n"
                f"**{player.current.title}**\n"
                f"`{format_duration(player.current.length)}`\n\n"
            )

        if tracks:
            description += "📜 **Up Next**\n"

            for number, track in enumerate(tracks[:15], start=1):
                description += (
                    f"`{number}.` **{track.title}** "
                    f"— `{format_duration(track.length)}`\n"
                )

            if len(tracks) > 15:
                description += (
                    f"\nAnd `{len(tracks) - 15}` more songs."
                )

        await interaction.response.send_message(
            embed=create_embed(
                "Queue",
                description
            )
        )


    @discord.app_commands.command(
        name="skipto",
        description="Skip to a numbered song in the queue"
    )
    @discord.app_commands.describe(
        number="The number shown in /queue"
    )
    async def skipto(
        self,
        interaction: discord.Interaction,
        number: int
    ):

        player = await self.get_player(interaction)

        if player is None:
            return

        if not await self.same_voice_channel(interaction, player):
            return

        tracks = list(player.queue)

        if number < 1 or number > len(tracks):
            await interaction.response.send_message(
                embed=error(
                    f"Choose a number from `1` to `{len(tracks)}`."
                ),
                ephemeral=True
            )
            return

        target = tracks[number - 1]

        for _ in range(number - 1):
            player.queue.get()

        await player.skip(force=True)

        await interaction.response.send_message(
            embed=create_embed(
                "Skip To",
                (
                    f"⏭ Skipping to queue number `{number}`.\n\n"
                    f"Next: **{target.title}**"
                )
            )
        )


    @discord.app_commands.command(
        name="stop",
        description="Stop music and disconnect"
    )
    async def stop(
        self,
        interaction: discord.Interaction
    ):

        player = await self.get_player(interaction)

        if player is None:
            return

        if not await self.same_voice_channel(interaction, player):
            return

        player.queue.reset()
        await player.disconnect()

        await interaction.response.send_message(
            embed=create_embed(
                "Stopped",
                (
                    "⏹ Music stopped.\n"
                    "The queue was cleared and Rockstar disconnected."
                )
            )
        )


async def setup(bot):
    await bot.add_cog(Music(bot))