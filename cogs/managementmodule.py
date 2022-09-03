import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ui import View, Item, Button, Select
import sys
import os
import requests
from io import BytesIO
from PIL import Image 
from PIL.PngImagePlugin import PngImageFile
from PIL.JpegImagePlugin import JpegImageFile

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '.')))

from clogger import clogger

class ManagementModule(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command()
    @commands.has_role('Admin')
    async def nicknameupdate(self, ctx, new_nickname):
        """This command will allow the Admin to update the bot's nickname"""

        await ctx.guild.me.edit(nick=new_nickname)

        await ctx.send_response(f"{ctx.author.mention} Nickname updated")

    @commands.slash_command()
    @commands.has_role('Admin')
    async def avatarupdate(self, ctx, file_or_url):
        """
        This command will allow the Admin to update the bot's avatar"""

        if isinstance(file_or_url, PngImageFile) is False and isinstance(file_or_url, JpegImageFile) is False:
            response = requests.get('https://cdn.discordapp.com/attachments/823656840701149194/1009932579065053324/mg_logo.png')
            with open('tempimg', 'wb') as stream:
                stream.write(response.content)

            with open('tempimg', 'rb') as stream:
                img = stream.read()                
                await self.client.user.edit(avatar=img)

            os.remove('tempimg')

        else:
            with open(file_or_url, 'rb') as f:
                data = f.read()
                await self.client.user.edit(avatar=data)

        await ctx.send_response(f"{ctx.author.mention} Avatar updated")
        
def setup(client):
    client.add_cog(ManagementModule(client))