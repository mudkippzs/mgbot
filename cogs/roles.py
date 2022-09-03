import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ui import View, Item, Button, Select
import sys
import os


sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '.')))

from clogger import clogger
from roles_views import RolesLocationView, RolesInterestsView, RolesPetsView


class RoleManagement(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command()
    @commands.has_role('Admin')
    async def roles(self, ctx):
        """
        This command will allow users to add/remove roles from their profile.
        """
        if ctx.channel.id in [1002643541257879662, 1002884287261065287]:
            # await ctx.author.send("Choose your Location!", view=RolesLocationView(bot=self.client))
            # await ctx.author.send("Choose your Server Alerts!", view=RolesInterestsView(bot=self.client))
            # await ctx.author.send("Choose your Favorite Pets!", view=RolesPetsView(bot=self.client))
            await ctx.send_response("Choose your Location!", view=RolesLocationView(bot=self.client))
            await ctx.send_response("Choose your Server Alerts!", view=RolesInterestsView(bot=self.client))
            await ctx.send_response("Choose your Favorite Pets!", view=RolesPetsView(bot=self.client))
        else:
            await ctx.send_response("```Please go to the 'choose-role' channel to use this command.```", delete_after=10)


def setup(client):
    client.add_cog(RoleManagement(client))
