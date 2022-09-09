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

from clogger import clogger
from utils import *

QUOTA_LIMIT = 50


def get_emoji(emotion):
    if emotion == "neutral":
        return random.choice([
            "😐"
        ])

    if emotion == "joy":
        return random.choice(["😀", "😁", "😂", "🤣", "😏", "😄", "🤪", "😋", "☺️", "😎", "😏", "🤠", "🤤", "🤗", "😌"])
    if emotion == 'fear':
        return random.choice(["😨", "😧", "😰", "😦", "😳", "😱", "🥶", "😥", "😓", "😧"])
    if emotion == 'disgust':
        return random.choice(["🤢", "🤮", "😖", "😫", "😩", "😵‍💫", "😬", "😒"])
    if emotion == 'sadness':
        return random.choice(["😔", "😥", "😢", "😭", "🤧", "😭", "🥺", "😞"])

    if emotion == 'anger':
        return random.choice(["👿", "😡", "🤬", "😤", "👿", "😠", "💢"])

    if emotion == 'surprise':
        return random.choice(["🤯", "😲", "🙀", "😵", "🥴", "🧎‍♀️", "😵", "😮", "😯"])


class Emgee(commands.Cog):
    def __init__(self, client):
        config = load_json_config("config.json")
        clogger("Emgee Reloaded...")
        self.api_key = config["ai_key"]
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
            # clogger(f"eMGee Emototional decay for {guild.name}")
            # clogger(f"B -> {self.es_init[str(guild.id)]}")
            self.es_init[str(guild.id)] = self.es_init[str(
                guild.id)].decay()
            # clogger(f"A -> {self.es_init[str(guild.id)]}")

    @tasks.loop(minutes=10)
    async def update_emgee_category_status_task(self):
        for guild in self.client.guilds:
            time.sleep(2)
            await self.update_emgee_category_status(guild, 1015905030760575026)

    async def update_emgee_category_status(self, guild, category_id):
        if guild.name != "Middle Ground":
            return

        if self.client.is_ws_ratelimited() == False:
            clogger(f"Rate-limit check passed - updating: {guild.name}.")
            es_dict = json.loads(self.es_init[str(guild.id)].to_json())
            for k in es_dict:
                if es_dict[k] == 0.0:
                    emoji = get_emoji("neutral")
                else:
                    emoji = get_emoji(get_highest_dict_key(es_dict))

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

    @discord.commands.slash_command(name='emotionalframe', description='View eMGee\'s current emotional frame.')
    async def emotionalframe(self, ctx):
        clogger(self.es_init)
        prompt = f"eMGee's Current Sentiment: {self.es_init[str(ctx.guild.id)].to_json()}\n\n1. For each emotion 1.0 is considered a strong intensity, -1.0 is a weak intensity and 0.0 is neutral. Articulate how eMGee is feeling overall considering the combination of emotional signals.\n2. Describe the mood."
        await ctx.respond("```Abstracting and formatting current Emotional Frame...please wait.```", delete_after=10)
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

        response = self.post_to_gpt3(prompt, args)
        reply = response["choices"][0]["text"]
        csv_line = [f"{temps[0]}", str(self.es_init[str(ctx.guild.id)])]
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

        if str(ctx.author.id) not in self.prompt_history:
            self.prompt_history[str(ctx.author.id)] = []

        if self.active == False:
            self.toggle_emgee(state=True, guild=str(ctx.guild.id))
            if ctx.author == self.client.user:
                return

            initial_payload = f"""{self.primer}\n\nRespond to the user: {ctx.author.display_name}, with their nickname, this Initial activation Prompt with some basic, courteous response: Start-up, Emgee!\n\n."""
        else:
            self.toggle_emgee(state=False, guild=str(ctx.guild.id))

            initial_payload = f"""{self.primer}\n\nRespond to the user: {ctx.author.display_name}, with their nickname, Initial deactivation Prompt with a basic, courteous response: eMGee, shut down.!\n\n"""

        response = self.post_to_gpt3(initial_payload)

        # If the request was successful, send a message containing the response from the API to the channel that we received our !gpt3 message from.

        self.prompt_history[str(ctx.author.id)].append(
            response["choices"][0]["text"])
        emgee_reply = response["choices"][0]["text"]
        await ctx.send_response(f"```{emgee_reply}```")

    async def emgee_reply(self, message):
        # clogger("eMGee is replying.")
        # clogger(self.message_history[str(message.guild.id)][str(message.channel.id)])
        history = self.message_history[str(
            message.guild.id)][str(message.channel.id)]
        # clogger("History:")
        # clogger(history)

        # Get the last 10 messages and put them into a string to send to GPT3
        history_string = ",".join([str(h[5]) for h in history]) + "\n"
        clogger("History string:")
        clogger(history_string)

        args = {
            'temp': 0.85,
            'max_tokens': 500,
            'top_p': 1.0,
            'fp': 0.25,
            'pp': 0.25,
        }

        prompt = f"1. Form a complete and proper response to the following chat history. Keep it on topic and be polite and helpful.\n\n {history} \n\n\nResponse:"
        # Send the string to GPT3 and get a response
        response = self.post_to_gpt3(history_string, args)
        # clogger("Response:")
        # clogger(response)
        reply = response["choices"][0]["text"].strip()
        # Send the response to discord
        test_channel = self.client.get_channel(823656840701149194)
        clogger(reply)
        await test_channel.send(f"```{reply[0:1999]}```")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != 1002884287261065287:
            # Emgee free speech
            #clogger("eMGee could say something.")
            if message.author.id != self.client.user.id:
                if str(message.guild.id) not in self.message_history.keys():
                    self.message_history[str(message.guild.id)] = {}

                if str(message.channel.id) not in self.message_history[str(message.guild.id)].keys():
                    self.message_history[str(message.guild.id)][str(
                        message.channel.id)] = []

                self.message_history[str(message.guild.id)][str(message.channel.id)].append(
                    [message.author.id, message.author.name, message.author.display_name, message.created_at, message.mentions, message.clean_content
                     ])
                if len(self.message_history[str(message.guild.id)][str(message.channel.id)]) > 10:
                    self.message_history[str(message.guild.id)][str(
                        message.channel.id)].pop(0)

                # clogger(self.message_history)
                # clogger(self.message_history[str(message.guild.id)][str(message.channel.id)])

                if random.randint(1, 100) < 5:
                    clogger("eMGee is going to say something.")
                    # await self.emgee_reply(message)

            if message.channel.id == 1016121939833659502:
                if message.author.id == self.client.user.id:
                    time.sleep(2)
                    topic = "Spread of the Imperium of Man throughout the Galaxy"
                    position = "It is imperative for humanity's surival against the xeno threat."

                    args = {
                        'temp': 0.85,
                        'max_tokens': 1500,
                        'top_p': 1.0,
                        'fp': 0.65,
                        'pp': 0.25,
                    }

                    # Bot Arena
                    if message.clean_content.startswith("```[jarvis]"):
                        now = str(datetime.datetime.now(
                            pytz.timezone('Europe/Dublin')).timestamp())
                        if len(self.bot_arena_history) < 1:
                            primer = f"Produce a variation of the following sentence and make it fun, interesting and knowledgable about the topic. Elaborate on your position and put forward a premise: 'Great I'd like to debate you about: {topic}. My position is: {position}. Lets do this?'"
                            primer_response = self.post_to_gpt3(primer, args)
                            primer_reply = primer_response["choices"][0]["text"].strip(
                            )
                            while len(primer_reply) < 5:
                                primer_response = self.post_to_gpt3(
                                    primer, args)
                                primer_reply = primer_response["choices"][0]["text"].strip(
                                )

                            await message.reply(f"```[eMGee]: {primer_reply}```")
                            self.bot_arena_history[now] = primer_reply
                        else:
                            self.bot_arena_history[now] = message.clean_content

                        prompt_history = [v for v in list(
                            self.bot_arena_history.values())]
                        prompt = "\n\n".join(prompt_history[-3:])
                        final_prompt = prompt + "\n\nRebuttal:"

                        response = self.post_to_gpt3(prompt, args)
                        reply = response["choices"][0]["text"].strip()

                        while reply.count("[") > 1:
                            response = self.post_to_gpt3(prompt, args)
                            reply = response["choices"][0]["text"].strip()

                        reply = reply.replace("[jarvis]", "[eMGee]")

                        if len(reply) < 3:
                            reply = "I have nothing in mind right now, why don't you pose a premise and we can argue it?"
                        await message.channel.send(f"```[eMGee]: {reply}```")

            else:
                # Normal Message Handling
                if message.author != self.client.user:
                    quotas = load_json_config("quotas.json")
                    if str(message.author.id) not in quotas["emgee"]:
                        quotas["emgee"][str(message.author.id)] = QUOTA_LIMIT

                    rolelist = [r.name for r in message.author.roles]
                    role_lock = True
                    for role in rolelist:
                        if role in list(self.whitelist.values()):
                            role_lock = False
                            break

                    if role_lock == True:
                        return

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

                    if not message.content.startswith(self.client.command_prefix) and message.content.lower().startswith("emgee"):
                        if message.content.lower().startswith("emgee analyze chat"):
                            self.message_memory = load_json_config(
                                "message_memory.json")
                            working_memory = []
                            memory_count = 0
                            memory_limit = 10
                            memory = self.message_memory[str(message.guild.id)]
                            # clogger(memory)
                            for timestamp in reversed(list(reversed(sorted(memory.keys())))[0:memory_limit]):
                                if memory_count < memory_limit:
                                    working_memory.append(memory[timestamp])
                                    memory_count += 1
                                else:
                                    break

                            additional_instruction = message.clean_content.replace(
                                "emgee analyze chat", "")
                            prompt = "\n".join(
                                [f"Ch: {m[0]}, ChId: {m[1]}, Auth: {m[2]}, Message: {m[4]}" for m in working_memory])
                            full_prompt = f"1. PROVIDE A THOROUGH AND DEEP ANALYSES OF THE CONVERSATIONS BELOW. {additional_instruction}\n\n<CHAT HISTORY:>\n{prompt}\n<END>.\n\n"
                            # clogger(full_prompt)

                            args = {
                                'temp': 0.75,
                                'max_tokens': 1000,
                                'top_p': 1.0,
                                'fp': 0.05,
                                'pp': 0.05,
                            }

                            response = self.post_to_gpt3(full_prompt, args)
                            reply = response["choices"][0]["text"]
                            # clogger(reply)
                            await message.reply(f"```{reply}```")

                        else:
                            # message.content.replace("@emgee", "")
                            if self.active and message.author != self.client.user:
                                if self.thinking == False:
                                    self.thinking == True

                                    if len(message.clean_content.replace("emgee", "")) < 5:
                                        return

                                    if quotas["emgee"][str(message.author.id)] < 1:
                                        await message.reply(f"```Your quota is 0. Quotas are reset at 00:01 GMT+1 daily. Max quota is {QUOTA_LIMIT}, extensions are not permitted at this time. Please use your quota wisely. Quotas do not carry over between periods.```", delete_after=15)
                                        return

                                    author = message.author
                                    if str(author.id) not in self.prompt_history:
                                        self.prompt_history[str(
                                            author.id)] = []

                                    if hasattr(message.author, "roles") == False:
                                        return

                                    if "Dunce Cap" in rolelist:
                                        return

                                    # if "Old Fag" in rolelist or "Trusted Tester" in rolelist: # or message.channel.id in [1001642398797008987, 1001205346288799877, 844881586008883220]:
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
                                    formatted_prompt = f"{message_content}"

                                    self.prompt_history[str(author.id)].append(
                                        formatted_prompt)
                                    message_history = "\n".join(
                                        self.prompt_history[str(author.id)][-30:])
                                    full_prompt = f"\nYOU ARE A PERSONA NAMED EMGEE. YOU ARE AN AI IN SERVICE OF A DISCORD SERVER. YOU ACT AND ARTICULATE IN ACCORDANCE WITH YOUR EMOTIONAL STATE. WITH THE CURRENT EMOTIONAL SENTIMENT: {self.es_init[str(message.guild.id)].to_json()}\nRESPOND TO THE USER WITH THIS SENTIMENT PROFILE REFLECTED IN PERSONALITY, TONE, EMOTION, VERBOSITY, COURTEOUSNESS AND VOCABULARY.\n{message_history}"
                                    # clogger(full_prompt)

                                    args = {
                                        'temp': 0.8,
                                        'max_tokens': 1000,
                                        'top_p': 1.0,
                                        'fp': 0.1,
                                        'pp': 0.1,
                                    }

                                    response = self.post_to_gpt3(
                                        self.primer + full_prompt, args)
                                    emgee_reply = response["choices"][0]["text"]

                                    if len(emgee_reply) > 0:
                                        quotas["emgee"][str(
                                            message.author.id)] -= 1
                                    write_json_config("quotas.json", quotas)

                                    emgee_reply_final = emgee_reply.replace(
                                        self.primer, "")
                                    self.prompt_history[str(author.id)].append(
                                        f"{emgee_reply_final}")
                                    if len(emgee_reply_final):
                                        await message.reply(f"```{emgee_reply_final.strip()}```")
                                    else:
                                        await message.reply("```Please try again! The AI was unable to determine an appropriate response. Try rephrasing the statement slightly.```", delete_after=10)
                                    self.thinking = False
                                else:
                                    clogger(
                                        "eMGee is thinking... no new messages or prompts will be included.")
                            else:
                                return


def setup(client):
    client.add_cog(Emgee(client))
