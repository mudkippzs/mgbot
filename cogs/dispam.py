import asyncio
import datetime
import discord
import json
import sys
import os
import openai
import pytz
import requests

from discord.ext import commands

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '.')))

from clogger import clogger
from utils import *


def contains_invite(message):
    contains_invite_flag = False

    return contains_invite_flag



class Dispam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spam_log_data = load_json_config("spamlogs.json")
        config = load_json_config("config.json")
        self.api_key = config["ai_key"]    
        self.translate_api_key = config["translatekey"]       
        self.translation_confidence_level = 0.5

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.author.id in [218521566412013568]:
            return

        if message.clean_content.lower().startswith("jarvis"):
            return

        if message.clean_content.lower().startswith("emgee"):
            return

        if len(message.clean_content) < 8 and len(message.mentions) > 1:
            return
        
        #if self.is_english(message.clean_content) is False:
            #non_en_dm = await message.author.send("```English only - please refrain from  posting in non-English as it's considered spam. Ongoing spam will result in penalty.```")
            #await self.handle_spam(message, "Non-english posting.", False)
        #    clogger(f"Non-english text detected: {message.clean_content}")
        #else:
        #    clogger(f"English text detected: {message.clean_content}")

        if message.content.find("discord.gg") != -1:
            await self.handle_spam(message, "Discord invite link shared", True)


        
    def post_to_gpt3(self, payload, args=None):
        openai.api_key = self.api_key
        # formatted_payload = "\n".join(payload)
        if args == None:
            args = {
                'temp': 0.85,
                'max_tokens': 500,
                'top_p': 1.0,
                'fp': 0.02,
                'pp': 0.02,
            }
        return openai.Completion.create(
            model="text-davinci-003",
            prompt=payload,
            temperature=args['temp'],
            max_tokens=args['max_tokens'],
            top_p=args['top_p'],
            frequency_penalty=args['fp'],
            presence_penalty=args['pp']
        )

    def detect_language(self, text, api_key):
        """
        Detects the language of the given text.
        :param text: The text to detect the language of.
        :return: The language of the text.
        """
        url = "https://libretranslate.com/detect"
        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "q": text,
            "api_key": api_key
        }

        confidence = 0.00000001
        language = None

        try:
            response = requests.post(url, headers=headers, data=data, timeout=2).json()[0]
        except (requests.Timeout, KeyError):        
            language = None

        confidence = response["confidence"]
        language = response["language"]

        clogger(response)

        return language, confidence


    def is_english(self, string):
        language_detected, confidence = self.detect_language(string, self.translate_api_key)
        if 'en' == language_detected and confidence > self.translation_confidence_level:
            return True
        else:
            return False

    async def handle_spam(self, message, reason=None, hard=False):
        await message.channel.send(f"```English only please. Deleting non-English message by {message.author.display_name}.```", delete_after=10)
        await message.delete()
        if hard is True:
            self.spam_log_data = load_json_config("spamlogs.json")
            if str(message.author.id) not in self.spam_log_data:
                self.spam_log_data[str(message.author.id)] = {"spam_count": 1}
            else:
                self.spam_log_data[str(message.author.id)]["spam_count"] += 1

            if self.spam_log_data[str(message.author.id)]["spam_count"] >= 5:
                self.spam_log_data[str(message.author.id)]['spam_count'] = 0
                await message.author.timeout_for(datetime.timedelta(hours=24), reason=f"Timeout for {reason}.")
                embed = discord.Embed(title=f"{message.author.display_name} has been put in Timeout!", description=f"{message.author.mention} has been timed out for 24hrs for: {reason}. <@&1001210793204912341>", color=0x00ff00)
                if message.author.avatar != None:
                    embed.set_thumbnail(url=message.author.avatar.url)
                embed.set_footer(text="Dispam Spam Prevention")
                await self.bot.get_channel(828931953955831838).send(embed=embed)
                await message.author.send(f"```{message.author.mention} you have been timed out for: {reason}, this may result in a ban. You have been warned {self.spam_log_data[str(message.author.id)]['spam_count']} times.```")
            else:
                await message.author.send(f"```{message.author.mention} you have been warned for spamming. You have been warned {self.spam_log_data[str(message.author.id)]['spam_count']} times.```")
            
            write_json_config("spamlogs.json", self.spam_log_data)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.author.bot:
            return

        if after.author.id in [218521566412013568]:
            return

        message = after

        if message.clean_content.lower().startswith("jarvis"):
            return

        if message.clean_content.lower().startswith("emgee"):
            return

        # if len(message.clean_content) > 8 and len(message.mentions) < 1:
        #     if self.is_english(message.clean_content) is False:
        #         #non_en_dm = await message.author.send("```English only - please refrain from  posting in non-English as it's considered spam. Ongoing spam will result in penalty.```")
        #         #await self.handle_spam(message, "Non-english posting.", False)
        #         clogger(f"Non-english text detected: {message.clean_content}")
        #     else:
        #         clogger(f"English text detected: {message.clean_content}")

        if after.content.find("discord.gg") != -1:
            await message.delete()
            self.spam_log_data = load_json_config("spamlogs.json")
            if str(after.author.id) not in self.spam_log_data:
                self.spam_log_data[after.author.id] = {"spam_count": 1}
            else:
                self.spam_log_data[after.author.id]["spam_count"] += 1


            if self.spam_log_data[str(message.author.id)]["spam_count"] >= 5:
                self.spam_log_data[str(message.author.id)]['spam_count'] = 0
                await message.author.timeout_for(datetime.timedelta(hours=24), reason="Timeout for Invite spam.")
                embed = discord.Embed(title=f"{message.author.display_name} has been put in Timeout!", description=f"{message.author.mention} has been timed out for 24hrs for: {reason}. <@&1001210793204912341>", color=0x00ff00)
                if message.author.avatar != None:
                    embed.set_thumbnail(url=message.author.avatar.url)
                embed.set_footer(text="Dispam Spam Prevention")
                await self.bot.get_channel(828931953955831838).send(embed=embed)
                await message.author.send(f"{message.author.mention} you have been timed out for invite for: {reason}, this may result in a ban. You have been warned {self.spam_log_data[str(message.author.id)]['spam_count']} times.")
            else:
                await message.author.send(f"{message.author.mention} you have been warned for: {reason}. You have been warned {self.spam_log_data[str(message.author.id)]['spam_count']} times.")
            
            write_json_config("spamlogs.json", self.spam_log_data)

    
    @commands.slash_command(name='spam', description='Check the spam count of a user.')
    @commands.has_any_role(['Wielder of the flame of Anor', 'Admin'])    
    async def spam(self, ctx, user: discord.Member):
        if user.id not in self.spam_log_data:
            await ctx.send_response(f"{user.mention} has not been flagged for spam.", delete_after=10)
        else:
            await ctx.send_response(f"{user.mention} has been warned ```{self.spam_log_data[str(user.id)]['spam_count']} times.``` for spam.", delete_after=10)

    @commands.slash_command(name='resetspam', description='Recent a users spam violations.')
    @commands.has_role('Admin')
    async def spam_reset(self, ctx, user: discord.Member):
        self.spam_log_data = load_json_config("spamlogs.json")

        if user.id not in self.spam_log_data:
            await ctx.send_response(f"{user.mention} has not been flagged for spam.", delete_after=10)
        else:
            self.spam_log_data[str(user.id)]['spam_count'] = 0
            write_json_config("spamlogs.json", self.spam_log_data)
            await ctx.send_response(f"{user.mention} has been reset.", delete_after=10)

def setup(client):
    client.add_cog(Dispam(client))
