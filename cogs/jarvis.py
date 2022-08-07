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

QUOTA_LIMIT = 50

class Jarvis(commands.Cog):
    def __init__(self, client):
        config = load_json_config("config.json")        
        self.client = client
        self.prompt_history = {}
        self.message_memory = {}
        self.active = None
        self.thinking = False
        self.primer = """Respond in the voice of JARVIS the AI from Ironman; don't use @'s or label your responses, respond directly. Avoid over use of symbols and emojis."""
        self.whitelist = load_json_config("roles.json")
        
    
    @commands.Cog.listener()
    async def on_ready(self):
        del self.whitelist["825644695472439306"]
        for guild in self.client.guilds:
            self.toggle_jarvis(state=True, guild=str(guild.id))

    @commands.command(name='jstatus', help='Check if JARVIS online.')
    async def jstatus(self, ctx):
        if self.active:
            await ctx.send(f"```JARVIS is online```")
        else:
            await ctx.send(f"```JARVIS is offline```")

    def toggle_jarvis(self, state=None, guild = None):
        config = load_json_config("config.json")
        clogger(f"Toggling JARVIS for {str(guild)}: ON")
        if state is None:
            config["guilds"][guild]["modules"]["gpt3_jarvis"] = True if config["guilds"][guild]["modules"]["gpt3_jarvis"] == False else True
        else:
            config["guilds"][guild]["modules"]["gpt3_jarvis"] = state

        self.active = config["guilds"][guild]["modules"]["gpt3_jarvis"]

        write_json_config("config.json", config)

    def post_to_gpt3(self, payload):
        openai.api_key = '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'
        #formatted_payload = "\n".join(payload)
        return openai.Completion.create(
            model="text-davinci-002",
            prompt=payload,
            temperature=0.15,
            max_tokens=500,
            top_p=1,
            frequency_penalty=0.25,
            presence_penalty=0.35
        )

    @commands.command(name='forget', help='Clear the prompt history. Do this if you get weird/no/repeating results.')
    async def forget(self, ctx):
        self.prompt_history[str(ctx.author.id)] = []

    @commands.command(name='prompthistory', help='See your prompt history to better understand odd outputs (mainly useful to debug).')
    async def prompthistory(self, ctx):
        if str(ctx.message.author.id) not in self.prompt_history:
            self.prompt_history[str(ctx.message.author.id)] = []

        await ctx.send(self.prompt_history[str(ctx.message.author.id)])

    @commands.command(hidden = True)
    @commands.has_role('Staff')
    async def jarvis(self, ctx):
        self.prompt_history = {}

        if str(ctx.message.author.id) not in self.prompt_history:
            self.prompt_history[str(ctx.message.author.id)] = []

        if self.active == False:
            self.toggle_jarvis(state=True, guild = str(ctx.guild.id))
            if ctx.message.author == self.client.user:
                return

            initial_payload = f"""{self.primer}\n\nRespond to the user: {ctx.message.author.display_name}, with their nickname, this Initial activation Prompt with some basic, courteous response: Start-up, Jarvis!\n\n."""
        else:            
            self.toggle_jarvis(state=False, guild = str(ctx.guild.id))

            initial_payload = f"""{self.primer}\n\nRespond to the user: {ctx.message.author.display_name}, with their nickname, Initial deactivation Prompt with a basic, courteous response: JARVIS, shut down.!\n\n"""

        response = self.post_to_gpt3([initial_payload,])

        # If the request was successful, send a message containing the response from the API to the channel that we received our !gpt3 message from.

        self.prompt_history[str(ctx.message.author.id)].append(response["choices"][0]["text"])
        jarvis_reply = response["choices"][0]["text"]
        await ctx.send(f"```{jarvis_reply}```")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author != self.client.user:            
            quotas = load_json_config("quotas.json")
            if str(message.author.id) not in quotas["jarvis"]:
                quotas["jarvis"][str(message.author.id)] = QUOTA_LIMIT

        #     if str(message.channel.id) not in self.message_memory:
        #         self.message_memory[str(message.channel.id)] = []

        #     member_list = [str({"uid": m.id, "name": m.display_name, "roles": ','.join([r.name for r in m.roles])}) for m in message.guild.members if m.status == discord.Status.online]

        #     if str(message.id) not in self.message_memory[str(message.channel.id)]:
        #         message_string = f"GUILD_ID <{message.guild.id}> MESSAGE_ID <{message.id}> CHANNEL_NAME <{message.channel.id}> MESSAGE_CREATED <{message.created_at}> AUTHOR <{message.author.display_name}> MESSAGE <{message.clean_content}>"
        #         self.message_memory[str(message.channel.id)].append(message_string)

        #     if len(self.message_memory) > 100:
        #         self.message_memory = self.message_memory[:100]

        #     message_memory_string = "Current Online Members\n\n" + "\n".join(member_list) + "\n\nMessage Log:\n\n" + "\n".join(self.message_memory[str(message.channel.id)])

        #     message_memory_string = message_memory_string[:3000]

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
