import discord

from config import OWNER_ID


def is_bot_owner(user: discord.User):
    return user.id == OWNER_ID


def can_target(
    moderator: discord.Member,
    target: discord.Member
):
    # Rockstar owner immunity
    if target.id == OWNER_ID:
        return False, "You cannot moderate the Rockstar owner."

    # Server owner immunity
    if target.id == target.guild.owner_id:
        return False, "You cannot moderate the server owner."

    # Cannot target yourself
    if moderator.id == target.id:
        return False, "You cannot moderate yourself."

    # Moderator hierarchy check
    if moderator.top_role <= target.top_role:
        return False, (
            "You cannot moderate someone with "
            "the same or higher role."
        )

    # Bot hierarchy check
    if moderator.guild.me.top_role <= target.top_role:
        return False, (
            "My role is not high enough to moderate this user."
        )

    return True, "OK"


def has_permission(
    member: discord.Member,
    permission: discord.Permissions
):
    return member.guild_permissions >= permission