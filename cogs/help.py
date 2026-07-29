import discord
from discord.ext import commands

from config import (
    EMBED_COLOR,
    FOOTER_TEXT
)


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @discord.app_commands.command(
        name="help",
        description="Shows Rockstar commands"
    )
    async def help(
        self,
        interaction: discord.Interaction
    ):

        embed = discord.Embed(
            title="⭐ Rockstar Commands",
            description="Your complete Rockstar command list.",
            color=EMBED_COLOR
        )


        embed.add_field(
            name="🛡 Moderation",
            value=(
                "`/purge` - Delete messages\n"
                "`/mute` - Timeout a user\n"
                "`/unmute` - Remove timeout\n"
                "`/kick` - Kick a member\n"
                "`/ban` - Ban a member\n"
                "`/unban` - Unban by ID\n"
                "`/lock` - Lock a channel\n"
                "`/unlock` - Unlock a channel\n"
                "`/autorole` - Set join role\n"
                "`/removeautorole` - Remove autorole\n"
                "`/embed` - Send custom embed\n"
                "`/channels` - View channel IDs\n"
                "`/snipe` - Deleted message info\n"
                "`/editsnipe` - Edited message info"
            ),
            inline=False
        )


        embed.add_field(
            name="👤 User",
            value=(
                "`/avatar` - View avatar\n"
                "`/banner` - View banner\n"
                "`/userinfo` - User information\n"
                "`/id` - View user ID"
            ),
            inline=False
        )


        embed.add_field(
            name="👑 Owner",
            value=(
                "`/bot on` - Enable Rockstar\n"
                "`/bot off` - Disable public commands\n"
                "`/safety on` - Emergency lockdown\n"
                "`/safety off` - Restore server"
            ),
            inline=False
        )


        embed.set_footer(
            text=FOOTER_TEXT
        )

        embed.timestamp = discord.utils.utcnow()


        await interaction.response.send_message(
            embed=embed
        )


async def setup(bot):
    await bot.add_cog(
        Help(bot)
    )