import asyncio
import datetime
import pytz
import discord
import json
import openai
import os
import sys
import time

from discord.ext import commands

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '.')))

from clogger import clogger
from utils import *

QUOTA_LIMIT = 50

class Jarvis(commands.Cog):
    def __init__(self, client):
        config = load_json_config("config.json")
        clogger("Jarvis Reloaded...")
        self.api_key = config["ai_key"]    
        self.client = client
        self.prompt_history = {}
        self.bot_arena_history = {}
        self.message_memory = {}
        self.active = None
        self.thinking = False
        self.primer = """Respond in the voice of JARVIS the AI from Ironman; don't use @'s or label your responses, respond directly. Avoid over use of symbols and emojis."""
        self.whitelist = load_json_config("roles.json")
        self.whitelist["1001932664548376617"] = "Old Fag"
        
    
    @commands.Cog.listener()
    async def on_ready(self):
        del self.whitelist["825644695472439306"]
        for guild in self.client.guilds:
            self.toggle_jarvis(state=True, guild=str(guild.id))

    @discord.commands.slash_command(name='jstatus', description='Check if JARVIS online.')
    async def jstatus(self, ctx):
        if self.active:
            await ctx.send_response(f"```JARVIS is online```")
        else:
            await ctx.send_response(f"```JARVIS is offline```")

    @discord.commands.slash_command(name='spark', description='Kick off a debate between AIs.')
    @commands.has_role('Admin')
    async def spark(self, ctx):
        if ctx.channel.id == 1016121939833659502:
            prompt = "Generate a variation of the phrase: 'eMGee, let us debate/have a chat/shoot the breeze etc'. The motivation is to invite a sentient AI to debate on a topic of their choice. Vary the invitation or greeting and be suave and smooth."
            response = self.post_to_gpt3(prompt)
            reply = response["choices"][0]["text"].strip()
            clogger(reply)
            await ctx.send_response(f"```[jarvis]: {reply}```")
        else:
            await ctx.send_response(f"```This is only available in the #bot-arena channel.```", delete_after=15)

    def toggle_jarvis(self, state=None, guild = None):
        config = load_json_config("config.json")
        clogger(f"Toggling JARVIS for {str(guild)}: ON")
        if state is None:
            config["guilds"][guild]["modules"]["gpt3_jarvis"] = True if config["guilds"][guild]["modules"]["gpt3_jarvis"] == False else True
        else:
            config["guilds"][guild]["modules"]["gpt3_jarvis"] = state

        self.active = config["guilds"][guild]["modules"]["gpt3_jarvis"]

        write_json_config("config.json", config)

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
            model="text-davinci-002",
            prompt=payload,
            temperature=args['temp'],
            max_tokens=args['max_tokens'],
            top_p=args['top_p'],
            frequency_penalty=args['fp'],
            presence_penalty=args['pp']
        )


    @discord.commands.slash_command(name='forget', description='Clear the prompt history. Do this if you get weird/no/repeating results.')
    async def forget(self, ctx):
        self.prompt_history[str(ctx.author.id)] = []
        await ctx.send_response(f"```Prompt history cleared!```", delete_after=5)

    @discord.commands.slash_command(name='prompthistory', description='See your prompt history to better understand odd outputs (mainly useful to debug).')
    async def prompthistory(self, ctx):
        if str(ctx.author.id) not in self.prompt_history:
            self.prompt_history[str(ctx.author.id)] = []

        prompt_history = "\n".join(self.prompt_history[str(ctx.author.id)])
        await ctx.send_response(f"```Prompt History for {ctx.author.display_name} \n\n{prompt_history}```")

    @discord.commands.slash_command(name='jarvis', description='Toggle JARVIS online/offline.')
    @commands.has_role('Staff')
    async def jarvis(self, ctx):
        self.prompt_history = {}

        if str(ctx.author.id) not in self.prompt_history:
            self.prompt_history[str(ctx.author.id)] = []

        if self.active == False:
            self.toggle_jarvis(state=True, guild = str(ctx.guild.id))
            if ctx.author == self.client.user:
                return

            initial_payload = f"""{self.primer}\n\nRespond to the user: {ctx.author.display_name}, with their nickname, this Initial activation Prompt with some basic, courteous response: Start-up, Jarvis!\n\n."""
        else:            
            self.toggle_jarvis(state=False, guild = str(ctx.guild.id))

            initial_payload = f"""{self.primer}\n\nRespond to the user: {ctx.author.display_name}, with their nickname, Initial deactivation Prompt with a basic, courteous response: JARVIS, shut down.!\n\n"""

        response = self.post_to_gpt3([initial_payload,])

        # If the request was successful, send a message containing the response from the API to the channel that we received our !gpt3 message from.

        self.prompt_history[str(ctx.author.id)].append(response["choices"][0]["text"])
        jarvis_reply = response["choices"][0]["text"]
        await ctx.send_response(f"```{jarvis_reply}```")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == 1016121939833659502:
            time.sleep(2)
            # Bot Arena
            if message.author.id == self.client.user.id:
                if message.clean_content.startswith("```[eMGee]"):
                    now = str(datetime.datetime.now(
                        pytz.timezone('Europe/Dublin')).timestamp())
                    if len(self.bot_arena_history) < 1:
                        affirmative_prompt = "Produce a variation of the following: 'Sure Id love to debate/chat/talk/discuss that/with you"
                        response = self.post_to_gpt3(affirmative_prompt)
                        reply = response["choices"][0]["text"].strip()
                        final_prompt = f"[jarvis]: {reply}"
                        await message.reply(f"```{final_prompt}```")
                        self.bot_arena_history[now] = final_prompt
                    else:
                        self.bot_arena_history[now] = message.clean_content

                    prompt_history = [v for v in list(
                        self.bot_arena_history.values())]
                    prompt = "\n\n".join(prompt_history[-3:])
                    final_prompt = prompt + "\n\nRebuttal:"

                    args = {
                        'temp': 0.29,
                        'max_tokens': 1500,
                        'top_p': 1.0,
                        'fp': 0.15,
                        'pp': 0.15,
                    }


                    response = self.post_to_gpt3(prompt, args)
                    reply = response["choices"][0]["text"].strip()
                    
                    while reply.count("[") > 1:                            
                        response = self.post_to_gpt3(prompt, args)
                        reply = response["choices"][0]["text"].strip()

                    reply = reply.replace("[eMGee]", "[jarvis]")

                    if len(reply) < 3:
                        reply = "continue."
                    await message.channel.send(f"```[jarvis]: {reply}```")

        else:

            if message.author != self.client.user:            
                quotas = load_json_config("quotas.json")
                if str(message.author.id) not in quotas["jarvis"]:
                    quotas["jarvis"][str(message.author.id)] = QUOTA_LIMIT
            
                rolelist = [r.name for r in message.author.roles]
                role_lock = True
                for role in rolelist:
                    if role in list(self.whitelist.values()):
                        role_lock = False
                        break

                if role_lock == True:
                    return                

                if not message.content.startswith(self.client.command_prefix) and message.content.lower().startswith("jarvis"):
                    #message.content.replace("@jarvis", "")
                    if self.active and message.author != self.client.user:
                        if self.thinking == False:
                            self.thinking == True

                            if quotas["jarvis"][str(message.author.id)] < 1:
                                await message.reply(f"```Your quota is 0. Quotas are reset at 00:01 GMT+1 daily. Max quota is {QUOTA_LIMIT}, extensions are not permitted at this time. Please use your quota wisely. Quotas do not carry over between periods.```", delete_after=15)
                                return

                            author = message.author
                            if str(author.id) not in self.prompt_history:
                                self.prompt_history[str(author.id)] = []

                            if hasattr(message.author, "roles") == False:
                                return

                            if "Dunce Cap" in rolelist:
                                return


                            #if "Old Fag" in rolelist or "Trusted Tester" in rolelist: # or message.channel.id in [1001642398797008987, 1001205346288799877, 844881586008883220]:
                            channel = message.channel
                            channel_name = channel.name
                            channel_id = channel.id
                            mentions = message.mentions
                            embeds = message.embeds
                            attachments = message.attachments
                            created_at = message.created_at
                            edited = False
                            message_content = message.clean_content
                            role_mentions = message.role_mentions
                            stickers = message.stickers

                            if message.edited_at:
                                edited = True

                            embeds_count = len(embeds)
                            attachments_count = len(attachments)
                            stickers_count = len(stickers)
                            role_mentions_count = len(role_mentions)
                            role_list = ",".join([r.name for r in role_mentions])
                            formatted_prompt = f"{message_content}"
                            
                            self.prompt_history[str(author.id)].append(formatted_prompt)
                            # clogger(message_memory_string)
                            response = self.post_to_gpt3("\n".join(self.prompt_history[str(author.id)][-30:]))
                            # response = self.post_to_gpt3(message_memory_string + "\n\nPrompt History:" + "\n".join(self.prompt_history[str(author.id)][-30:]))
                            jarvis_reply = response["choices"][0]["text"]
                            
                            if len(jarvis_reply) > 0:
                                quotas["jarvis"][str(message.author.id)] -= 1
                            write_json_config("quotas.json", quotas)

                            self.prompt_history[str(author.id)].append(f"{jarvis_reply}")
                            if len(jarvis_reply):
                                await message.reply(f"```{jarvis_reply.strip()}```")
                            else:
                                await message.reply("```Please try again! The AI was unable to determine an appropriate response. Try rephrasing the statement slightly.```", delete_after=10)
                            self.thinking = False
                        else:
                            clogger("Jarvis is thinking... no new messages or prompts will be included.")    
                    else:
                        return

def setup(client):
    client.add_cog(Jarvis(client))
