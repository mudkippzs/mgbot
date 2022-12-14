import json
from discord.ext import commands


class ExportRoles(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(name='exportroles', description='Export the current set of roles to a dictionary.')
    @commands.has_role('Admin')
    async def export_roles(self, ctx):
        """Exports all roles to a JSON file called roles.json."""
        
        # Create a dictionary to store the role data in.
        role_data = {}

        # Iterate over the guild's roles and add them to the dictionary.
        for role in ctx.guild.roles:
            role_data[str(role.id)] = role.name

        # Write the data to a JSON file.
        with open("roles.json", "w") as f:
            json.dump(role_data, f)


        # Send a message to the channel to let the user know that it is done.
        await ctx.send_response("Done.")


def setup(client):
    client.add_cog(ExportRoles(client))