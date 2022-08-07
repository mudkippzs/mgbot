import discord

class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="help", aliases=["h"])
    async def help(self, ctx):
        """
        Displays a list of commands and their descriptions.
        """
        embed = discord.Embed(title="Help", description="List of commands and their descriptions.", color=0x00ff00)
        embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

        for command in self.client.commands:
            if command.hidden:
                continue
            embed.add_field(name=f"{command.name}", value=f"{command.help}", inline=False)
        
        await ctx.send(embed=embed)

    # @commands.Cog.listener()
    # async def on_ready(self):
    # """Client Even - on_ready: triggers when Client is logged in and listening for events."""
    #     clogger(f"Help loaded!")

def setup(client):
    client.add_cog(Help(client))