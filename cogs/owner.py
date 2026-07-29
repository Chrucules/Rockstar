import discord
from discord.ext import commands

from config import OWNER_ID
from utils.embeds import success, error


class Owner(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    def is_owner(self, user):
        return user.id == OWNER_ID


    @discord.app_commands.command(
        name="bot",
        description="Turn Rockstar on or off"
    )
    @discord.app_commands.describe(
        status="on or off"
    )
    async def status(
        self,
        interaction: discord.Interaction,
        status: str
    ):

        if not self.is_owner(interaction.user):
            await interaction.response.send_message(
                embed=error(
                    "Only the Rockstar owner can use this command."
                ),
                ephemeral=True
            )
            return


        if status.lower() == "on":

            self.bot.enabled = True

            await interaction.response.send_message(
                embed=success(
                    "Rockstar is now enabled."
                )
            )


        elif status.lower() == "off":

            self.bot.enabled = False

            await interaction.response.send_message(
                embed=success(
                    "Rockstar is now disabled."
                )
            )


        else:

            await interaction.response.send_message(
                embed=error(
                    "Use `/bot on` or `/bot off`."
                ),
                ephemeral=True
            )


    @discord.app_commands.command(
        name="safety",
        description="Enable or disable safety mode"
    )
    @discord.app_commands.describe(
        status="on or off"
    )
    async def safety(
        self,
        interaction: discord.Interaction,
        status: str
    ):

        if not self.is_owner(interaction.user):

            await interaction.response.send_message(
                embed=error(
                    "Only the Rockstar owner can use this command."
                ),
                ephemeral=True
            )
            return


        if status.lower() == "on":

            self.bot.safety_mode = True

            await interaction.response.send_message(
                embed=success(
                    "Safety mode enabled."
                )
            )


        elif status.lower() == "off":

            self.bot.safety_mode = False

            await interaction.response.send_message(
                embed=success(
                    "Safety mode disabled."
                )
            )


        else:

            await interaction.response.send_message(
                embed=error(
                    "Use `/safety on` or `/safety off`."
                ),
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(
        Owner(bot)
    )