import discord

from config import (
    BOT_NAME,
    EMBED_COLOR,
    FOOTER_TEXT,
    DEFAULT_GIF
)


def create_embed(
    title,
    description,
    color=EMBED_COLOR,
    gif=None
):

    embed = discord.Embed(
        title=f"{BOT_NAME} | {title}",
        description=description,
        color=color
    )

    embed.set_footer(
        text=FOOTER_TEXT
    )

    embed.timestamp = discord.utils.utcnow()

    if gif:
        embed.set_image(url=gif)

    elif DEFAULT_GIF:
        embed.set_image(url=DEFAULT_GIF)

    return embed


def success(message):
    return create_embed(
        "Success",
        f"✅ {message}",
        color=0x00FF00
    )


def error(message):
    return create_embed(
        "Error",
        f"❌ {message}",
        color=0xFF0000
    )


def info(message):
    return create_embed(
        "Information",
        f"ℹ️ {message}"
    )