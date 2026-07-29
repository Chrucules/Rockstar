import discord
from discord.ext import commands

from utils.embeds import create_embed


class Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @discord.app_commands.command(
        name="ping",
        description="Check Rockstar latency"
    )
    async def ping(self, interaction: discord.Interaction):

        latency = round(self.bot.latency * 1000)

        embed = create_embed(
            "Ping",
            f"🏓 Pong!\nLatency: `{latency}ms`"
        )

        await interaction.response.send_message(
            embed=embed
        )


    @discord.app_commands.command(
        name="avatar",
        description="View a user's avatar"
    )
    async def avatar(
        self,
        interaction: discord.Interaction,
        user: discord.User = None
    ):

        user = user or interaction.user

        embed = create_embed(
            "Avatar",
            f"User: {user.mention}\nID: `{user.id}`"
        )

        embed.set_image(
            url=user.display_avatar.url
        )

        await interaction.response.send_message(
            embed=embed
        )


    @discord.app_commands.command(
        name="userinfo",
        description="View user information"
    )
    async def userinfo(
        self,
        interaction: discord.Interaction,
        user: discord.Member = None
    ):

        user = user or interaction.user

        embed = create_embed(
            "User Information",
            (
                f"👤 User: {user.mention}\n"
                f"🆔 ID: `{user.id}`\n"
                f"📅 Created: <t:{int(user.created_at.timestamp())}:F>\n"
                f"📥 Joined: <t:{int(user.joined_at.timestamp())}:F>"
            )
        )

        embed.set_thumbnail(
            url=user.display_avatar.url
        )

        await interaction.response.send_message(
            embed=embed
        )


    @discord.app_commands.command(
        name="id",
        description="Get your Discord ID"
    )
    async def get_id(
        self,
        interaction: discord.Interaction
    ):

        embed = create_embed(
            "Discord ID",
            f"Your ID is:\n`{interaction.user.id}`"
        )

        await interaction.response.send_message(
            embed=embed
        )


    @discord.app_commands.command(
        name="banner",
        description="View a user's banner"
    )
    async def banner(
        self,
        interaction: discord.Interaction,
        user: discord.User = None
    ):

        user = user or interaction.user

        fetched = await self.bot.fetch_user(user.id)

        if fetched.banner:

            embed = create_embed(
                "Banner",
                f"User: {user.mention}"
            )

            embed.set_image(
                url=fetched.banner.url
            )

        else:

            embed = create_embed(
                "Banner",
                "This user does not have a banner."
            )

        await interaction.response.send_message(
            embed=embed
        )


async def setup(bot):
    await bot.add_cog(
        Utility(bot)
    )