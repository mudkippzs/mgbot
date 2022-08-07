import asyncio
import discord
import json
import openai
import os
import sys

from discord.ext import commands

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '.')))

from clogger import clogger
from utils import *


class Emgee(commands.Cog):
    def __init__(self, client):
        config = load_json_config("config.json")
        
        self.client = client
        self.prompt_history = {}
        self.active = None
        self.thinking = False
        self.primer = """Respond in the voice of FRIDAY the AI from Ironman; don't use @'s or label your responses, respond directly. Avoid over use of symbols and emojis."""
        for guild in self.client.guilds:
            self.toggle_emgee(state=True, guild=guild)

    def toggle_emgee(self, state=None, guild=None):
        config = load_json_config("config.json")
        if state is None:
            config["guilds"][guild]["modules"]["gpt3_emgee"] = True if config["guilds"][guild]["modules"]["gpt3_emgee"] == False else True
        else:
            config["guilds"][guild]["modules"]["gpt3_emgee"] = state

        self.active = config["guilds"][guild]["modules"]["gpt3_emgee"]

        write_json_config("config.json", config)

    def post_to_gpt3(self, payload):
        openai.api_key = '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'
        formatted_payload = "\n".join(payload)
        return openai.Completion.create(
            model="text-davinci-002",
            prompt=formatted_payload,
            temperature=0.80,
            max_tokens=300,
            top_p=1,
            frequency_penalty=0.50,
            presence_penalty=0.60
        )

    @commands.command()
    async def forget(self, ctx):
        self.prompt_history[str(ctx.author.id)] = []

    @commands.command()
    async def prompthistory(self, ctx):
        if str(ctx.message.author.id) not in self.prompt_history:
            self.prompt_history[str(ctx.message.author.id)] = []

#        for prompt in self.prompt_history[str(ctx.message.author.id)]:
 #           clogger(prompt)
        await ctx.send(self.prompt_history[str(ctx.message.author.id)])

    @commands.command(hidden = True)
    @commands.has_role('Staff')
    async def emgee(self, ctx):
        self.prompt_history = {}

        if str(ctx.message.author.id) not in self.prompt_history:
            self.prompt_history[str(ctx.message.author.id)] = []

        if self.active == False:
            self.toggle_emgee(state=True)
            if ctx.message.author == self.client.user:
                return

            initial_payload = f"""{self.primer}\n\nRespond to the user: {ctx.message.author.display_name}, with their nickname, this Initial activation Prompt with some basic, courteous response: Start-up, Jarvis!\n\n."""
        else:            
            self.toggle_emgee(state=False)

            initial_payload = f"""{self.primer}\n\nRespond to the user: {ctx.message.author.display_name}, with their nickname, Initial deactivation Prompt with a basic, courteous response: JARVIS, shut down.!\n\n"""

        response = self.post_to_gpt3([initial_payload,])

        # If the request was successful, send a message containing the response from the API to the channel that we received our !gpt3 message from.

        self.prompt_history[str(ctx.message.author.id)].append(response["choices"][0]["text"])
        emgee_reply = response["choices"][0]["text"]
        await ctx.send(f"```{emgee_reply}```")

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.content.startswith(self.client.command_prefix) and message.content.lower().startswith("emgee"):
            #message.content.replace("@emgee", "")
            if self.active and message.author != self.client.user:
                if self.thinking == False:
                    self.thinking == True
                    author = message.author
                    if str(author.id) not in self.prompt_history:
                        self.prompt_history[str(author.id)] = []

                    rolelist = [str(r) for r in message.author.roles]
                    if "Dunce Cap" in rolelist:
                        return

                    if "Old Fag" in rolelist or "Trusted Tester" in rolelist: # or message.channel.id in [1001642398797008987, 1001205346288799877, 844881586008883220]:
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
                        response = self.post_to_gpt3(self.prompt_history[str(author.id)][-20:])
                        emgee_reply = response["choices"][0]["text"]
                        self.prompt_history[str(author.id)].append(f"{emgee_reply}")
                        if len(emgee_reply):
                            await message.reply(f"```{emgee_reply.strip()}```")
                        else:
                            await message.reply("```Please try again! The AI was unable to determine an appropriate response. Try rephrasing the statement slightly.```", delete_after=10)
                        self.thinking = False
                else:
                    clogger("Jarvis is thinking... no new messages or prompts will be included.")    
            else:
                return

def setup(client):
    client.add_cog(Emgee(client))
