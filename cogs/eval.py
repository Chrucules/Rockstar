import io
import contextlib
import traceback

import discord
from discord.ext import commands

from config import OWNER_ID
from utils.embeds import success, error


class Eval(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name="eval",
        description="Run Python code (Owner Only)"
    )
    async def eval(
        self,
        interaction: discord.Interaction,
        code: str
    ):

        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message(
                embed=error("You are not authorized to use this command."),
                ephemeral=True
            )
            return

        env = {
            "bot": self.bot,
            "discord": discord,
            "commands": commands,
            "interaction": interaction,
        }

        output = io.StringIO()

        try:
            with contextlib.redirect_stdout(output):
                result = eval(code, env)

            text = output.getvalue()

            if result is not None:
                text += repr(result)

            if not text:
                text = "No output."

            if len(text) > 1900:
                text = text[:1900] + "..."

            await interaction.response.send_message(
                embed=success(f"```py\n{text}\n```")
            )

        except Exception:
            await interaction.response.send_message(
                embed=error(
                    f"```py\n{traceback.format_exc()[:1900]}\n```"
                )
            )


async def setup(bot):
    await bot.add_cog(Eval(bot))