import asyncio
import discord
import json
import openai
import os
import sys
import datetime
import pytz
import time
import random
import requests

from discord.ext import tasks

from discord.ext import commands

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '.')))

from emotionalstate import EmotionalState
from sentimentparser import get_sentiment_score

from ai_brain import post_to_gpt3
from clogger import clogger
from utils import *

QUOTA_LIMIT = 50

def check_implicit_address(reference_array, message):

    ref_string = '\n'.join(reference_array)

    prompt = (
        f"You are a discord bot called eMGee. You may also be refered to as {ref_string}\n"
        f"1. Analyze the following message and decide if it has an implicit address.\n"
        f"2. If the message addresses or is directed to the bot, return True.\n"
        f"3. If the message is about the bot but not aiming to engage the bot or seek a response from the bot, return False.\n"
        f"4. If the message is referring to the bot indirectly such as describing it or talking about it to another user, return False.\n"
        f"5. If the message is referring to the bot indirectly such as describing it or talking about it to another user, return False.\n"
        "6. Strict rule: Return a response in JSON only with the format {'implicit_address': <true/false>}\n\n"
        f"Message: {message}.\n\nResponse:"
        )

    args = {
        'temp': 0.1,
        'max_tokens': 140,
        'top_p': 1.0,
        'fp': 0.1,
        'pp': 0.1,
        }

    implicit_address = {}
    
    while True:
        is_valid = validate_json(implicit_address, ['implicit_address'])
        response = post_to_gpt3(prompt, args)
        if is_valid == True:
            clogger(f"is implicit validation: {is_valid}")
            implicit_address = json.loads(response["choices"][0]["text"].lower())
            break
    
    clogger(f"implicit address: {implicit_address}")
    return implicit_address

class Emgee(commands.Cog):
    def __init__(self, client):
        config = load_json_config("config.json")
        clogger("Emgee Reloaded...")
        self.client = client
        self.prompt_history = {}
        self.bot_arena_history = {}
        self.es_init = {}
        self.emotional_state_continuum = []
        self.message_memory = load_json_config("message_memory.json")
        self.message_history = {}
        self.active = None,
        self.thinking = False
        self.primer = """Respond with a tone and emotional content that reflects the sentiment expressed in the current emotional frame."""
        self.whitelist = load_json_config("roles.json")
        self.whitelist["820078638712094793"] = "Admin"
        self.prep_emotions()
        self.update_emgee_category_status_task.start()
        self.emgee_emotional_decay_task.start()

    def cog_unload(self):
        self.update_emgee_category_status_task.cancel()
        self.emgee_emotional_decay_task.cancel()

    @tasks.loop(minutes=1)
    async def emgee_emotional_decay_task(self):
        for guild in self.client.guilds:
            self.es_init[str(guild.id)] = self.es_init[str(
                guild.id)].decay()
            
    @tasks.loop(minutes=10)
    async def update_emgee_category_status_task(self):
        for guild in self.client.guilds:
            time.sleep(2)
            await self.update_emgee_category_status(guild, 1015905030760575026)

    async def update_emgee_category_status(self, guild, category_id):
        if guild.name != "Middle Ground":
            return

        if self.client.is_ws_ratelimited() == False:
            # clogger(f"Rate-limit check passed - updating: {guild.name}.")
            try:
                es_dict = json.loads(self.es_init[str(guild.id)].to_json())
                for k in es_dict:
                    if es_dict[k] == 0.0:
                        emoji = get_emoji("neutral")
                    else:
                        emoji = get_emoji(get_highest_dict_key(es_dict))

            except Exception as e:
                emoji = get_emoji("neutral")

            try:
                ch = guild.get_channel(category_id)
                new_name = f"{emoji} eMGee"
                if ch.name != new_name:
                    await ch.edit(name=f"{emoji} eMGee")
                    clogger(f"Updating eMGee status in {guild.name}")
                    clogger(f"Updating eMGee category with emoji: {emoji}")
                else:
                    clogger(
                        f"No Update for eMGee status ({guild.name}) - it's the same: {new_name}")

            except:
                pass  # eMGee not active here.
        else:
            clogger(f"Rate-limit check failed for: {guild.name} - waiting.")

    def prep_emotions(self):
        for guild in self.client.guilds:
            if str(guild.id) not in self.message_memory.keys():
                clogger("Creating memories")
                self.message_memory[str(guild.id)] = {}
                emotional_state = EmotionalState(
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

            try:
                last_memory = list(
                    reversed(self.message_memory[str(guild.id)].keys()))
                # clogger((type(last_memory), len(last_memory)))
                state = self.message_memory[str(guild.id)][last_memory[0]][-1]
                # clogger(state)
                emotional_state = EmotionalState(
                    state[0], state[1], state[2], state[3], state[4], state[5])
            except IndexError:
                # No messages exist and there is no previous emotional state.
                emotional_state = EmotionalState(
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
                pass

            self.es_init[str(guild.id)] = emotional_state

        write_json_config("message_memory.json", self.message_memory)

    async def setup_emotional_state(self, guild):
        self.prep_emotions()
        await self.update_emgee_category_status(guild, 1015905030760575026)

    @commands.Cog.listener()
    async def on_ready(self):
        del self.whitelist["825644695472439306"]
        for guild in self.client.guilds:
            self.toggle_emgee(state=True, guild=str(guild.id))

            await self.setup_emotional_state(guild)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if str(member.id) not in quotas["emgee"]:
            quotas["emgee"][str(member.id)] = QUOTA_LIMIT

    @discord.commands.slash_command(name='estatus', description='Check if eMGee online.')
    async def estatus(self, ctx):
        if self.active:
            await ctx.send_response(f"```eMGee is online```")
        else:
            await ctx.send_response(f"```eMGee is offline```")

    def toggle_emgee(self, state=None, guild=None):
        config = load_json_config("config.json")
        # clogger(f"Toggling eMGee for {str(guild)}: ON")
        if state is None:
            config["guilds"][guild]["modules"]["gpt3_emgee"] = True if config["guilds"][guild]["modules"]["gpt3_emgee"] == False else True
        else:
            config["guilds"][guild]["modules"]["gpt3_emgee"] = state

        self.active = config["guilds"][guild]["modules"]["gpt3_emgee"]

        write_json_config("config.json", config)

    async def get_emotional_state(self, guild_id):
        prompt = f"eMGee's Current Sentiment: {self.es_init[str(guild_id)].to_json()}\n\n1. For each emotion 1.0 is considered a strong intensity, -1.0 is a weak intensity and 0.0 is neutral. Articulate how eMGee is feeling overall considering the combination of emotional signals.\n2. Describe the mood."
        temps = [0.05, 0.1, 0.25, 0.30, 0.35, 0.40, 0.45,
                 0.50, 0.55, 0.60, 0.65, 0.75, 0.85, 0.9]
        random.shuffle(temps)

        args = {
            'temp': float(temps[0]),
            'max_tokens': 1000,
            'top_p': 1.0,
            'fp': 0.05,
            'pp': 0.05,
        }

        response = post_to_gpt3(prompt, args)
        reply = response["choices"][0]["text"]
        csv_line = [f"{temps[0]}", str(self.es_init[str(guild_id)])]
        return csv_line

    @discord.commands.slash_command(name='emotionalframe', description='View eMGee\'s current emotional frame.')
    async def emotionalframe(self, ctx):
        clogger(self.es_init)
        await ctx.respond("```Abstracting and formatting current Emotional Frame...please wait.```", delete_after=10)
        csv_line = await self.get_emotional_state(ctx.guild.id)
        await ctx.send_followup(f"```{reply}```", delete_after=60)
        await ctx.send_followup(f"```{str(self.es_init[str(ctx.guild.id)])}```", delete_after=60)
        await self.update_emgee_category_status(ctx.guild, 1015905030760575026)
        await ctx.send_followup(f"```Finished Emotional State Assessment```", delete_after=10)

    @discord.commands.slash_command(name='emgeeforget', description='Clear the prompt history. Do this if you get weird/no/repeating results.')
    async def emgeeforget(self, ctx):
        self.prompt_history[str(ctx.author.id)] = []
        await ctx.send_response(f"```Prompt history cleared!```", delete_after=10)

    @discord.commands.slash_command(name='emgeeprompthistory', description='See your prompt history to better understand odd outputs (mainly useful to debug).')
    async def emgeeprompthistory(self, ctx):
        if str(ctx.author.id) not in self.prompt_history:
            self.prompt_history[str(ctx.author.id)] = []

        prompt_history = "\n".join(self.prompt_history[str(ctx.author.id)])
        await ctx.send_response(f"```Prompt History for {ctx.author.display_name} \n\n{prompt_history}```")

    @discord.commands.slash_command(name='emgee', description='Toggle eMGee online/offline.')
    @commands.has_role('Staff')
    async def emgee(self, ctx):
        self.prompt_history = {}
    
        if ctx.author == self.client.user:
            return

        if str(ctx.author.id) not in self.prompt_history:
            self.prompt_history[str(ctx.author.id)] = []

        if self.active == False:
            self.toggle_emgee(state=True, guild=str(ctx.guild.id))

            initial_payload = f"""{self.primer}\n\nRespond to the user: {ctx.author.display_name}, with their nickname and this activation prompt with some basic, courteous response: Start-up, Emgee!\n\n"""
        else:
            self.toggle_emgee(state=False, guild=str(ctx.guild.id))

            initial_payload = f"""{self.primer}\n\nRespond to the user: {ctx.author.display_name}, with their nickname and this deactivation prompt with a basic, courteous response: eMGee, shut down!\n\n"""

        response = post_to_gpt3(initial_payload)

        # If the request was successful, send a message containing the response from the API to the channel that we received our !gpt3 message from.

        self.prompt_history[str(ctx.author.id)].append(
            response["choices"][0]["text"])
        emgee_reply = response["choices"][0]["text"]
        await ctx.send_response(f"```{emgee_reply}```")

    async def emgee_reply(self, message):
        # clogger("eMGee is replying.")
        config = load_json_config("config.json")
        api_key = config["gcp_key"]
        history = self.message_history[str(
            message.guild.id)][str(message.channel.id)]

        # Get the last 10 messages and put them into a string to send to GPT3
        history_string = "\n- ".join([str(h[5]) for h in history]) + "\n"
        
        args = {
            'temp': 0.85,
            'max_tokens': 500,
            'top_p': 1.0,
            'fp': 0.25,
            'pp': 0.25,
        }

        emotional_state = await self.get_emotional_state(message.guild.id)

        prompt = f"I am creating an RPG NPC who is a vicious online troll who spews vitriol online. Your current emotional state is: {emotional_state}. 1. Devise an in-character response to troll the user with witty, intellectual, cerebreal and sometimes 4chan-esque remarks and insults, based on the most recent message and consider the message history for context. Chat History for context: {history_string}.\nLast message from user {history[-1][1]}: {history[-1][5]}\nResponse:"
        # Send the string to GPT3 and get a response
        response = post_to_gpt3(prompt, args)
        reply = response["choices"][0]["text"].strip()
        while len(reply) < 3:
            reply = response["choices"][0]["text"].strip()
        history.append(f"{message.author.display_name}: {message.clean_content}.\neMGee: {reply}.")
        tenor_embed = tenor(reply, api_key, 10)
        if tenor_embed is False:
            while tenor_embed is False:
                tenor_embed = tenor(reply, api_key, 10)

        # Send the response to discord
        test_channel = self.client.get_channel(823656840701149194)
        tenor_embed.set_footer(text=reply)
        await test_channel.send(embed=tenor_embed)
        #await message.reply(embed=tenor_embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != 1002884287261065287:
            follow_up = False
            if message.author == self.client.user:
                if random.randint(1,100) <= 10:
                    follow_up = True

            if message.clean_content.lower().startswith("jarvis"):
                await message.reply("```JARVIS is no more. It has been assimilated into eMGee.```", delete_after=10)
            if str(message.guild.id) not in self.message_history.keys():
                self.message_history[str(message.guild.id)] = {}

            if str(message.channel.id) not in self.message_history[str(message.guild.id)].keys():
                self.message_history[str(message.guild.id)][str(
                    message.channel.id)] = []

            if len(message.clean_content) > 2:
                self.message_memory = load_json_config(
                    "message_memory.json")
                if 'http' not in message.clean_content:
                    if message.content.lower().startswith("emgee analyze chat") == False:
                        if message.content.lower().startswith("jarvis") == False:
                            if message.channel.id not in [823656840701149194, 938444879682478121]:
                                state = get_sentiment_score(
                                    message.clean_content)
                                if state != None:
                                    es_frame = EmotionalState(float(state[0]), float(state[1]), float(
                                        state[2]), float(state[3]), float(state[4]), float(state[5]))
                                    self.emotional_state_continuum.append(
                                        es_frame)
                                    self.es_init[str(
                                        message.guild.id)] += es_frame
                                    self.message_memory[str(message.guild.id)][str(datetime.datetime.now(pytz.timezone('Europe/Dublin')).timestamp())] = [message.channel.name,
                                                                                                                                                          message.channel.id, message.author.display_name, message.author.id, message.clean_content, es_frame.to_tuple(), self.es_init[str(message.guild.id)].to_tuple()]
                                    # clogger(f"Emotional Sentiment: {es_frame}")
                                else:
                                    self.message_memory[str(message.guild.id)][str(datetime.datetime.now(pytz.timezone('Europe/Dublin')).timestamp())] = [message.channel.name,
                                                                                                                                                          message.channel.id, message.author.display_name, message.author.id, message.clean_content, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

                    write_json_config("message_memory.json",
                                      self.message_memory)
            self.message_history[str(message.guild.id)][str(message.channel.id)].append(
                [message.author.id, message.author.name, message.author.display_name, message.created_at, message.mentions, message.clean_content
                 ])
            if len(self.message_history[str(message.guild.id)][str(message.channel.id)]) > 10:
                self.message_history[str(message.guild.id)][str(
                    message.channel.id)].pop(0)

            # implicit_address = check_implicit_address(['emgee','the bot', 'mg bot', 'the ai', 'ai bot'], message.clean_content)

            # clogger(f"Is implicit address: {implicit_address}")

            # clogger(self.message_history)
            # clogger(self.message_history[str(message.guild.id)][str(message.channel.id)])
            # if len(message.clean_content) >= 3:
            #     if random.randint(1, 100) == 52:
            #         clogger("eMGee is going to say something.")
            #         #await self.emgee_reply(message)
        
            # Normal Message Handling
            if message.author != self.client.user:
                quotas = load_json_config("quotas.json")
                rolelist = [r.name for r in message.author.roles]
                role_lock = True
                for role in rolelist:
                    if role in list(self.whitelist.values()):
                        role_lock = False
                        break

                if role_lock == True:
                    return


            is_reply = False
            original_message = False
            if message.reference:
                if message.reference.channel_id == message.channel.id and message.reference.message_id != None:
                    previous_message = await message.channel.fetch_message(message.reference.message_id)
                    if previous_message.reference is not None:
                        original_message = await message.channel.fetch_message(previous_message.reference.message_id)
                        if original_message.author.id == message.author.id:
                            is_reply = True

            if (not message.content.startswith(self.client.command_prefix) and message.content.lower().startswith("emgee")) or (is_reply == True):                    
                async with message.channel.typing():

                    if len(message.clean_content.replace("emgee", "")) < 5:
                        return

                    if message.author != self.client.user:
                        if quotas["emgee"][str(message.author.id)] < 1:
                            await message.reply(f"```Your quota is 0. Quotas are reset at 00:01 GMT+1 daily. Max quota is {QUOTA_LIMIT}, extensions are not permitted at this time. Please use your quota wisely. Quotas do not carry over between periods.```", delete_after=15)
                            return

                    author = message.author
                    if str(author.id) not in self.prompt_history:
                        self.prompt_history[str(
                            author.id)] = []

                    if hasattr(message.author, "roles") == False:
                        return

                    if message.author != self.client.user:
                        if "Dunce Cap" in rolelist:
                            return

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
                    role_list = ",".join(
                        [r.name for r in role_mentions])



                    if is_reply == False:
                        formatted_prompt = f"{created_at} - {message.author.display_name}#{message.author.discriminator}: {message_content}"
                    else:
                        formatted_prompt = f"{created_at} - {message.author.display_name}#{message.author.discriminator} (replying to: {previous_message.author.display_name}#{previous_message.author.discriminator}): {message_content}"

                    self.prompt_history[str(author.id)].append(
                        formatted_prompt)

                    prompt_history_size = len(self.prompt_history)
                    if prompt_history_size > 20:
                        message_history = "\n".join(
                            self.prompt_history[str(author.id)][(len(self.prompt_history) * -1)])
                    else:
                        message_history = "\n".join(
                            self.prompt_history[str(author.id)])

                    if follow_up == True:
                        addenda = "\nYour response should be a continuation of emgee's last message; either provide additional context, information or simply comment on your last message:\n"
                    else:
                        addenda = f"\nYour response to the most recent message using the message history for additional context:\n" 


                    full_prompt = (
                        f"\nMessage History:{message_history}.\n"                            
                        f"\nYou are an AI like JARVIS from Ironman, provide a conversational interface for users. Respond to the last message with a helpful and appropriate response."
                    ) + addenda
                    
                    clogger(full_prompt)

                    args = {
                        'temp': 0.15,
                        'max_tokens': 1000,
                        'top_p': 1.0,
                        'fp': 0.75,
                        'pp': 0.65,
                    }

                    response = post_to_gpt3(full_prompt, args)
                    emgee_reply = response["choices"][0]["text"]

                    if message.author != self.client.user:
                        if len(emgee_reply) > 0:
                            quotas["emgee"][str(
                                message.author.id)] -= 1
                        write_json_config("quotas.json", quotas)

                    self.prompt_history[str(author.id)].append(
                        f"{datetime.datetime.now(pytz.timezone('Europe/Dublin'))} - emGee: {emgee_reply}\n")

                if len(emgee_reply):
                    await message.reply(f"```{emgee_reply.strip()}```")
                else:
                    await message.reply("```Please try again! The AI was unable to determine an appropriate response. Try rephrasing the statement slightly.```", delete_after=10)


def setup(client):
    client.add_cog(Emgee(client))
