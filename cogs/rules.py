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


class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id == 1002591595792699412:
            guild = self.bot.get_guild(payload.guild_id)
            role = discord.utils.get(guild.roles, name='Member')
            if payload.emoji.name == '✅':
                member = discord.utils.get(guild.members, id=payload.user_id)
                await member.add_roles(role)
                #clogger(f'{member} has accepted the rules.')
                embed = discord.Embed(title=f"{member.display_name} just joined!",
                                      description=f"<@&1002977037314687056> we have a new member! Please welcome {member.mention} to MG!\n\n```Click the thumbs up react to dismiss this message, {member.display_name} :)```", color=discord.Color.green())
                if member.avatar is not None:
                    embed.set_thumbnail(url=member.avatar.url)
                
                joined = datetime.datetime.now(pytz.timezone('Europe/Dublin')).strftime("%d/%m/%Y @ %H: %M: %S")
                embed.set_footer(
                    text=f"User Joined | {joined}")

                # send and wait for react.
                msg = await guild.get_channel(820097812506869780).send(embed=embed)
                await msg.add_reaction("\U0001f44d")

                # wait for reaction.
                def check(reaction, user):
                    return user == member and str(reaction.emoji) == "\U0001f44d"

                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=180.0, check=check)
                except asyncio.TimeoutError:
                    try:
                        await msg.delete()
                    except:
                        pass # User deleted the message or it timed out.
                else:
                    await msg.delete()

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.message_id == 1002591595792699412:
            guild = self.bot.get_guild(payload.guild_id)
            role = discord.utils.get(guild.roles, name='Member')
            if payload.emoji.name == '✅':
                member = discord.utils.get(guild.members, id=payload.user_id)
                if member != None:
                    await member.remove_roles(role)
                #clogger(f'{member} has removed the rules.')

def setup(bot):
    bot.add_cog(Rules(bot))
