import asyncio
import datetime
import discord
from discord.ext import commands
import sys
import os
import pytz

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '.')))

from clogger import clogger
from utils import *

class QuotaManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="quota", help="Check your BOT quota.")
    async def quota(self, ctx):
        """Get info about a user"""
        user = ctx.author
        quotas = load_json_config("quotas.json")

        for q in quota:
            if str(user.id) not in quotas[q]:
                quotas[q][str(user.id)] = QUOTA_LIMIT

        embed = discord.Embed(title=f"{user.display_name}'s Bot usage quota remaining...",
                              description=f"Bot quota is currently {QUOTA_LIMIT} per day. It refreshes at 00:05 GMT+1.", color=0x00ff00)

        for q in quotas:
            if str(user.id) not in quotas[q]:
                quotas[q][str(user.id)] = QUOTA_LIMIT
            embed.add_field(name=f"{q}",
                            value=f"```{quotas[q][str(user.id)]}```", inline=True)

        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.message.delete(reason="Command usage cleanup.")
        await ctx.send(embed=embed, delete_after=30)

    @commands.command(name='addquota', help='Check your bot quota.')
    async def addquota(self, ctx, value=0, bot=None):
        quotas = load_json_config("quotas.json")
        if bot == None:
            for q in quotas:
                for member in ctx.guild.members:
                    # False if member has left the server or has not had any reaction logged yet
                    if member == None:
                        continue
                quotas[q][str(member.id)] += value
        else:
            for member in ctx.guild.members:
                # False if member has left the server or has not had any reaction logged yet
                if member == None:
                    continue
                quotas[bot][str(member.id)] += value

        write_json_config("quotas.json", quotas)

    @commands.command(name='resetquotas', help='Reset AI bot quotas for all members. Optional: specify bot.')
    @commands.has_role('Admin')
    async def resetquotas(self, ctx, bot=None):
        quotas = load_json_config("quotas.json")
        if bot == None:
            for q in quotas:
                for member in ctx.guild.members:
                    # False if member has left the server or has not had any reaction logged yet
                    if member == None:
                        continue
                quotas[q][str(member.id)] = QUOTA_LIMIT
        else:
            for member in ctx.guild.members:
                # False if member has left the server or has not had any reaction logged yet
                if member == None:
                    continue
                quotas[bot][str(member.id)] = QUOTA_LIMIT

        write_json_config("quotas.json", quotas)


def setup(bot):
    bot.add_cog(QuotaManager(bot))
