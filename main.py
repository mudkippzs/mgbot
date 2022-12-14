"""Discord Bot: AutoGanj
Author: Ganjdalf
"""
import asyncio
from pathlib import Path
import json
import os
import sys
import traceback

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '.')))


from clogger import clogger
from cogwatch import watch
import discord
from discord.ext import commands
from roles_views import RolesLocationView, RolesSexView, RolesInterestsView, RolesPetsView, RolesVirtueView
from utils import *

config = load_json_config("config.json")
strings = load_json_config("strings.json")

# Declare Bots required perms via Intents().
INTENTS = discord.Intents.all()


class AutoGanj(commands.Bot):
    """A bot for managing a discord server that extends discord.py Bot class."""

    def __init__(self):
        """Kick off instance of Fatebot."""
        super().__init__(
            description=strings["strings"]["welcome_message"], intents=INTENTS)
        self.load_extensions()

    def load_extensions(self):
        """Load extensions on start of the bot."""
        for ext in Path("cogs").glob("./*.py"):
            dot_path = str(ext).replace(os.sep, ".")[:-3]
            try:
                self.load_extension(dot_path)
            except Exception as e:
                clogger(f"Cant load {dot_path}")

    @watch(path='cogs', debug=False)
    async def on_ready(self):
        """Client Even - on_ready: triggers when Client is logged in and listening for events."""
        clogger(f"{self.user} is online!")
        self.invites = {}
        for cog in sorted(self.cogs):
            clogger(f"Loaded: {cog}")
        clogger("------------------")
        clogger(f"Loaded: {len(self.cogs)} cogs")

        for guild in self.guilds:
            if str(guild.id) not in config["guilds"]:
                clogger(f"Adding {guild.name} to config...")
                config["guilds"][str(guild.id)] = {
                    "prefix": "&",
                    "choose_roles": None,
                    "modules":
                        {
                    "tripwire": True,
                    "userdata": True,
                    "bakerbot": False,
                    "logger": True,
                    "jarvis": True,
                    "emgee": False,
                    "basedboost": True,
                    "quotamanager": True,
                    "rules": True,
                    "roles": True,
                    "dispam": True,
                    "raiddefense": True
                    }
                }

            clogger(
                f"Connected to server: {guild.name} (Members: {guild.member_count})...")
            self.command_prefix = config["guilds"][str(guild.id)]["prefix"]
            self.invites[str(guild.id)] = await guild.invites()

            write_json_config("config.json", config)

        clogger("Loading views...")
        # Registers a View for persistent listening
        self.add_view(RolesLocationView(bot=self))
        # Registers a View for persistent listening
        self.add_view(RolesSexView(bot=self))
        # Registers a View for persistent listening
        self.add_view(RolesInterestsView(bot=self))
        # Registers a View for persistent listening
        self.add_view(RolesPetsView(bot=self))
        # Registers a View for persistent listening
        self.add_view(RolesVirtueView(bot=self))

        clogger(
            f"Loaded {len(self.invites)} invites from {len(self.guilds)} servers.")

    async def on_error(self, event_method, *args, **kwargs):
        """Client Even - on_error: triggers when an error occurs."""

        values = [f'{type(arg)}: {arg}' for arg in args]
        args = ', '.join(values)

        values = ['{}: {}'.format(k, v) for k, v in kwargs.items()]
        kwargs = ', '.join(values)

        error = 'Error handling "{}" with "{}" "{}"'.format(
            event_method, args, kwargs)
        clogger(error)

        exc_type, exc_obj, exc_tb = sys.exc_info()

        # We take all the traceback object and format it nicely with
        # a limit to 3 lines (if any), the exception type and message
        # is also extracted and nicely formatted. Once all that is done
        # we prepare an embed containing all this information and send it
        # to the .debug channel.

        channel = self.get_channel(1032057550201430087)  # ID of #.debug
        stacktrace = exc_tb
        exc_type_msg = f'**Exception Type:** {exc_type}'
        embed = discord.Embed(title=f'[Bug] Exception in `{self.__class__.__name__}.{event_method}`',
                              description=f'```py\n{exc_type_msg}\n'
                                          f'{str(exc_obj)}\n'
                                          f'```', color=0xFF0000)

        extracted_tb = traceback.extract_tb(stacktrace)
        formatted_tb = traceback.format_list(extracted_tb)

        for tb in formatted_tb:
            embed.add_field(name="\u200b", value=f"```{tb}```", inline=False)

        embed.set_footer(text=f'Generated by AutoGanj!')

        error_embed = await channel.send(embed=embed)

        # Add action reacts
        await error_embed.add_reaction('\u2705')
        await error_embed.add_reaction('\U0001F41B')
        await error_embed.add_reaction('\U0001F5D1')

    async def on_command_error(self, ctx, error):
        """Client Even - on_command_error: triggers when an error occurs in a command."""
        if isinstance(error, commands.CommandNotFound):
            clogger(f"Error: Command not found: {error}")
            clogger(sys.exc_info()[1])
            return
        raise error


async def main():
    """Create the bot and start it."""
    client = AutoGanj()
    await client.start(config["token"])

if __name__ == '__main__':
    asyncio.run(main())
