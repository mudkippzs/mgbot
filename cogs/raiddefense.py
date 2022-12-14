import datetime
import discord
from discord.ext import commands
import sys
import os
from typing import List

import pytz
import time
from server_logs import CHANNELS


sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '.')))

from clogger import clogger
from utils import *


FILTERED_ROLES = [
    1003025751886549134,
    1003025753316802631,
    1003025754482806824,
    1003025755808202752,
    1003025756437368913,
    1003025757456584737,
    1003025759008456839,
    1003025759897669763,
    1003025760753303682,
    1003025761738965083,
    1003025762842071161,
    1003025764138090607,
    1003025765199253625,
    1003025766092652554,
    1003025766801494017,
    1003026537571954708,
    1003025768424685568,
    1003025769376792626,
    1003058439196520458,
    1003058520746381382,
]

DEFENSE_ROLES = [
    1004167439879258192,  # In the Jar
    1004167279338061844,  # Target Locked
    1004168808916861001  # House Arrest
]


async def log_mod_powers(bot, command, channel, user, targets=[]):
    target_list = None
    if len(targets):
        target_list = ', '.join(targets)
    else:
        target_list = "No targets specified."

    embed = discord.Embed(title=f"{user.display_name} used {command} in {channel}.",
                          description=f"{target_list}", color=0x00ffff)

    if len(targets):
        for target in targets:
            embed.add_field(name="Target:", value=f"{str(target)}")

    embed.timestamp = datetime.datetime.now(pytz.timezone('Europe/Dublin'))

    if user.avatar != None:
        embed.set_thumbnail(url=user.avatar.url)

    embed.set_footer(text=f"ID: {user.id}")

    try:
        await bot.client.get_channel(CHANNELS["mod"]).send(embed=embed)
    except Exception as e:
        embed = discord.Embed(title=f"{user.display_name} used {command} in {channel}.",
                              description=f"{target_list}", color=0x00ffff)
        await bot.client.get_channel(CHANNELS["mod"]).send(embed=embed)


class RaidDefense(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.lockdown = False
        self.target_list = []


    @commands.Cog.listener()
    async def on_member_join(self, member):
        config = load_json_config("config.json")
        if self.lockdown == True:
            await member.add_roles(1004168808916861001)
            await member.add_roles(1004167279338061844)
            await member.send(f"```Hi {member.display_name}, this is Middle Ground Security system. \n\nMG Lockdown has been Triggered: You have joined the server during a security event and have been moved to a secure/restricted role until the security concern has been resolved. Please reach out to ga??j??#9046 if you have any concerns - this shouldn't take very long.\n\nThis happens when the server is under threat from bad actors and we need to stop inbound members from flooding.\n\nI appreciate your patience while we resolve this, the quarantine is for your protection and to prevent them harvesting our member's list or harassing members.```")

    """
        Admin Commands.
    """
    @commands.slash_command(name='houseparty', description="Say, J.A.R.V.I.S., is it that time?")
    @commands.has_role('Wielder of the flame of Anor')
    async def houseparty(self, ctx):
        await log_mod_powers(self, "houseparty", ctx.channel, ctx.author)
        for member in ctx.guild.members:
            if ctx.guild.get_role(1004167439879258192) in member.roles:
                await member.send('You have been banned from MG.')
                await ctx.guild.ban(member, delete_message_days=7)
        await ctx.message.delete()

    @commands.slash_command(name='execute', description="Ban the list of targeted users.")
    @commands.has_role('Wielder of the flame of Anor')
    async def execute(self, ctx):
        await log_mod_powers(self, "execute", ctx.channel, ctx.author)
        targets = 0
        for member in ctx.guild.members:
            if ctx.guild.get_role(1004167279338061844) in member.roles:
                targets += 1
                #await ctx.guild.ban(member, reason="Banned by Raid Defense", delete_message_days = 1)
                await ctx.send_response(f"```Target {targets} neutralized...tracking next target...```", delete_after=10)
        await ctx.send_response(f"```{targets} targets neutralized...standing by...```", delete_after=10)

        self.target_list = []
        await ctx.message.delete()

    @commands.slash_command(name='deputize', description="Grant someone the role of Deputy.")
    @commands.has_role('Admin')
    async def deputize(self, ctx, *, member: discord.Member):
        await log_mod_powers(self, "deputize", ctx.channel, ctx.author, str(member))
        await ctx.send_response(f"```Deputizing {member.display_name}...```", delete_after=10)
        await member.add_roles(ctx.guild.get_role(853286399896453140))
        await member.send("You have been Deputized as an MG Mod to deal with varmints! Please delete spam, and use the RaidDefense system to defend the motherland!")
        await ctx.message.delete()

    @commands.slash_command(name='abrogate', description="Revoke from all deputys: the role of Wielder of the flame of Anor!")
    @commands.has_role('Admin')
    async def abrogate(self, ctx, member: discord.Member = None):
        await log_mod_powers(self, "abrogate", ctx.channel, ctx.author)
        await ctx.send_response("```Abrogating deputies now...```", delete_after=5)
        if member is None:
            for member in ctx.guild.members:
                if str(member.id) not in  ["218521566412013568", "1003196739517427806"]:
                    if ctx.guild.get_role(853286399896453140) in member.roles:
                        await ctx.send_followup(f"```{member.display_name} abrogated...```")
                        await member.remove_roles(ctx.guild.get_role(853286399896453140))
                        await member.send("Thank you for your service as an MG Wielder of the flame of Anor! The threats have abated for now and if your services are needed in future you will be called on to serve the community.")
        else:
            if ctx.guild.get_role(853286399896453140) in member.roles:
                await ctx.send_followup(f"```{member.display_name} abrogated...```")
                await member.remove_roles(ctx.guild.get_role(853286399896453140))
                await member.send("Thank you for your service as an MG Wielder of the flame of Anor! The threats have abated for now and if your services are needed in future you will be called on to serve the community.")

        await ctx.send_followup("```Abrogation complete.```", delete_after=5)
        await ctx.message.delete()
        
    """
        `Wielder of the flame of Anor` commands.
    """
    @commands.slash_command(name='analyze', description="Run /userinfo for each targeted user.")
    @commands.has_role('Wielder of the flame of Anor')
    async def analyze(self, ctx):
        await log_mod_powers(self, "analyze", ctx.channel, ctx.author)
        for member in ctx.guild.members:
            if ctx.guild.get_role(1004167279338061844) in member.roles:
                await ctx.send_response(f"```Scanning bogey: {str(member)}```", delete_after=5)
                try:
                    await ctx.invoke(self.client.get_command('userinfo'), member)
                except Exception as e:
                    clogger(f"Error: {e}")
                    pass
                time.sleep(1)
        await ctx.message.delete()

    @commands.slash_command(name='lockdown', description="Extreme measure! Lock the server down to prevent any posting or activity to permit cleanup.")
    @commands.has_role('Admin')
    async def lockdown(self, ctx):
        """
        Lockdown the server for a set amount of time.

        :param ctx: context of the message
        :param time: amount of minutes to lockdown the server
        """
        await log_mod_powers(self, "lockdown", ctx.channel, ctx.author)

        # Set the lockdown flag to true and set the lockdown time to now + the specified time
        self.lockdown = True

        # Get all channels and roles on the server
        channels = ctx.guild.channels

        # Create a dictionary of permissions that will be applied to all channels
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        overwrite.read_messages = False


        for channel in ctx.guild.channels:
            if "totw" not in channel.name:
                await channel.set_permissions(role, overwrite=overwrite)

        for member in ctx.guild.members:
            if ctx.guild.get_role(1004167279338061844) in member.roles:
                clogger(f"Moving {str(member)} to 'House Arrest'...")
                # add 'house arrest' role to all targets
                target_role = ctx.guild.get_role(1004167279338061844)
                house_arrest = ctx.guild.get_role(1004168808916861001)
                await member.remove_roles(target_role)
                await member.add_roles(house_arrest)
                # remove 'target locked' role to all targets
                clogger("...target relocation complete...")
                self.target_list.remove(member)

        arrest_role = discord.utils.get(ctx.guild.roles, name='House Arrest')
        # Loop through all channels and set the permissions for the limited role to the permissions dictionary
        for channel in channels:
            if "totw" not in channel.name:
                if channel.type in [discord.ChannelType.category]:
                    await channel.set_permissions(arrest_role, overwrite=overwrite)

        for member in arrest_role.members:
            clogger(f"Member: {str(member)} locked down...")
            await member.send(f"```Hi {member.display_name}, this is Middle Ground Security system. \n\nMG Lockdown has been Triggered: You have been moved to a secure/restricted role until the security concern has been resolved. Please reach out to ga??j??#9046 if you have any concerns - this shouldn't take very long.\n\nThis happens when the server is under threat from bad actors and we need to stop inbound members from flooding.```")

        await ctx.send_response('```Lockdown protocol engaged...all channels locked and members notified...```', delete_after=5)
        await ctx.message.delete()

    @commands.slash_command(name='unlock', description="Unlock the server and release all locked down users.")
    @commands.has_role('Admin')
    async def unlock(self, ctx):
        """
        Unlock the server by setting the lockdown flag to false and setting the lockdown time to None

        :param ctx: context of the message
        """
        await log_mod_powers(self, "unlock", ctx.channel, ctx.author)
        self.lockdown = False

        channels = ctx.guild.channels
        role = discord.utils.get(ctx.guild.roles, name='House Arrest')

        for channel in channels:
            if "totw" not in channel.name:
                if channel.type in [discord.ChannelType.category]:
                    await channel.set_permissions(role, overwrite=None)

        for member in role.members:
            await member.send(f"```Hi {member.display_name}, this is Middle Ground Security system. \n\nMG Lockdown has been lifted. We appreicate your patience and apologize for the inconvienience! Let us know if you have any questions or concerns! @Staff```")
            # remove 'house arrest' role to all targets
            await member.remove_roles(1004168808916861001)

        await ctx.send_response('```Lockdown lifted...```', delete_after=5)
        await ctx.message.delete()

    @commands.slash_command(name='lockstatus', description="Check the lockdown status of the server.")
    @commands.has_role('Wielder of the flame of Anor')
    async def lockstatus(self, ctx):
        """
        Check the status of the lockdown and send a message to the channel with the status.

        :param ctx: context of the message
        """
        if self.lockdown:
            await ctx.send_response(f'```MG is in lockdown.```', delete_after=10)
        else:
            await ctx.send_response('```MG is not in lockdown.```', delete_after=10)
        await ctx.message.delete()

    @commands.slash_command(name='target', description="Target the specified user(s). Select users by @mentioning them.")
    @commands.has_role('Wielder of the flame of Anor')
    async def target(self, ctx):
        await log_mod_powers(self, "target", ctx.channel, ctx.author, ','.join([u.display_name for u in ctx.message.mentions]))
        for member in ctx.message.mentions:
            if member.id not in [218521566412013568,820070084009000960]:
                clogger(f"Targeted Member: {str(member)}: {type(member)}")
                await member.add_roles(ctx.guild.get_role(1004167279338061844))
                await ctx.send_response(f"```Target: {str(member)} scanned and locked.```", delete_after=10)
                await ctx.send_response(f"```Preparing countermeasures...```", delete_after=10)
                self.target_list.append(member)

        await ctx.message.delete()

    @commands.slash_command(name='arrest', description="Jar the targets, removing them from gen-pop.")
    @commands.has_role('Wielder of the flame of Anor')
    async def arrest(self, ctx):
        await log_mod_powers(self, "arrest", ctx.channel, ctx.author)
        for member in ctx.guild.members:
            if ctx.guild.get_role(1004167279338061844) in member.roles:
                await member.add_roles(ctx.guild.get_role(1004167439879258192))
                await member.remove_roles(ctx.guild.get_role(1004167279338061844))
                await ctx.send_response_response(f"```Target in the jar: {member.display_name}, has been engaged and contained...```", delete_after=10)
                self.target_list = []
        await ctx.message.delete()

    @commands.slash_command(name='turnloose', description="Release user from the jar and/or untarget them. Intentionally single user only.")
    @commands.has_role('Wielder of the flame of Anor')
    async def turnloose(self, ctx, *, user: discord.Member):
        await log_mod_powers(self, "deputize", ctx.channel, ctx.author, ','.join([u.display_name for u in ctx.message.mentions]))
        if isinstance(members, list):
            for member in ctx.guild.members:
                if ctx.guild.get_role(1004167439879258192) in member.roles:
                    await member.remove_roles(ctx.guild.get_role(1004167439879258192))
                    await ctx.send_response(f"```Target {str(member)} unjarred - standing by...```", delete_after=10)
                if ctx.guild.get_role(1004167279338061844) in member.roles:
                    await member.remove_roles(ctx.guild.get_role(1004167279338061844))
                    self.target_list.remove(member)
                    await ctx.send_response(f"```Target {str(member)} unlocked - standing by...```", delete_after=10)
        else:
            member = members
            if ctx.guild.get_role(1004167439879258192) in member.roles:
                await member.remove_roles(ctx.guild.get_role(1004167439879258192))
            if ctx.guild.get_role(1004167279338061844) in member.roles:
                await member.remove_roles(ctx.guild.get_role(1004167279338061844))
                self.target_list.remove(member)

            await ctx.send_response(f"```Target {str(member)} cleared - standing by...```", delete_after=10)
        await ctx.message.delete()

    @commands.slash_command(name='targetlist', description="Show a list of bogeys on the wire.")
    @commands.has_role('Wielder of the flame of Anor')
    async def targetlist(self, ctx):
        targets = []
        await log_mod_powers(self, "targetlist", ctx.channel, ctx.author)
        for member in ctx.guild.members:
            if ctx.guild.get_role(1004167279338061844) in member.roles:
                targets.append(member)

        await ctx.send_response_response(f"```Current Targets ({len(targets)})\n--------------------\n\n{(',').join([str(m) for m in targets])}```", delete_after=20)
        await ctx.message.delete()

    def save_userperms(self):
        with open('userperms.json', 'w') as f:
            json.dump(self.userperms, f)

    def load_userperms(self):
        if os.path.exists('userperms.json'):
            with open('userperms.json', 'r') as f:
                self.userperms = json.load(f)

    def load_roles(self):
        if os.path.exists('roles.json'):
            with open('roles.json', 'r') as f:
                self.roles = json.load(f)

    @commands.Cog.listener()
    async def on_ready(self):
        self.load_roles()
        self.load_userperms()


def setup(client):
    client.add_cog(RaidDefense(client))