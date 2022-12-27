import discord
import json
import asyncio
import datetime
import os
import requests
import sys
import pytz

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib
import pandas
from io import BytesIO
from PIL import Image

from discord.ext import commands, tasks
from paginator import Paginator, Page

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '.')))

from clogger import clogger
from utils import *

async def log_own_submission(message):

    ownlog = load_json_config("owns.json")

    if str(message.guild.id) not in ownlog:
        ownlog[str(message.guild.id)] = []
        ownlog[str(message.guild.id)].append(message.id)
    else:
        if is_already_owned(ownlog, message):
            await message.channel.send("```This user has already been owned.```")
            return
        else:
            ownlog[str(message.guild.id)].append(message.id)

    write_json_config("owns.json", ownlog)

async def trulyowned(original_message, guild_id):
    trulyowned = load_json_config("trulyowned.json")
    if str(guild_id) not in trulyowned:
        trulyowned[str(guild_id)] = []
        trulyowned[str(guild_id)].append(original_message.id)
    else:
        if original_message.id not in trulyowned[str(guild_id)]:
            trulyowned[str(guild_id)].append(original_message.id)
        else:
            await original_message.channel.send("```This own has already been truly owned.```")
            return

    write_json_config("trulyowned.json", trulyowned)


async def add_member_to_ownzone(member):
    ownzone = load_json_config("ownzone.json")

    if not str(member.id) in ownzone:
        ownzone[str(member.id)] = {
            "has_owned": 0,
            "been_owned": 0,
            "last_owner": None,
            "last_owned": None,
            "last_owned_timestamp": None,
            "has_owned_log": [],
            "been_owned_log": []
        }

        write_json_config("ownzone.json", ownzone)

    return


def is_already_owned(ownlog, message):
    if message.id in ownlog[str(message.guild.id)]:
        return True
    else:
        return False


async def increment_owning(owner, target, message):
    ownzone = load_json_config("ownzone.json")

    ownzone[str(owner.id)]["has_owned"] += 1
    ownzone[str(target.id)]["been_owned"] += 1
    ownzone[str(target.id)]["last_owned"] = owner.id
    ownzone[str(target.id)]["last_owned_timestamp"] = datetime.datetime.now(
        pytz.timezone("Europe/Dublin")).strftime("%d/%m/%Y %H:%M:%s")

    attachments = []
    embeds = []

    for attachment in message.attachments:
        attachments.append(attachment.url)

    for embed in message.embeds:
        embeds.append(embed.image.url)

    owned_entry = [owner.id, target.id, message.channel.id, message.clean_content,
                   message.created_at.strftime("%d/%m/%Y %H:%M:%s"), attachments, embeds]

    clogger("owned: " + str(owned_entry))

    ownzone[str(owner.id)]["has_owned_log"] = owned_entry
    ownzone[str(target.id)]["been_owned_log"] = owned_entry

    write_json_config("ownzone.json", ownzone)


class Ownalytics(commands.Cog):

    def __init__(self, client):
        self.client = client
        # Check if the task loop is already running
        self.config = load_json_config('config.json')
        self.paginator = Paginator(self.client)

    @commands.Cog.listener()
    async def on_ready(self):
        # Iterate through all members and add them to the ownzone log if they're not in it already.
        m_count = 0
        for guild in self.client.guilds:
            for member in guild.members:
                await add_member_to_ownzone(member)
                m_count += 1

        clogger(f"All members {m_count} added to the ownzone...")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await add_member_to_ownzone(member)

    # Handle on react with :owned: custom emoji should post an embed to the channel named: 📥the-own-box

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.client.user.id:
            return

        if payload.emoji.name == "owned":
            message = await self.client.get_channel(payload.channel_id).fetch_message(payload.message_id)

            is_reply = False
            original_message = False
            if message.reference:
                if message.reference.channel_id == message.channel.id and message.reference.message_id != None:
                    previous_message = await message.channel.fetch_message(message.reference.message_id)
                    if previous_message.id is not None:
                        is_reply = True

            if is_reply:
                
                log_own_submission(message)

                embed = discord.Embed(title=f"[Own Zone Report] ID: {message.id}", description=f"{previous_message.author.mention} has been owned by {message.author.mention}...", timestamp=datetime.datetime.now(
                    pytz.timezone("Europe/Dublin")), color=discord.Colour.blurple())
                embed.set_author(name="The Own Box",
                                 icon_url=self.client.user.avatar.url)
                embed.add_field(
                    name="Owner:", value=f"{message.author.mention}")
                embed.add_field(
                    name="Target:", value=f"{previous_message.author.mention}")
                embed.add_field(name="The Own:",
                                value=f"{message.clean_content}")
                
                if len(previous_message.clean_content) > 0:
                    own_reason = previous_message.clean_content
                else:
                    own_reason = '\u200b'

                if len(previous_message.attachments):
                    embed.set_image(url=previous_message.attachments[0].url)

                if len(previous_message.embeds):
                    embed.set_image(url=previous_message.embeds[0].image.url)

                if len(own_reason) > 999:
                    # add a field for for every 999 characters in 'own_reason'.
                    embed.add_field(name=f"...because {previous_message.author.display_name} said wayyyy to much:",
                                        value=f"{own_reason[0:999]}")
                    for i in range(1000, len(own_reason), 999):
                        embed.add_field(name=f"...and then you said...:",
                                        value=f"{own_reason[i:i+999]}")
                else:
                    embed.add_field(name=f"...because {previous_message.author.display_name} said:", value=f"{own_reason}")

                embeds = [embed]

                if message is not None:
                    for attachment in message.attachments:
                        embeds[0].set_image(url=attachment[5][0])

                    for embed in message.embeds:
                        if 'image' in dir(embed):
                            embeds[0].set_image(url=embed['image']['url'])

                # Send the embed to the channel named: 📥the-own-box
                channel = discord.utils.get(self.client.get_guild(
                    payload.guild_id).text_channels, name="📥the-own-box")
                # Send the embed to the channel
                ownbox_post = await channel.send(embed=embeds[0])
                wheeze_emoji = discord.utils.get(self.client.get_guild(
                    payload.guild_id).emojis, name="wheeze")
                await ownbox_post.add_reaction(wheeze_emoji)
                await ownbox_post.add_reaction("❌")

            else:

                # Remove the reaction and send a message in the channel to tell the user only replys can be flagged as owns and delete after 10s.
                channel = self.client.get_channel(payload.channel_id)
                react_message = await channel.fetch_message(payload.message_id)
                await react_message.remove_reaction(payload.emoji, self.client.get_guild(payload.guild_id).get_member(payload.user_id))
                await self.client.get_channel(payload.channel_id).send("```Only replies can be flagged as owns.```", delete_after=10)

        
        if payload.emoji.name == "wheeze" and int(payload.channel_id) == 1057029272298061865:
            
            if not discord.utils.get(self.client.get_guild(payload.guild_id).roles, name="Chief Executive Owner") in self.client.get_guild(payload.guild_id).get_member(payload.user_id).roles:
                return

            message = await self.client.get_channel(payload.channel_id).fetch_message(payload.message_id)
            embed = message.embeds[0]
            original_message_id = int(embed.title.split(" ")[-1])

            original_message = await self.client.get_channel(payload.channel_id).fetch_message(original_message_id)

            await increment_owning(original_message.author, original_message.reference.author, original_message)

            channel = discord.utils.get(self.client.get_guild(
                payload.guild_id).text_channels, name="🍆ownzone")
            
            # Send the embed to the channel
            await channel.send(embed=embed)
            embed.title = f"[Truly Owned] {embed.title}"
            embed.colour = discord.Colour.green()
            trulyowned(original_message, original_message.guild.id)

        if payload.emoji.name == "❌" and int(payload.channel_id) == 1057029272298061865:
            # Colour the embed red and rename title to [Rejected] prefix keeping the rest of the title.
            message = await self.client.get_channel(payload.channel_id).fetch_message(payload.message_id)
            embed = message.embeds[0]
            embed.title = f"[Rejected] {embed.title}"
            embed.colour = discord.Colour.red()
            await message.edit(embed=embed)

    @discord.commands.slash_command(name='generateownzone', description='Generates an Ownzone graph.')
    @commands.has_any_role('Staff', 'Chief Executive Owner')
    async def generateownzone(self, ctx):
        await ctx.send_response(f"```Generating an own zone chart...```", delete_after=5)
        ownzone = load_json_config("ownzone.json")
        ownzone_graph_data = {}

        for user in ownzone:
            ownzone_graph_data[user] = {
                "has_owned": ownzone[user]["has_owned"],
                "been_owned": ownzone[user]["been_owned"],
                "ability_to_own": 0,
                "difficulty_to_own": 0
            }

        for user in ownzone_graph_data:
            try:
                ownzone_graph_data[user]["ability_to_own"] = ownzone_graph_data[user]["has_owned"] / (
                    ownzone_graph_data[user]["has_owned"] + ownzone_graph_data[user]["been_owned"])
            except ZeroDivisionError as e:
                ownzone_graph_data[user]["ability_to_own"] = 0.0

            try:
                ownzone_graph_data[user]["difficulty_to_own"] = ownzone_graph_data[user]["been_owned"] / (
                    ownzone_graph_data[user]["has_owned"] + ownzone_graph_data[user]["been_owned"])
            except ZeroDivisionError as e:
                ownzone_graph_data[user]["difficulty_to_own"] = 0.0

        ownzone_graph_data_df = pandas.DataFrame.from_dict(
            ownzone_graph_data, orient='index')
        ownzone_graph_data_df.reset_index(inplace=True)
        ownzone_graph_data_df.rename(
            columns={'index': 'user_id'}, inplace=True)

        ownzone_graph_data_df['user_id'] = ownzone_graph_data_df['user_id'].astype(
            int)
        ownzone_graph_data_df['has_owned'] = ownzone_graph_data_df['has_owned'].astype(
            int)
        ownzone_graph_data_df['been_owned'] = ownzone_graph_data_df['been_owned'].astype(
            float)
        ownzone_graph_data_df['ability_to_own'] = ownzone_graph_data_df['ability_to_own'].astype(
            float)
        ownzone_graph_data_df['difficulty_to_own'] = ownzone_graph_data_df['difficulty_to_own'].astype(
            float)

        ownzone_graph_data_df['user_id'] = ownzone_graph_data_df['user_id'].astype(
            str)

        ownzone_graph_data_df['user_id'] = ownzone_graph_data_df['user_id'].apply(
            lambda x: self.client.get_user(int(x)).display_name)

        ownzone_graph_data_df.sort_values(by=['ability_to_own'], inplace=True)

        ownzone_graph_data_df.reset_index(inplace=True)
        ownzone_graph_data_df.drop(columns=['index'], inplace=True)

        ownzone_graph_data_df.set_index('user_id', inplace=True)

        # Plot each user on an Pournelle chart that ranges from -1 through 0 at the origin to 1 on both X and Y axis. Label each data point with the user's display name and use their avatar for the data point image.
        fig, ax = plt.subplots()
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.set_xlabel('Ability to Own')
        ax.xaxis.set_label_coords(0.5, -0.09)
        ax.set_ylabel('Difficulty to Own')
        ax.yaxis.set_label_coords(-0.09, 0.5)
        ax.spines['left'].set_position('center')
        ax.spines['bottom'].set_position('center')

        # Eliminate upper and right axes
        ax.spines['right'].set_color('none')
        ax.spines['top'].set_color('none')

        # Show ticks in the left and lower axes only
        ax.xaxis.set_ticks_position('none')
        ax.yaxis.set_ticks_position('none')
        ax.set_yticklabels([])
        ax.set_xticklabels([])

        status = await ctx.send_followup("```Mathology has been manifested; acquiring pfps...```")

        for i in range(len(ownzone_graph_data_df)):
            try:
                user_display_name = ownzone_graph_data_df.index[i]
                # get users based on display name, use the discord utils get to look up the user.
                user = discord.utils.get(
                    self.client.users, name=user_display_name)
                # get the avatar url for the user
                try:
                    avatar_url = user.avatar.url.replace(
                        "size=1024", "size=100").replace("gif", "png")
                except:
                    random_default = [
                        "https://ia903204.us.archive.org/4/items/discordprofilepictures/discordred.png",
                        "https://ia903204.us.archive.org/4/items/discordprofilepictures/discordgrey.png",
                        "https://ia903204.us.archive.org/4/items/discordprofilepictures/discordgreen.png",
                        "https://ia903204.us.archive.org/4/items/discordprofilepictures/discordblue.png",
                    ]
                    avatar_url = random.choice(random_default)

                # get the ability to own and difficulty to own for the user
                ability_to_own = ownzone_graph_data_df.iloc[i]['ability_to_own']
                difficulty_to_own = ownzone_graph_data_df.iloc[i]['difficulty_to_own']
                # plot the user's avatar image at the ability to own and difficulty to own coordinates. Use requests.get() with a good user-agent to download the image to a temp file and load it to plt.imread().
                response = requests.get(avatar_url, headers={
                                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'})
                # use the response as the image.
                img = Image.open(BytesIO(response.content))
                img = img.resize((100, 100), Image.ANTIALIAS)
                with open('temp.png', 'wb') as f:
                    img.save(f)
                # Plot the image to the graph.
                img = plt.imread('temp.png')
                imagebox = OffsetImage(img, zoom=0.1)
                imagebox.image.axes = ax
                await status.edit(f"```Getting {user_display_name}'s pfp...```")
                ab = AnnotationBbox(
                    imagebox, (ability_to_own, difficulty_to_own), frameon=False)
                ax.add_artist(ab)
                # label the user's display name at the ability to own and difficulty to own coordinates
                ax.annotate(user_display_name, (ability_to_own,
                                                difficulty_to_own - 0.10), fontsize=5, ha='center', va='bottom')

            except (AttributeError, SyntaxError) as e:
                clogger(
                    f"```Skipping {user_display_name} - avatar: {user.avatar}...```")
                clogger(e)
                continue

        await status.edit(f"```Ownzone calculated and rendered...```")
        ax.annotate("Hardest to Own", (0.02, 0.95), fontsize=8)
        ax.annotate("Easiest to Own", (0.02, -1.0), fontsize=8)
        ax.annotate("Owns the hardest", (0.60, 0.02), fontsize=8)
        ax.annotate("Owns the weakest", (-1.0, 0.02), fontsize=8)

        # save the plot to a file

        plt.savefig('ownzone.png')
        # send the plot to the channel as a stylish embed.
        today = datetime.datetime.now(pytz.timezone(
            "Europe/Dublin")).strftime("%d/%m/%Y %H:%M:%S")
        embed = discord.Embed(
            title=f"Own'th Zone'th - ({today})", description="The Own'th Zone'th decides the standing of all...own or be owned. There is no middle ground here.", color=discord.Colour.blurple())
        embed.set_image(url="attachment://ownzone.png")
        await ctx.send(file=discord.File('ownzone.png'), embed=embed)
        await status.delete()

        os.remove('temp.png')
        os.remove('ownzone.png')

    @discord.commands.slash_command(name='addown', description='Adds an own to the ownzone.')
    @commands.has_any_role('Staff', 'Chief Executive Owner')
    async def addown(self, ctx, owner: discord.Member, target: discord.Member, message_id: discord.Option(str, "The ID of the Own message."), op_message_id: discord.Option(str, "The ID of the message belonging to the target of the Own.")):
        await ctx.send_response(f"```Manual owning in progress...```", delete_after=5)
        embed = discord.Embed(title=f"[Own Zone Report] ID: {message_id}", description=f"{target.mention} has been owned by {owner.mention}...", timestamp=datetime.datetime.now(
            pytz.timezone("Europe/Dublin")), color=discord.Colour.blurple())
        embed.set_author(name="The Own Box",
                         icon_url=self.client.user.avatar.url)
        embed.add_field(name="Owner:", value=f"{owner.mention}")
        embed.add_field(name="Target:", value=f"{target.mention}")

        op_message = await ctx.channel.fetch_message(int(op_message_id))
        owner_message = await ctx.channel.fetch_message(int(message_id))
        
        log_own_submission(owner_message)

        if len(op_message.clean_content) > 0:
            own_reason = op_message.clean_content
        else:
            own_reason = '\u200b'

        if len(op_message.attachments):
            embed.set_image(url=op_message.attachments[0].url)

        if len(op_message.embeds):
            embed.set_image(url=op_message.embeds[0].image.url)
        
        if len(own_reason) > 999:
            # add a field for for every 999 characters in 'own_reason'.
            embed.add_field(name=f"...because {op_message.author.display_name} said wayyyy to much:",
                                value=f"{own_reason[0:999]}", inline=True)
            for i in range(1000, len(own_reason), 999):
                embed.add_field(name=f"...and then you said...:",
                                value=f"{own_reason[i:i+999]}", inline=True)
        else:
            embed.add_field(name=f"...because {op_message.author.display_name} said wayyyy to much:", value=f"{own_reason}")


        # Send the embed to the channel named: 📥the-own-box
        channel = self.client.get_channel(1057029272298061865)
        # Send the embed to the channel
        ownbox_post = await channel.send(embed=embed)        
        wheeze_emoji = discord.utils.get(self.client.get_guild(
            ctx.guild.id).emojis, name="wheeze")
        await ownbox_post.add_reaction(wheeze_emoji)
        await ownbox_post.add_reaction("❌")
        await ctx.send_response(f"```Manual owning completed...```", delete_after=5)

    @discord.commands.slash_command(name='editown', description='Edits an own in the ownzone.')
    @commands.has_any_role('Staff', 'Chief Executive Owner')
    async def editown(self, ctx, user: discord.Member, has_owned: int = 0, been_owned: int = 0):
        ownzone = load_json_config("ownzone.json")
        status = await ctx.send_response(f"```Manually augmenting ownzone logs...```")

        if str(user.id) not in ownzone:
            await ctx.send_response(f"```{user.display_name} is not in the ownzone...```", delete_after=5)
            return

        # add the has_owned and been_owned values to the log.
        old_has_owned = ownzone[str(user.id)]["has_owned"]
        old_been_owned = ownzone[str(user.id)]["been_owned"]
        ownzone[str(user.id)]["has_owned"] += has_owned
        ownzone[str(user.id)]["been_owned"] += been_owned

        write_json_config("ownzone.json", ownzone)
        # Respond showing the delta with an embed. If there was any change to either metric add a field showing the before and after.
        embed = discord.Embed(title=f"{user.display_name}'s Ownzone", description=f"{user.mention} has been edited in the ownzone...",
                              timestamp=datetime.datetime.now(pytz.timezone("Europe/Dublin")), color=discord.Colour.blurple())
        embed.set_author(name="The Own Box",
                         icon_url=self.client.user.avatar.url)
        embed.set_thumbnail(url=user.avatar.url)

        if has_owned != 0:
            embed.add_field(
                name="Has Owned:", value=f"{old_has_owned} -> {ownzone[str(user.id)]['has_owned']}")

        if been_owned != 0:
            embed.add_field(
                name="Been Owned:", value=f"{old_been_owned} -> {ownzone[str(user.id)]['been_owned']}")

        mod_log_channel = self.client.get_channel(1049832907079954492)
        await ctx.send(embed=embed, delete_after=5)
        await mod_log_channel.send(embed=embed)
        status = await ctx.edit(f"```Completed manually augmenting ownzone logs...```", delete_after=5)


def setup(client):
    client.add_cog(Ownalytics(client))