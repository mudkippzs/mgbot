import datetime
import discord
from discord.ext import commands
import sys
import os

import pytz

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '.')))


from clogger import clogger


CHANNELS = {
    "mod": 820095623553482763,
    "join-leave": 822866616487378975,
    "server": 820077049036406808,
    "invite": 822866429215899699,
    "channel": 822866452298203198,
    "role": 822866470546964560,
    "voice": 822866489773391872,
    "message": 822866537303638046,
    "member": 822866553187598367
}


async def sync_templates(guild: discord.Guild):
    """
    Sync templates for a guild.
    """
    # Get the guilds templates
    templates = await guild.templates()

    # Iterate through the templates and sync them
    for template in templates:
        await template.sync()

class Serverlogs(commands.Cog):
    def __init__(self, client):
        self.client = client

    def find_invite_by_code(self, after_invites, guild, code):
        for inv in after_invites:
            if inv.code == code:
                return inv

    @commands.slash_command()
    async def testinvites(self, ctx):
        clogger(self.client.invites)

    @commands.slash_command(name="synctemplate", description="Sync Server Template.")
    async def sync_template(self, ctx):
        await sync_templates(ctx.guild)
        await ctx.send_response("```Server Synced```", delete_after=5)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Logs when a member joins the server"""
        before_invites = self.client.invites[str(member.guild.id)]
        after_invites = await member.guild.invites()
        embed = discord.Embed(title="Member Joined", description=f"{member} has joined the server.", color=0x00ff00)
        for invite in before_invites:
            try:
                if invite.uses < self.find_invite_by_code(after_invites, member.guild, invite.code).uses:
                    embed.add_field(name="Invite Used", value=f"{invite.code}")
                    embed.add_field(name="Inviter", value=f"{invite.inviter}")
                    await self.client.get_channel(CHANNELS["invite"]).send(embed=embed)
            except AttributeError:
                embed.add_field(name="Invite Used", value="Joined from listing site or custom URL.")
                embed.add_field(name="Inviter", value="N/A")
        
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))
        if member.avatar != None:
            embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"ID: {member.id}")

        await self.client.get_channel(CHANNELS["join-leave"]).send(embed=embed)


    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Logs when a member joins the server"""
        before_invites = self.client.invites[str(member.guild.id)]
        after_invites = await member.guild.invites()
        embed = discord.Embed(title="Member Left", description=f"{member} has left the server.", color=0xff0000)
        for invite in before_invites:
            try:
                if invite.uses < self.find_invite_by_code(after_invites, member.guild, invite.code).uses:
                    embed.add_field(name="Invite Used", value=f"{invite.code}")
                    embed.add_field(name="Inviter", value=f"{invite.inviter}")
                    await self.client.get_channel(CHANNELS["invite"]).send(embed=embed)
            except AttributeError:
                embed.add_field(name="Invite Used", value="Joined from listing site or custom URL.")
                embed.add_field(name="Inviter", value="N/A")
        
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"ID: {member.id}")

        reac_remove = await self.client.get_channel(820097714154242098).get_partial_message(1002591595792699412).remove_reaction("\U00002705", member)
        await self.client.get_channel(CHANNELS["join-leave"]).send(embed=embed)


    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Logs when a message is deleted"""        
        if message.author == self.client.user:
            return

        embed = discord.Embed(title="Message Deleted", description=f"A message was deleted in {message.channel}.", color=0xff0000)
        embed.add_field(name="Author", value=f"{message.author}")
        if len(message.content):
            embed.add_field(name="Content", value=f"{message.content}")
        embed.set_thumbnail(url=message.author.avatar.url)
        embed.set_footer(text=f"ID: {message.id}")
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))

        await self.client.get_channel(CHANNELS["message"]).send(embed=embed)

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        """Logs when multiple messages are deleted"""
        for message in messages:
            if message == self.client.user:
                return

            embed = discord.Embed(title="Message Deleted", description=f"A message was deleted in {message.channel}.", color=0xff0000)
            embed.add_field(name="Author", value=f"{message.author}")
            
            if len(message.content):
                embed.add_field(name="Content", value=f"{message.content}")
            
            embed.set_thumbnail(url=message.author.avatar.url)
            embed.set_footer(text=f"ID: {message.id}")
            embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))

            await self.client.get_channel(CHANNELS["message"]).send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Logs when a message is edited"""
        if before.author == self.client.user:
            return

        embed = discord.Embed(title="Message Edited", description=f"A message was edited in {before.channel}.", color=0xffff00)
        embed.add_field(name="Author", value=f"{before.author}")
        
        if len(before.content):
            if len(before.content) > 2000:
                embed.add_field(name="Before", value=f"{before.content[:1997]}...")
            else:
                embed.add_field(name="Before", value=f"{before.content}")
        if len(after.content):
            if len(after.content) > 2000:
                embed.add_field(name="After", value=f"{after.content[:1997]}...")
            else:
                embed.add_field(name="After", value=f"{after.content}")
        
        embed.set_thumbnail(url=before.author.avatar.url)
        embed.set_footer(text=f"ID: {before.id}")
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))

        await self.client.get_channel(CHANNELS["message"]).send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_clear(self, payload):
        """Logs when a reaction is cleared"""
        user = await self.client.fetch_user(payload.user_id)
        embed = discord.Embed(title="Reaction Cleared", description=f"A reaction was cleared by {user.display_name} ({payload.user_id}).", color=0x00ff00)
        embed.set_footer(text=f"ID: {payload.message_id}")
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))

        await self.client.get_channel(CHANNELS["mod"]).send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """Logs when a reaction is removed"""
        user = await self.client.fetch_user(payload.user_id)
        embed = discord.Embed(title="Reaction Removed", description=f"A reaction was removed by {user.display_name} ({payload.user_id}).", color=0x00ff00)
        embed.set_footer(text=f"ID: {payload.message_id}")
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))

        await self.client.get_channel(CHANNELS["mod"]).send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Logs when a member updates their profile"""
        embed = discord.Embed(title="Member Updated", description=f"{before} has updated their profile.", color=0xffff00)
        embed.add_field(name="Before", value=f"```Name: {before.name}\nNick: {before.nick}```\nRoles: {''.join([r.mention for r in before.roles])}")
        embed.add_field(name="After", value=f"```Name: {after.name}\nNick: {after.nick}```\nRoles: {''.join([r.mention for r in after.roles])}")
        if after.avatar != None:
            embed.set_thumbnail(url=after.avatar.url)
        embed.set_footer(text=f"ID: {after.id}")
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))

        member_log = await self.client.get_channel(CHANNELS["member"]).send(embed=embed)

        if before.roles != after.roles:
            role_added = [r for r in after.roles if r not in [r for r in before.roles]]
            if len(role_added) > 0:
                embed.add_field(name="New Role:", value=role_added[0].mention)
            else:
                role_removed = [r for r in before.roles if r not in [r for r in after.roles]]
                if len(role_removed) > 0:
                    embed.add_field(name="Removed Role:", value=role_removed[0].mention)

            await self.client.get_channel(CHANNELS["role"]).send(embed=embed)

        else:
            return

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Logs when a member joins or leaves a voice channel"""
        if before.channel == after.channel:
            return

        if before.channel is None:
            embed = discord.Embed(title="Voice Channel Update", color=0x00ff00)
            embed.description = f"{member} has joined {after.channel}"
        elif after.channel is None:
            embed = discord.Embed(title="Voice Channel Update", color=0xff0000)
            embed.description = f"{member} has left {before.channel}"
        else:
            embed = discord.Embed(title="Voice Channel Update", color=0xff00ff)
            embed.description = f"{member} has moved from {before.channel} to {after.channel}"

        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"ID: {member.id}")
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))
        await self.client.get_channel(CHANNELS["voice"]).send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        """Logs when the server updates"""

        embed = discord.Embed(title="Server Updated", description=f"The server has been updated.", color=0xffff00)
        embed.add_field(name="Before", value=f"Name: {before}\nOwner: {before}\nRegion: {before}\nVerification Level: {before}\nDefault Notification Level: {before}\nExplicit Content Filter Level: {before}")
        embed.add_field(name="After", value=f"Name: {after}\nOwner: {after}\nRegion: {after}\nVerification Level: {after}\nDefault Notification Level: {after}\nExplicit Content Filter Level: {after}")
        embed.set_thumbnail(url=self.client.user)
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))

        await self.client.get_channel(CHANNELS["server"]).send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        """Logs when a role is created"""

        embed = discord.Embed(title="Role Created", description=f"A new role has been created.", color=0x00ff00)
        embed.add_field(name="Role Name", value=f"{role}")
        embed.set_thumbnail(url=self.client.user.avatar.url)
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))

        

        await self.client.get_channel(CHANNELS["role"]).send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        """Logs when a role is deleted"""

        embed = discord.Embed(title="Role Deleted", description=f"A role has been deleted.", color=0xff0000)
        embed.add_field(name="Role Name", value=f"{role}")
        embed.set_thumbnail(url=self.client.user.avatar.url)
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))

        

        await self.client.get_channel(CHANNELS["role"]).send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        """Logs when a role is updated"""

        embed = discord.Embed(title="Role Updated", description=f"A role has been updated.", color=0xffff00)
        embed.add_field(name="Before", value=f"Name: {before}\nPermissions: {before}\nPosition: {before}\nHoist: {before}\nMentionable: {before}")
        embed.add_field(name="After", value=f"Name: {after}\nPermissions: {after}\nPosition: {after}\nHoist: {after}\nMentionable: {after}")
        embed.set_thumbnail(url=self.client.user.avatar.url)
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))

        

        await self.client.get_channel(CHANNELS["role"]).send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        """Logs when a member is banned"""

        embed = discord.Embed(title="Member Banned", description=f"{user} has been banned from the server.", color=0xff0000)
        embed.set_thumbnail(url=user.avatar.url)
        embed.set_footer(text=f"ID: {user}")
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))
        await self.client.get_channel(820097714154242098).get_partial_message(1002591595792699412).remove_reaction("\U00002705", user)
        await self.client.get_channel(CHANNELS["mod"]).send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        """Logs when a member is unbanned"""

        embed = discord.Embed(title="Member Unbanned", description=f"{user} has been unbanned from the server.", color=0x00ff00)
        embed.set_thumbnail(url=user.avatar.url)
        embed.set_footer(text=f"ID: {user}")
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))

        await self.client.get_channel(CHANNELS["mod"]).send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        """Logs when a channel is created"""

        embed = discord.Embed(title="Channel Created", description=f"A new channel has been created.", color=0x00ff00)
        embed.add_field(name="Channel Name", value=f"{channel}")
        embed.set_thumbnail(url=self.client.user.avatar.url)
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))

        await self.client.get_channel(CHANNELS["channel"]).send(embed=embed)
        await sync_templates(channel.guild)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """Logs when a channel is deleted"""

        embed = discord.Embed(title="Channel Deleted", description=f"A channel has been deleted.", color=0xff0000)
        embed.add_field(name="Channel Name", value=f"{channel}")
        embed.set_thumbnail(url=self.client.user.avatar.url)
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))

        await self.client.get_channel(CHANNELS["channel"]).send(embed=embed)
        await sync_templates(channel.guild)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        """Logs when a channel is updated"""

        embed = discord.Embed(title="Channel Updated", description=f"A channel has been updated.", color=0xffff00)

        try:
            before_topic = "None" if before.topic == None else before.topic
            after_topic = "None" if after.topic == None else after.topic

            embed.add_field(name="Before", value=f"```markdown\n**Name:** {before.name}\n**Position:** {before.position}\n**Category:** {before.category}\n**Topic:** {before_topic}\n**NSFW:** {before.nsfw}```")
            embed.add_field(name="After", value=f"```markdown\n**Name:** {after.name}\n**Position:** {after.position}\n**Category:** {after.category}\n**Topic:** {after_topic}\n**NSFW:** {after.nsfw}```")
        except:
            pass
        
        embed.set_thumbnail(url=self.client.user.avatar.url)
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))

        await self.client.get_channel(CHANNELS["channel"]).send(embed=embed)
        await sync_templates(after.guild)

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        """Logs when emojis are updated"""

        embed = discord.Embed(title="Emojis Updated", description=f"The server emojis have been updated.", color=0xffff00)
        embed.add_field(name="Before", value=f"{before}")
        embed.add_field(name="After", value=f"{after}")
        embed.set_thumbnail(url=self.client.user.avatar.url)
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))

        await self.client.get_channel(CHANNELS["server"]).send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_integrations_update(self, guild):
        """Logs when integrations are updated"""

        embed = discord.Embed(title="Integrations Updated", description=f"The server integrations have been updated.", color=0xffff00)
        embed.set_thumbnail(url=self.client.user.avatar.url)
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))

        await self.client.get_channel(CHANNELS["server"]).send(embed=embed)

    @commands.Cog.listener()
    async def on_webhooks_update(self, channel):
        """Logs when webhooks are updated"""

        embed = discord.Embed(title="Webhooks Updated", description=f"The webhooks in {channel} have been updated.", color=0xffff00)
        embed.set_thumbnail(url=self.client.user.avatar.url)
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))

        await self.client.get_channel(CHANNELS["server"]).send(embed=embed)        


def setup(client):
    client.add_cog(Serverlogs(client))
