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
    "mod": 1049832907079954492,
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
        await ctx.send_response("```Server Synced...```", delete_after=5)

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
                    
            except AttributeError:
                embed.add_field(name="Invite Used", value="Joined from listing site or custom URL.")
                embed.add_field(name="Inviter", value="N/A")
        
        embed.add_field(name="User ID", value=user.id)
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%d/%m/%Y %H:%M:%S"))
        embed.add_field(name="Created Account", value=user.created_at.strftime("%d/%m/%Y %H:%M:%S"))

        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))

        if member.avatar != None:
            embed.set_thumbnail(url=member.avatar.url)

        embed.set_author(name="MG Log Bot", url=self.client.user.avatar.url)
        

        await self.client.get_channel(CHANNELS["invite"]).send(embed=embed)
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
            except AttributeError:
                embed.add_field(name="Invite Used", value="Joined from listing site or custom URL.")
                embed.add_field(name="Inviter", value="N/A")
        # Get the User object so we can get their avatar as they're no longer a member.
        user = await self.client.fetch_user(member.id)

        embed.add_field(name="User ID", value=user.id)
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%d/%m/%Y %H:%M:%S"))
        embed.add_field(name="Created Account", value=user.created_at.strftime("%d/%m/%Y %H:%M:%S"))

        embed.set_thumbnail(url=user.avatar.url)
        embed.set_author(name="MG Log Bot", url=self.client.user.avatar.url)
        
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))

        # Remove their Rules reaction.
        reac_remove = await self.client.get_channel(820097714154242098).get_partial_message(1002591595792699412).remove_reaction("\U00002705", member)
        await self.client.get_channel(CHANNELS["join-leave"]).send(embed=embed)
        await self.client.get_channel(CHANNELS["invite"]).send(embed=embed)


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
        embed.set_author(name="MG Log Bot", url=self.client.user.avatar.url)
        
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
            embed.set_author(name="MG Log Bot", url=self.client.user.avatar.url)            
            
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
                embed.add_field(name="Before", value=f"{before.content[:1000]}...")
            else:
                embed.add_field(name="Before", value=f"{before.content[:1000]}")
        if len(after.content):
            if len(after.content) > 2000:
                embed.add_field(name="After", value=f"{after.content[:1000]}...")
            else:
                embed.add_field(name="After", value=f"{after.content[:1000]}")
        
        embed.set_thumbnail(url=after.author.avatar.url)
        embed.set_author(name="MG Log Bot", url=self.client.user.avatar.url)
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))

        await self.client.get_channel(CHANNELS["message"]).send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_clear(self, payload):
        """Logs when a reaction is cleared"""
        embed = discord.Embed(title="Reaction Cleared", description=f"A reaction was cleared.", color=0x00ff00)
        
        embed.set_thumbnail(url=after.author.avatar.url)
        embed.set_author(name="MG Log Bot", url=self.client.user.avatar.url)
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))

        await self.client.get_channel(CHANNELS["mod"]).send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """Logs when a reaction is removed"""
        user = await self.client.fetch_user(payload.user_id)
        embed = discord.Embed(title="Reaction Removed", description=f"A reaction was removed by {user.display_name} ({payload.user_id}).", color=0x00ff00)
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))
        embed.set_thumbnail(url=user.avatar.url)
        embed.set_author(name="MG Log Bot", url=self.client.user.avatar.url)

        await self.client.get_channel(CHANNELS["mod"]).send(embed=embed)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        pass

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Logs when a member updates their profile or roles."""
        # Iterate through teh before/after and add the updated attributes as fields to the embed, note in the title if they change their avatar. Check for name, discriminator, profile avatar or info updates, new roles or removed roles.
        embed = discord.Embed(title="Member Updated", description=f"{after} has updated their profile.", color=0x00ff00)
        if before.avatar.url != after.avatar.url:
            embed.add_field(name="Avatar Updated!", value=f"{before.avatar.url} to {after.avatar.url}")
        if before.name != after.name:
            embed.add_field(name="Name Updated", value=f"{before.name} to {after.name}")
        if before.discriminator != after.discriminator:
            embed.add_field(name="Discriminator Updated", value=f"{before.discriminator} to {after.discriminator}")
        if before.nick != after.nick:
            embed.add_field(name="Nickname Updated", value=f"{before.nick} to {after.nick}")
        if before.roles != after.roles:
            for role in before.roles:
                if role not in after.roles:
                    embed.add_field(name="Role Removed", value=f"{role.mention}")
            for role in after.roles:
                if role not in before.roles:
                    embed.add_field(name="Role Added", value=f"{role.mention}")
        
        # Check if activity or custom status changed.
        embed.set_thumbnail(url=after.avatar.url)
        embed.set_author(name="MG Log Bot", url=self.client.user.avatar.url)
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))

        await self.client.get_channel(CHANNELS["member"]).send(embed=embed)

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
        embed.set_author(name="MG Log Bot", url=self.client.user.avatar.url)
        
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))
        await self.client.get_channel(CHANNELS["voice"]).send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        """Logs when the server updates"""

        embed = discord.Embed(title="Server Updated", description=f"The server has been updated.", color=0xffff00)
        embed.add_field(name="Before", value=f"Name: {before}\nOwner: {before}\nRegion: {before}\nVerification Level: {before}\nDefault Notification Level: {before}\nExplicit Content Filter Level: {before}")
        embed.add_field(name="After", value=f"Name: {after}\nOwner: {after}\nRegion: {after}\nVerification Level: {after}\nDefault Notification Level: {after}\nExplicit Content Filter Level: {after}")
        embed.set_thumbnail(url=self.client.user.avatar.url)
        embed.set_author(name="MG Log Bot", url=self.client.user.avatar.url)
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))

        await self.client.get_channel(CHANNELS["server"]).send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        """Logs when a role is created"""

        embed = discord.Embed(title="Role Created", description=f"A new role has been created.", color=0x00ff00)
        embed.add_field(name="Role Name", value=f"{role}")
        embed.set_thumbnail(url=self.client.user.avatar.url)
        embed.set_author(name="MG Log Bot", url=self.client.user.avatar.url)
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))        

        await self.client.get_channel(CHANNELS["role"]).send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        """Logs when a role is deleted"""

        embed = discord.Embed(title="Role Deleted", description=f"A role has been deleted.", color=0xff0000)
        embed.add_field(name="Role Name", value=f"{role}")
        embed.set_thumbnail(url=self.client.user.avatar.url)
        embed.set_author(name="MG Log Bot", url=self.client.user.avatar.url)
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))        

        await self.client.get_channel(CHANNELS["role"]).send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        """Logs when a role is updated"""

        embed = discord.Embed(title="Role Updated", description=f"A role has been updated.", color=0xffff00)
        embed.add_field(name="Before", value=f"Name: {before}\nPermissions: {before}\nPosition: {before}\nHoist: {before}\nMentionable: {before}")
        embed.add_field(name="After", value=f"Name: {after}\nPermissions: {after}\nPosition: {after}\nHoist: {after}\nMentionable: {after}")
        embed.set_thumbnail(url=self.client.user.avatar.url)
        embed.set_author(name="MG Log Bot", url=self.client.user.avatar.url)
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))        

        await self.client.get_channel(CHANNELS["role"]).send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        """Logs when a member is banned"""

        embed = discord.Embed(title="Member Banned", description=f"{user} has been banned from the server.", color=0xff0000)
        embed.set_thumbnail(url=user.avatar.url)
        embed.set_author(name="MG Log Bot", url=self.client.user.avatar.url)
        
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))
        await self.client.get_channel(820097714154242098).get_partial_message(1002591595792699412).remove_reaction("\U00002705", user)
        await self.client.get_channel(CHANNELS["mod"]).send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        """Logs when a member is unbanned"""

        embed = discord.Embed(title="Member Unbanned", description=f"{user} has been unbanned from the server.", color=0x00ff00)
        embed.set_thumbnail(url=user.avatar.url)
        
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))
        embed.set_author(name="MG Log Bot", url=self.client.user.avatar.url)

        await self.client.get_channel(CHANNELS["mod"]).send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        """Logs when a channel is created"""

        embed = discord.Embed(title=f"Channel Created: {channel.name}", color=0x00ff00)
        embed.add_field(name="Channel Name", value=f"{channel}")
        embed.set_thumbnail(url=self.client.user.avatar.url)
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))
        embed.set_author(name="MG Log Bot", url=self.client.user.avatar.url)

        await self.client.get_channel(CHANNELS["channel"]).send(embed=embed)
        await sync_templates(channel.guild)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        """Logs when a channel is deleted"""

        embed = discord.Embed(title=f"Channel Deleted: {channel.name}", color=0xff0000)
        embed.add_field(name="Channel Name", value=f"{channel}")
        embed.set_thumbnail(url=self.client.user.avatar.url)
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))
        embed.set_author(name="MG Log Bot", url=self.client.user.avatar.url)

        await self.client.get_channel(CHANNELS["channel"]).send(embed=embed)
        await sync_templates(channel.guild)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        """Logs when a channel is updated"""

        embed = discord.Embed(title=f"{before.name}", description=f"Channel updated!", color=0x00ff00)
        embed.set_thumbnail(url=before.guild.icon.url)
        
        embed.timestamp = datetime.datetime.utcnow()

        if before.name != after.name:
            embed.add_field(name="Name", value=f"```{before.name}``` -> ```{after.name}```", inline=False)

        if after.type == discord.ChannelType.text or after.type == discord.ChannelType.news:
            if before.topic != after.topic:
                embed.add_field(name="Topic", value=f"```{before.topic}``` -> ```{after.topic}```", inline=False)

            if before.slowmode_delay != after.slowmode_delay:
                embed.add_field(name="Slowmode Delay", value=f"```{before.slowmode_delay} ``` -> ```{after.slowmode_delay}```", inline=False)
        
            if before.is_news() != after.is_news():
                embed.add_field(name="News Channel", value=f"```{before.is_news()}``` -> ```{after.is_news()}```", inline=False)

            if before.is_nsfw() != after.is_nsfw():
                embed.add_field(name="NSFW", value=f"{before.is_nsfw()}``` -> ```{after.is_nsfw()}```", inline=False)     

        if before.position != after.position:
            embed.add_field(name="Position", value=f"```{before.position}``` -> ```{after.position}```", inline=False)

        if before.overwrites!= after.overwrites:
            embed.add_field(name="Permission Overwrites", value="Changed")
            # iterate over the overwrites dict in before/after and list the changes.
            for key, value in before.overwrites.items():
                if key not in after.overwrites:
                    embed.add_field(name=f"{key}", value=f"```{value} ``` -> ```Removed```", inline=False)
                elif value != after.overwrites[key]:
                    embed.add_field(name=f"{key}", value=f"```{value} ``` -> ```{after.overwrites[key]}```", inline=False)

        if before.category is None and after.category is not None:
            embed.add_field(name="Category", value=f"```None``` -> ```{after.category}```", inline=False)

        elif before.category is not None and after.category is None:
            embed.add_field(name="Category", value=f"```{before.category} ``` -> ```None```", inline=False)

        elif before.category != after.category:
            embed.add_field(name="Category", value=f"```{before.category} ``` -> ```{after.category}```", inline=False)     
        
        embed.set_thumbnail(url=self.client.user.avatar.url)
        embed.set_author(name="MG Log Bot", url=self.client.user.avatar.url)
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))

        await self.client.get_channel(CHANNELS["channel"]).send(embed=embed)
        await sync_templates(after.guild)

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        """Logs when emojis are updated"""

        embed = discord.Embed(title="Emojis Updated", description=f"The server emojis have been updated.", color=0xffff00)
        emoji_added = []
        emoji_removed = []

        embed.set_thumbnail(url=self.client.user.avatar.url)
        embed.set_author(name="MG Log Bot", url=self.client.user.avatar.url)
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))
        
        for emoji in before:
            if emoji not in after:
                emoji_removed.append(emoji)
        for emoji in after:
            if emoji not in before:
                emoji_added.append(emoji)
        
        if len(emoji_removed):
            embed.add_field(name="Removed", value=f"{', '.join([str(e) for e in emoji_removed])}")
        
        if len(emoji_added):
            embed.add_field(name="Added", value=f"{', '.join([str(e) for e in emoji_added])}")
        
        
        await self.client.get_channel(CHANNELS["server"]).send(embed=embed)


    @commands.Cog.listener()
    async def on_guild_integrations_update(self, guild):
        """Logs when integrations are updated"""

        embed = discord.Embed(title="Integrations Updated", description=f"The server integrations have been updated.", color=0xffff00)
        embed.set_thumbnail(url=self.client.user.avatar.url)
        embed.set_author(name="MG Log Bot", url=self.client.user.avatar.url)
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))

        await self.client.get_channel(CHANNELS["server"]).send(embed=embed)

    @commands.Cog.listener()
    async def on_webhooks_update(self, channel):
        """Logs when webhooks are updated"""

        embed = discord.Embed(title="Webhooks Updated", description=f"The webhooks in {channel} have been updated.", color=0xffff00)
        embed.set_thumbnail(url=self.client.user.avatar.url)
        embed.set_author(name="MG Log Bot", url=self.client.user.avatar.url)
        embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))

        await self.client.get_channel(CHANNELS["server"]).send(embed=embed)        


def setup(client):
    client.add_cog(Serverlogs(client))
