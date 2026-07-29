import discord
from discord.ext import commands
import os

from config import TOKEN


intents = discord.Intents.all()


class Rockstar(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents
        )


    async def setup_hook(self):

        for filename in os.listdir("./cogs"):

            if filename.endswith(".py") and filename != "__init__.py":

                try:
                    await self.load_extension(
                        f"cogs.{filename[:-3]}"
                    )

                    print(
                        f"Loaded {filename}"
                    )

                except Exception as e:

                    print(
                        f"Failed loading {filename}: {e}"
                    )


        synced = await self.tree.sync()

        print(
            f"Synced {len(synced)} commands"
        )



bot = Rockstar()


@bot.event
async def on_ready():

    print("--------------------------------")
    print(f"🎸 Rockstar online as {bot.user}")
    print("--------------------------------")



bot.run(TOKEN)