import datetime
import discord
import asyncio
from discord.ext import commands, tasks
import random
import json
import os
import re
import sys
import pytz
import timeago

from jarvis import QUOTA_LIMIT
from pprint import pprint

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '.')))

from clogger import clogger
from utils import *


class Userinfo(commands.Cog):

    def calculate_xp(self, message, author=None):
        multiplier = 0.04
        if hasattr(author, "roles"):
            if "Based" in [y.name for y in author.roles]:
                multiplier = 0.08

            if "Afflicted with Cringe" in [y.name for y in author.roles]:
                multiplier = 0.02

        return (len(message) / 5) * multiplier

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def userinfo(self, ctx, user: discord.Member = None):
        """Get info about a user"""
        if not user:
            user = ctx.author


        user_xp = load_json_config("user_xp.json")
        emoji_tracker = load_json_config("emoji_tracker.json")
        quotas = load_json_config("quotas.json")

        if not str(user.id) in user_xp:
            user_xp[str(user.id)] = {
                "current_role": "825644695472439306",
                "next_role": "826116442822410261",
                "xp": 0,
                "xp_to_next_level": 100,
            }

        if str(user.id) not in emoji_tracker:
            emoji_tracker[str(user.id)] = {}
            top_emojis = ["--", "--", "--"]
        else:
            user_emojis = emoji_tracker[str(user.id)]
            sorted_user_emojis = sorted(
                user_emojis.items(), key=lambda x: x[1], reverse=True)
            filtered_emojis_list = ["\u2b50", "<:based:1002002396605599784>",
                                    "<:cringe:1002002378691710986>", "<:storbaord:954547894533373972>"]
            filtered_emojis = [
                e for e in sorted_user_emojis if e[0] not in filtered_emojis_list]

            for i in range(3-len(filtered_emojis)):
                filtered_emojis.append("--")

            top_emojis = [x[0] for x in filtered_emojis[:3]]

        filtered_roles = ["Admin", "Bot", "Cool Kid", "Gamer", "RPG Nerd", "Artist", "Writer", "Coding",
                          "Mathologist", "History Buff", "Armchair Political Analyst", "Sports Fan", "Couch Potato"]

        embed = discord.Embed(title=f"{user.display_name} ({str(user)} - {user.id})",
                              description="", color=0x00ff00)

        embed.add_field(name="\u200b",
                        value=f"```markdown\n#Membership Timestamps```", inline=False)

        created_at = user.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC")
        embed.add_field(name="Account Timestamp", value=f"```{created_at}```")

        account_age = timeago.format(
            user.created_at, datetime.datetime.utcnow().replace(tzinfo=pytz.utc))
        embed.add_field(name="Joined Discord", value=f"```{account_age}```", inline=True)

        joined_at = user.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC")
        embed.add_field(name="Joined Timestamp", value=f"```{joined_at}```", inline=True)

        joined_age = timeago.format(
            user.joined_at, datetime.datetime.utcnow().replace(tzinfo=pytz.utc))
        embed.add_field(name="Joined",
                        value=f"```{joined_age}```", inline=True)

        role_list = [role.mention for role in user.roles if role !=
                     ctx.guild.default_role and role.name not in filtered_roles]

        embed.add_field(name="\u200b",
                        value=f"```markdown\n#XP & Top Emojis```", inline=False)

        embed.add_field(
            name="XP", value=f"```{round(user_xp[str(user.id)]['xp'])}```")

        embed.add_field(name="XP to next level",
                        value=f"```{round(user_xp[str(user.id)]['xp_to_next_level'])}```")

        embed.add_field(name="Top 3 Emojis",
                        value=f"{top_emojis[0]} {top_emojis[1]} {top_emojis[2]}")

        embed.add_field(name="\u200b",
                        value=f"```markdown\n#AI Bot Quotas```", inline=False)

        for q in quotas:
            if str(user.id) not in quotas[q]:
                quotas[q][str(user.id)] = QUOTA_LIMIT
            embed.add_field(name=f"{q}",
                            value=f"```{quotas[q][str(user.id)]}```", inline=True)

        if len(role_list):
            embed.add_field(name="Roles", value=', '.join(role_list), inline=False)

        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        write_json_config("user_xp.json", user_xp)
        await ctx.message.delete(reason="Command usage cleanup.")
        await ctx.send(embed=embed, delete_after=30)

    @commands.command()
    async def leaderboard(self, ctx):
        """Lists the top 10 users along with their current role and current XP"""

        user_xp_dict = load_json_config("user_xp.json")

        sorted_user_xp = sorted(user_xp_dict.items(),
                                key=lambda x: x[1]['xp'], reverse=True)

        pprint(sorted_user_xp)

        embed = discord.Embed(title="Leaderboard", color=0x00ff00)

        embed.add_field(
            name=f"\u200b", value=f"```Rank\tMember\t\t\tXP```", inline=False)

        # let's just do the top 10 for this exercise
        for i, (key, data) in enumerate(sorted_user_xp[0:10]):
            user = self.client.get_user(int(key))
            current_role = discord.utils.get(
                ctx.message.guild.roles, id=data['current_role'])
            if current_role != None:
                current_role = current_role.mention

            # uhh I know it's weird but handles the case where there are many more key-value pairs than guild members maybe? idk ¯\_(ツ)_/¯
            if user is not None:
                # for funsies add some emojis (done manually for obvious reasons) probably wouldn't do this in production though... meaningless waste of api hits ¯\_(ツ)_/¯
                emojis = {1: "🥇", 2: "🥈", 3: "🥉"}
                if i + 1 < 4:
                    emoji = emojis[i + 1]
                else:
                    emoji = "🏅"  # show no emoji if not in the top 3!

                embed.add_field(
                    name=f"\u200b", value=f"```{emoji} {i+1:<2} {user.display_name:<20}{round(data['xp']):>5}```", inline=False)

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        config = load_json_config("config.json")
        
        if message.guild is None:
            return

        if config["guilds"][str(message.guild.id)]["modules"]["userdata"] == False:
            return

        if message.author.bot == True:
            return

        user_xp = load_json_config("user_xp.json")

        if not str(message.author.id) in user_xp:
            user_xp[str(message.author.id)] = {
                "current_role": "825644695472439306",
                "next_role": "826116442822410261",
                "xp": 0,
                "xp_to_next_level": 100,
            }

        write_json_config("user_xp.json", user_xp)
        filtered_channels = [934122764510593044, 823656840701149194, ]
        if message.channel.id not in filtered_channels:
            await self._updateXP(message)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        config = load_json_config("config.json")
        emojiFreq = load_json_config("emoji_tracker.json")

        if config["guilds"][str(reaction.message.guild.id)]["modules"]["userdata"] == False:
            return

        if reaction.message.author.bot == True:
            return

        if not str(user.id) in emojiFreq:
            emojiFreq[str(user.id)] = {}

        if not str(reaction.emoji) in emojiFreq[str(user.id)]:

            emojiFreq[str(user.id)][str(reaction.emoji)] = 1
        else:
            emojiFreq[str(user.id)][str(reaction.emoji)] += 1

        write_json_config("emoji_tracker.json", emojiFreq)

    async def _updateXP(self, message):
        user_xp = load_json_config("user_xp.json")
        level_roles = load_json_config("roles.json")

        if not str(message.author.id) in user_xp:
            user_xp[str(message.author.id)] = {
                "current_role": "825644695472439306",
                "next_role": "826116442822410261",
                "xp": 0,
                "xp_to_next_level": 100,
            }

        user_xp[str(message.author.id)
                ]["xp"] += self.calculate_xp(message.clean_content, message.author)

        if user_xp[str(message.author.id)]["xp"] >= user_xp[str(message.author.id)]["xp_to_next_level"]:
            old_role = discord.utils.get(
                message.guild.roles, name=level_roles[str(user_xp[str(message.author.id)]["current_role"])])

            new_role = discord.utils.get(
                message.guild.roles, name=level_roles[str(user_xp[str(message.author.id)]["next_role"])])

            if new_role is None:
                return

            if str(old_role) not in ["Member"]:
                await message.author.remove_roles(old_role)
            await message.author.add_roles(new_role)

            role_list = [v for k, v in level_roles.items()]

            try:
                next_role = discord.utils.get(
                    message.guild.roles, name=role_list[role_list.index(str(new_role)) + 1])
            except:
                next_role = {"id": None}

            user_xp[str(message.author.id)]["current_role"] = new_role.id
            user_xp[str(message.author.id)]["next_role"] = next_role.id
            user_xp[str(message.author.id)]["xp_to_next_level"] *= 1.69
            channel = message.guild.get_channel(820097984024018944)

            level_up_embed = discord.Embed(
                title=f"{message.author.display_name} achieved the rank of: {new_role.name}", description="", color=0x00ff00)

            level_up_embed.add_field(
                name="Aquired in", value=message.channel.name, inline=True)
            level_up_embed.add_field(
                name="XP", value=f"{round(user_xp[str(message.author.id)]['xp'])}")
            level_up_embed.add_field(name="XP to next level",
                                     value=f"{user_xp[str(message.author.id)]['xp_to_next_level']}")

            level_up_embed.set_thumbnail(url=message.author.display_avatar.url)
            level_up_embed.set_footer(
                text=f"Grats {message.author}!", icon_url=message.author.display_avatar.url)

            await channel.send(embed=level_up_embed)

        write_json_config("user_xp.json", user_xp)


def setup(client):
    client.add_cog(Userinfo(client))
