import discord
from discord.ext import commands
import asyncio
from datetime import timedelta

from utils.embeds import success, error, create_embed
from utils.permissions import can_target


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.autorole = None
        self.ragebait_users = set()
        self.deleted_messages = {}
        self.edited_messages = {}


    # ==========================
    # MESSAGE TRACKING
    # ==========================

    @commands.Cog.listener()
    async def on_message_delete(self, message):

        if message.author.bot:
            return

        self.deleted_messages[message.channel.id] = message


    @commands.Cog.listener()
    async def on_message_edit(self, before, after):

        if before.author.bot:
            return

        self.edited_messages[before.channel.id] = (
            before,
            after
        )


    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        # Ragebait deletes messages silently
        if message.author.id in self.ragebait_users:

            try:
                await message.delete()

            except:
                pass


    # ==========================
    # AUTOROLE
    # ==========================

    @commands.Cog.listener()
    async def on_member_join(self, member):

        if self.autorole:

            role = member.guild.get_role(
                self.autorole
            )

            if role:
                await member.add_roles(role)



    @discord.app_commands.command(
        name="autorole",
        description="Set the automatic join role"
    )
    @commands.has_permissions(manage_roles=True)
    async def autorole(
        self,
        interaction,
        role: discord.Role
    ):

        self.autorole = role.id

        await interaction.response.send_message(
            embed=success(
                f"Autorole set to {role.mention}"
            )
        )



    @discord.app_commands.command(
        name="removeautorole",
        description="Remove automatic role"
    )
    @commands.has_permissions(manage_roles=True)
    async def removeautorole(
        self,
        interaction
    ):

        self.autorole = None

        await interaction.response.send_message(
            embed=success(
                "Autorole removed."
            )
        )



    # ==========================
    # MODERATION
    # ==========================


    @discord.app_commands.command(
        name="purge",
        description="Delete messages"
    )
    @commands.has_permissions(manage_messages=True)
    async def purge(
        self,
        interaction,
        amount: int
    ):

        await interaction.response.defer(
            ephemeral=True
        )

        deleted = await interaction.channel.purge(
            limit=amount
        )

        await interaction.followup.send(
            embed=success(
                f"Deleted {len(deleted)} messages."
            )
        )



    @discord.app_commands.command(
        name="mute",
        description="Timeout a user"
    )
    @commands.has_permissions(moderate_members=True)
    async def mute(
        self,
        interaction,
        user: discord.Member,
        minutes: int
    ):

        allowed, msg = can_target(
            interaction.user,
            user
        )

        if not allowed:

            await interaction.response.send_message(
                embed=error(msg),
                ephemeral=True
            )

            return


        await user.timeout(
            timedelta(minutes=minutes)
        )


        await interaction.response.send_message(
            embed=success(
                f"{user.mention} muted for {minutes} minutes."
            )
        )



    @discord.app_commands.command(
        name="unmute",
        description="Remove timeout"
    )
    @commands.has_permissions(moderate_members=True)
    async def unmute(
        self,
        interaction,
        user: discord.Member
    ):

        allowed, msg = can_target(
            interaction.user,
            user
        )

        if not allowed:

            await interaction.response.send_message(
                embed=error(msg),
                ephemeral=True
            )

            return


        await user.timeout(None)


        await interaction.response.send_message(
            embed=success(
                f"{user.mention} unmuted."
            )
        )



    @discord.app_commands.command(
        name="kick",
        description="Kick a user"
    )
    @commands.has_permissions(kick_members=True)
    async def kick(
        self,
        interaction,
        user: discord.Member
    ):

        allowed, msg = can_target(
            interaction.user,
            user
        )

        if not allowed:

            await interaction.response.send_message(
                embed=error(msg),
                ephemeral=True
            )

            return


        await user.kick()


        await interaction.response.send_message(
            embed=success(
                f"{user.mention} kicked."
            )
        )



    @discord.app_commands.command(
        name="ban",
        description="Ban a user"
    )
    @commands.has_permissions(ban_members=True)
    async def ban(
        self,
        interaction,
        user: discord.Member
    ):

        allowed, msg = can_target(
            interaction.user,
            user
        )

        if not allowed:

            await interaction.response.send_message(
                embed=error(msg),
                ephemeral=True
            )

            return


        await user.ban()


        await interaction.response.send_message(
            embed=success(
                f"{user.mention} banned."
            )
        )



    @discord.app_commands.command(
        name="unban",
        description="Unban using ID"
    )
    @commands.has_permissions(ban_members=True)
    async def unban(
        self,
        interaction,
        user_id: str
    ):

        user = await self.bot.fetch_user(
            int(user_id)
        )

        await interaction.guild.unban(
            user
        )


        await interaction.response.send_message(
            embed=success(
                f"{user} unbanned."
            )
        )



    # ==========================
    # CHANNEL COMMANDS
    # ==========================


    @discord.app_commands.command(
        name="lock",
        description="Lock channel"
    )
    @commands.has_permissions(manage_channels=True)
    async def lock(
        self,
        interaction
    ):

        overwrite = interaction.channel.overwrites_for(
            interaction.guild.default_role
        )

        overwrite.send_messages = False


        await interaction.channel.set_permissions(
            interaction.guild.default_role,
            overwrite=overwrite
        )


        await interaction.response.send_message(
            embed=success(
                "Channel locked."
            )
        )



    @discord.app_commands.command(
        name="unlock",
        description="Unlock channel"
    )
    @commands.has_permissions(manage_channels=True)
    async def unlock(
        self,
        interaction
    ):

        overwrite = interaction.channel.overwrites_for(
            interaction.guild.default_role
        )

        overwrite.send_messages = True


        await interaction.channel.set_permissions(
            interaction.guild.default_role,
            overwrite=overwrite
        )


        await interaction.response.send_message(
            embed=success(
                "Channel unlocked."
            )
        )



    # ==========================
    # CUSTOM EMBED
    # ==========================


    @discord.app_commands.command(
        name="embed",
        description="Send a custom embed"
    )
    @commands.has_permissions(manage_messages=True)
    async def embed_command(
        self,
        interaction,
        channel: discord.TextChannel,
        title: str,
        description: str,
        gif_url: str = None
    ):

        embed = create_embed(
            title,
            description,
            gif=gif_url
        )


        await channel.send(
            embed=embed
        )


        await interaction.response.send_message(
            embed=success(
                "Embed sent."
            ),
            ephemeral=True
        )



    # ==========================
    # RAGEBAIT
    # ==========================


    @discord.app_commands.command(
        name="ragebait",
        description="Silently ragebait a user"
    )
    @commands.has_permissions(moderate_members=True)
    async def ragebait(
        self,
        interaction,
        user: discord.Member
    ):

        allowed, msg = can_target(
            interaction.user,
            user
        )

        if not allowed:

            await interaction.response.send_message(
                embed=error(msg),
                ephemeral=True
            )

            return


        self.ragebait_users.add(
            user.id
        )


        await interaction.response.send_message(
            embed=success(
                "Ragebait enabled silently."
            ),
            ephemeral=True
        )


        while user.id in self.ragebait_users:

            try:

                await user.timeout(
                    timedelta(seconds=5)
                )

                await asyncio.sleep(5)

                await user.timeout(None)

                await asyncio.sleep(5)


            except:

                break



    @discord.app_commands.command(
        name="unragebait",
        description="Disable ragebait"
    )
    async def unragebait(
        self,
        interaction,
        user: discord.Member
    ):

        self.ragebait_users.discard(
            user.id
        )


        await user.timeout(None)


        await interaction.response.send_message(
            embed=success(
                "Ragebait disabled."
            ),
            ephemeral=True
        )



    # ==========================
    # INFO COMMANDS
    # ==========================


    @discord.app_commands.command(
        name="channels",
        description="List channels and IDs"
    )
    async def channels(
        self,
        interaction
    ):

        text = ""

        for channel in interaction.guild.channels:

            text += (
                f"{channel.mention} "
                f"`{channel.id}`\n"
            )


        await interaction.response.send_message(
            embed=create_embed(
                "Channels",
                text[:4000]
            )
        )



    @discord.app_commands.command(
        name="snipe",
        description="Show deleted message"
    )
    async def snipe(
        self,
        interaction
    ):

        message = self.deleted_messages.get(
            interaction.channel.id
        )

        if not message:

            await interaction.response.send_message(
                embed=error(
                    "Nothing to snipe."
                ),
                ephemeral=True
            )

            return


        await interaction.response.send_message(
            embed=create_embed(
                "Deleted Message",
                f"{message.author.mention}\n\n{message.content}"
            )
        )



    @discord.app_commands.command(
        name="editsnipe",
        description="Show edited message"
    )
    async def editsnipe(
        self,
        interaction
    ):

        data = self.edited_messages.get(
            interaction.channel.id
        )

        if not data:

            await interaction.response.send_message(
                embed=error(
                    "Nothing to editsnipe."
                ),
                ephemeral=True
            )

            return


        before, after = data


        await interaction.response.send_message(
            embed=create_embed(
                "Edited Message",
                (
                    f"Before:\n{before.content}\n\n"
                    f"After:\n{after.content}"
                )
            )
        )



async def setup(bot):
    await bot.add_cog(
        Moderation(bot)
    )