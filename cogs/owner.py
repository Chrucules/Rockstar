import json
import os

import aiosqlite
import discord
from discord.ext import commands

import config
from utils.embeds import success, error


DATABASE_PATH = "database/safety.db"

LOCKED_PERMISSIONS = (
    "send_messages",
    "add_reactions",
    "connect",
    "speak",
    "stream",
    "create_public_threads",
    "create_private_threads",
    "send_messages_in_threads",
)


class Owner(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db_path = DATABASE_PATH


    async def cog_load(self):
        os.makedirs("database", exist_ok=True)

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS safety_state (
                    guild_id INTEGER PRIMARY KEY,
                    enabled INTEGER NOT NULL DEFAULT 0
                )
            """)

            await db.execute("""
                CREATE TABLE IF NOT EXISTS safety_members (
                    guild_id INTEGER NOT NULL,
                    member_id INTEGER NOT NULL,
                    role_ids TEXT NOT NULL,
                    PRIMARY KEY (guild_id, member_id)
                )
            """)

            await db.execute("""
                CREATE TABLE IF NOT EXISTS safety_channels (
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    overwrites TEXT NOT NULL,
                    PRIMARY KEY (guild_id, channel_id)
                )
            """)

            await db.commit()

            cursor = await db.execute(
                "SELECT COUNT(*) FROM safety_state WHERE enabled = 1"
            )
            active_count = (await cursor.fetchone())[0]

        config.SAFETY_MODE = active_count > 0


    def is_owner(self, user):
        return user.id == config.OWNER_ID


    def is_exempt(self, member, guild):
        return (
            member.id == config.OWNER_ID
            or member.id == guild.owner_id
            or member.id == self.bot.user.id
        )


    def serialize_overwrites(self, channel):
        saved = []

        for target, overwrite in channel.overwrites.items():
            allow, deny = overwrite.pair()

            saved.append({
                "type": "role" if isinstance(target, discord.Role) else "member",
                "id": target.id,
                "allow": allow.value,
                "deny": deny.value
            })

        return json.dumps(saved)


    def deserialize_overwrites(self, guild, raw_data):
        restored = {}

        for item in json.loads(raw_data):
            if item["type"] == "role":
                target = guild.get_role(item["id"])
            else:
                target = guild.get_member(item["id"])

            if target is None:
                continue

            allow = discord.Permissions(item["allow"])
            deny = discord.Permissions(item["deny"])

            restored[target] = discord.PermissionOverwrite.from_pair(
                allow,
                deny
            )

        return restored


    async def safety_is_enabled(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                SELECT enabled
                FROM safety_state
                WHERE guild_id = ?
                """,
                (guild_id,)
            )

            row = await cursor.fetchone()

        return bool(row and row[0])


    async def enable_safety(self, guild):
        if await self.safety_is_enabled(guild.id):
            return False, "Safety mode is already enabled."

        role_failures = []
        channel_failures = []

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM safety_members WHERE guild_id = ?",
                (guild.id,)
            )

            await db.execute(
                "DELETE FROM safety_channels WHERE guild_id = ?",
                (guild.id,)
            )

            # Save member roles
            for member in guild.members:
                if self.is_exempt(member, guild):
                    continue

                role_ids = [
                    role.id
                    for role in member.roles
                    if role != guild.default_role
                ]

                await db.execute(
                    """
                    INSERT OR REPLACE INTO safety_members
                    (guild_id, member_id, role_ids)
                    VALUES (?, ?, ?)
                    """,
                    (
                        guild.id,
                        member.id,
                        json.dumps(role_ids)
                    )
                )

            # Save exact channel permission overwrites
            for channel in guild.channels:
                await db.execute(
                    """
                    INSERT OR REPLACE INTO safety_channels
                    (guild_id, channel_id, overwrites)
                    VALUES (?, ?, ?)
                    """,
                    (
                        guild.id,
                        channel.id,
                        self.serialize_overwrites(channel)
                    )
                )

            await db.execute(
                """
                INSERT OR REPLACE INTO safety_state
                (guild_id, enabled)
                VALUES (?, 1)
                """,
                (guild.id,)
            )

            await db.commit()

        # Strip manageable roles
        bot_member = guild.me

        for member in guild.members:
            if self.is_exempt(member, guild):
                continue

            removable_roles = [
                role
                for role in member.roles
                if (
                    role != guild.default_role
                    and not role.managed
                    and role < bot_member.top_role
                )
            ]

            if not removable_roles:
                continue

            try:
                await member.remove_roles(
                    *removable_roles,
                    reason="Rockstar safety mode enabled"
                )
            except (discord.Forbidden, discord.HTTPException):
                role_failures.append(member.id)

        # Lock every channel
        for channel in guild.channels:
            try:
                overwrites = dict(channel.overwrites)

                everyone_overwrite = overwrites.get(
                    guild.default_role,
                    discord.PermissionOverwrite()
                )

                for permission in LOCKED_PERMISSIONS:
                    setattr(everyone_overwrite, permission, False)

                overwrites[guild.default_role] = everyone_overwrite

                # Remove any direct permission that could let another
                # member bypass the @everyone lock.
                for target, overwrite in list(overwrites.items()):
                    if not isinstance(target, discord.Member):
                        continue

                    if self.is_exempt(target, guild):
                        continue

                    for permission in LOCKED_PERMISSIONS:
                        setattr(overwrite, permission, False)

                    overwrites[target] = overwrite

                # Explicitly allow the configured owner.
                owner_member = guild.get_member(config.OWNER_ID)

                if owner_member:
                    owner_overwrite = overwrites.get(
                        owner_member,
                        discord.PermissionOverwrite()
                    )

                    owner_overwrite.view_channel = True
                    owner_overwrite.send_messages = True
                    owner_overwrite.add_reactions = True
                    owner_overwrite.connect = True
                    owner_overwrite.speak = True
                    owner_overwrite.stream = True
                    owner_overwrite.create_public_threads = True
                    owner_overwrite.create_private_threads = True
                    owner_overwrite.send_messages_in_threads = True

                    overwrites[owner_member] = owner_overwrite

                await channel.edit(
                    overwrites=overwrites,
                    reason="Rockstar safety mode enabled"
                )

            except (discord.Forbidden, discord.HTTPException, TypeError):
                channel_failures.append(channel.id)

        config.SAFETY_MODE = True

        message = (
            "Safety mode enabled.\n"
            f"Role failures: `{len(role_failures)}`\n"
            f"Channel failures: `{len(channel_failures)}`"
        )

        return True, message


    async def disable_safety(self, guild):
        if not await self.safety_is_enabled(guild.id):
            return False, "Safety mode is not enabled."

        role_failures = []
        channel_failures = []

        async with aiosqlite.connect(self.db_path) as db:
            member_cursor = await db.execute(
                """
                SELECT member_id, role_ids
                FROM safety_members
                WHERE guild_id = ?
                """,
                (guild.id,)
            )
            saved_members = await member_cursor.fetchall()

            channel_cursor = await db.execute(
                """
                SELECT channel_id, overwrites
                FROM safety_channels
                WHERE guild_id = ?
                """,
                (guild.id,)
            )
            saved_channels = await channel_cursor.fetchall()

        bot_member = guild.me

        # Restore member roles
        for member_id, raw_role_ids in saved_members:
            member = guild.get_member(member_id)

            if member is None or self.is_exempt(member, guild):
                continue

            roles_to_restore = []

            for role_id in json.loads(raw_role_ids):
                role = guild.get_role(role_id)

                if (
                    role is not None
                    and not role.managed
                    and role < bot_member.top_role
                ):
                    roles_to_restore.append(role)

            if not roles_to_restore:
                continue

            try:
                await member.add_roles(
                    *roles_to_restore,
                    reason="Rockstar safety mode disabled"
                )
            except (discord.Forbidden, discord.HTTPException):
                role_failures.append(member.id)

        # Restore exact channel overwrites
        for channel_id, raw_overwrites in saved_channels:
            channel = guild.get_channel(channel_id)

            if channel is None:
                continue

            try:
                restored = self.deserialize_overwrites(
                    guild,
                    raw_overwrites
                )

                await channel.edit(
                    overwrites=restored,
                    reason="Rockstar safety mode disabled"
                )

            except (
                discord.Forbidden,
                discord.HTTPException,
                TypeError,
                json.JSONDecodeError
            ):
                channel_failures.append(channel.id)

        if not role_failures and not channel_failures:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "DELETE FROM safety_members WHERE guild_id = ?",
                    (guild.id,)
                )

                await db.execute(
                    "DELETE FROM safety_channels WHERE guild_id = ?",
                    (guild.id,)
                )

                await db.execute(
                    "DELETE FROM safety_state WHERE guild_id = ?",
                    (guild.id,)
                )

                await db.commit()

            config.SAFETY_MODE = False

            return True, "Safety mode disabled. Roles and channels restored."

        return False, (
            "Safety restoration was only partially completed.\n"
            f"Role failures: `{len(role_failures)}`\n"
            f"Channel failures: `{len(channel_failures)}`\n\n"
            "The backup was kept so `/safety off` can be tried again."
        )


    @discord.app_commands.command(
        name="bot",
        description="Turn Rockstar on or off"
    )
    @discord.app_commands.describe(status="on or off")
    async def control_bot(
        self,
        interaction: discord.Interaction,
        status: str
    ):
        if not self.is_owner(interaction.user):
            await interaction.response.send_message(
                embed=error("Only the Rockstar owner can use this command."),
                ephemeral=True
            )
            return

        status = status.lower().strip()

        if status == "on":
            config.BOT_ENABLED = True

            await interaction.response.send_message(
                embed=success("Rockstar is now enabled.")
            )

        elif status == "off":
            config.BOT_ENABLED = False

            await interaction.response.send_message(
                embed=success("Rockstar is now disabled.")
            )

        else:
            await interaction.response.send_message(
                embed=error("Use `/bot on` or `/bot off`."),
                ephemeral=True
            )


    @discord.app_commands.command(
        name="safety",
        description="Enable or disable server safety mode"
    )
    @discord.app_commands.describe(status="on or off")
    async def safety(
        self,
        interaction: discord.Interaction,
        status: str
    ):
        if not self.is_owner(interaction.user):
            await interaction.response.send_message(
                embed=error("Only the Rockstar owner can use this command."),
                ephemeral=True
            )
            return

        if interaction.guild is None:
            await interaction.response.send_message(
                embed=error("This command can only be used in a server."),
                ephemeral=True
            )
            return

        status = status.lower().strip()

        if status not in ("on", "off"):
            await interaction.response.send_message(
                embed=error("Use `/safety on` or `/safety off`."),
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        if status == "on":
            worked, message = await self.enable_safety(interaction.guild)
        else:
            worked, message = await self.disable_safety(interaction.guild)

        embed = success(message) if worked else error(message)

        await interaction.followup.send(
            embed=embed,
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Owner(bot))