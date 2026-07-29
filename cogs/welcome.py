import discord
from discord.ext import commands

from config import (
    JOIN_CHANNEL_ID,
    LEAVE_CHANNEL_ID,
    JOIN_TITLE,
    JOIN_MESSAGE,
    LEAVE_TITLE,
    LEAVE_MESSAGE,
    JOIN_GIF,
    LEAVE_GIF,
    EMBED_COLOR,
    FOOTER_TEXT
)


class Welcome(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_member_join(
        self,
        member: discord.Member
    ):

        channel = self.bot.get_channel(
            JOIN_CHANNEL_ID
        )

        if channel is None:
            return


        embed = discord.Embed(
            title=JOIN_TITLE,
            description=JOIN_MESSAGE.format(
                member=member.mention,
                server=member.guild.name,
                count=member.guild.member_count
            ),
            color=EMBED_COLOR
        )


        embed.set_thumbnail(
            url=member.display_avatar.url
        )


        if JOIN_GIF:
            embed.set_image(
                url=JOIN_GIF
            )


        embed.set_footer(
            text=FOOTER_TEXT
        )

        embed.timestamp = discord.utils.utcnow()


        await channel.send(
            embed=embed
        )



    @commands.Cog.listener()
    async def on_member_remove(
        self,
        member: discord.Member
    ):

        channel = self.bot.get_channel(
            LEAVE_CHANNEL_ID
        )

        if channel is None:
            return


        embed = discord.Embed(
            title=LEAVE_TITLE,
            description=LEAVE_MESSAGE.format(
                member=member.mention,
                server=member.guild.name
            ),
            color=EMBED_COLOR
        )


        embed.set_thumbnail(
            url=member.display_avatar.url
        )


        if LEAVE_GIF:
            embed.set_image(
                url=LEAVE_GIF
            )


        embed.set_footer(
            text=FOOTER_TEXT
        )

        embed.timestamp = discord.utils.utcnow()


        await channel.send(
            embed=embed
        )



async def setup(bot):
    await bot.add_cog(
        Welcome(bot)
    )