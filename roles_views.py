import discord
from discord.ext import commands
from discord.ui import View, Select

from clogger import clogger
from utils import *


ROLE_DICT = {
    "europe": ('Europe', '#89CFF0'),
    "n_america": ('N. America', '#89CFF0'),
    "s_america": ('S. America', '#89CFF0'),
    "asia": ('Asia', '#89CFF0'),
    "africa": ('Africa', '#89CFF0'),
    "australia": ('Australia', '#89CFF0'),
    "gaming": ("Gamer", "#A0522D"),
    "ttrpg": ("RPG Nerd", "#A0522D"),
    "tv": ("Couch Potato", "#A0522D"),
    "art": ("Artist", "#A0522D"),
    "writer": ("Writer", "#A0522D"),
    "programmer": ("Coding", "#A0522D"),
    "math": ("Mathologist", "#A0522D"),
    "history": ("History Buff", "#A0522D"),
    "politics": ("Armchair Political Analyst", "#A0522D"),
    "sports": ("Sports Fan", "#A0522D"),
    "dogs": ("Dogs", "#00a6ec"),
    "cat": ("Cats", "#f05fd2"),
    "bird": ("Birds", "#EEE800"),
    "reptile": ("Reptiles", "#96f35a")
}


# the function called when the user is done selecting options
async def role_manager(select, interaction, bot):
    await interaction.response.defer()

    config = load_json_config("config.json")

    try:
        for guild in bot.guilds:
            channel = guild.get_channel(
                config["guilds"][str(guild.id)]["choose_roles"])
            roles = [r for r in guild.roles if r.name in select.values]
            member = guild.get_member(interaction.user.id)

            for role in roles:
                # Check if the user has the role already.
                if role in member.roles:
                    # Remove the role from the user's profile.
                    await member.remove_roles(role)
                    await interaction.followup.send(f"Removed {role} from your profile.", ephemeral=True)
                else:
                    # Add the role to the user's profile.
                    await member.add_roles(role)
                    await interaction.followup.send(f"Added {role} to your profile.", ephemeral=True)
    except Exception as e:
        pass


class RolesLocationView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.select(  # the decorator that lets you specify the properties of the select menu
        # the placeholder text that will be displayed if nothing is selected
        placeholder="Choose your Location!",
        custom_id="location-select",
        min_values=0,  # the minimum number of values that must be selected by the users
        max_values=1,  # the maxmimum number of values that can be selected by the users
        options=[  # the list of options from which users can choose, a required field
            discord.SelectOption(
                label="Europe",
                description="From Europe",
                emoji="🌍"
            ),
            discord.SelectOption(
                label="North America",
                description="From North America",
                emoji="🌎"
            ),
            discord.SelectOption(
                label="South America",
                description="From South America",
                emoji="🌎"
            ),
            discord.SelectOption(
                label="Australia",
                description="From Australia",
                emoji="🌏"
            ),
            discord.SelectOption(
                label="Asia",
                description="From Asia",
                emoji="🌏"
            ),
            discord.SelectOption(
                label="Africa",
                description="From Africa",
                emoji="🌍"
            )
        ]
    )
    # the function called when the user is done selecting options
    async def select_callback(self, select, interaction):
        r = await role_manager(select, interaction, self.bot)


class RolesSexView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.select(  # the decorator that lets you specify the properties of the select menu
        # the placeholder text that will be displayed if nothing is selected
        placeholder="Choose your Sex!",
        custom_id="sex-select",
        min_values=0,  # the minimum number of values that must be selected by the users
        max_values=1,  # the maxmimum number of values that can be selected by the users
        options=[  # the list of options from which users can choose, a required field
            discord.SelectOption(
                label="Male",
                description="Adult Human Male.",
                emoji="♂️"
            ),
            discord.SelectOption(
                label="Female",
                description="Adult Human Female",
                emoji="♀️"
            )
        ]
    )
    # the function called when the user is done selecting options
    async def select_callback(self, select, interaction):
        r = await role_manager(select, interaction, self.bot)


class RolesInterestsView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.select(  # the decorator that lets you specify the properties of the select menu
        # the placeholder text that will be displayed if nothing is selected
        placeholder="Choose your Server Alerts!",
        custom_id="interest-select",
        min_values=0,  # the minimum number of values that must be selected by the users
        max_values=10,  # the maxmimum number of values that can be selected by the users
        options=[  # the list of options from which users can choose, a required field
            discord.SelectOption(
                label="Gamer",
                description="Get notified about Gaming streams, discussions or events!",
                emoji="🎮"
            ),
            discord.SelectOption(
                label="RPG Nerd",
                description="Get notified about getting involved with our RPG club!",
                emoji="🧙"
            ),
            discord.SelectOption(
                label="Couch Potato",
                description="Get notified about film/documentary/tv streaming partys!!",
                emoji="📺"
            ),
            discord.SelectOption(
                label="Artist",
                description="Get notified about Art stuff!",
                emoji="🎨"
            ),
            discord.SelectOption(
                label="Writer",
                description="Get notified about Writing stuff!",
                emoji="✒️"
            ),
            discord.SelectOption(
                label="Coding",
                description="Get notified about Coding stuff!",
                emoji="💻"
            ),
            discord.SelectOption(
                label="Mathologist",
                description="Get notified about Mathology stuff!",
                emoji="🧮"
            ),
            discord.SelectOption(
                label="History Buff",
                description="Get notified about History Buff stuff!",
                emoji="📜"
            ),
            discord.SelectOption(
                label="Armchair Political Analyst",
                description="Get notified about discussions on Politics!",
                emoji="🌐"
            ),
            discord.SelectOption(
                label="Sports Fan",
                description="Get notified about Sports Fan stuff!",
                emoji="⚽"
            )
        ]
    )
    # the function called when the user is done selecting options
    async def select_callback(self, select, interaction):
        r = await role_manager(select, interaction, self.bot)


class RolesPetsView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.select(  # the decorator that lets you specify the properties of the select menu
        # the placeholder text that will be displayed if nothing is selected
        placeholder="Choose your favorite Pets!",
        custom_id="pets-select",
        min_values=0,  # the minimum number of values that must be selected by the users
        max_values=3,  # the maxmimum number of values that can be selected by the users
        options=[  # the list of options from which users can choose, a required field
            discord.SelectOption(
                label="Cats",
                description=":woozy_face:!",
                emoji="🐱"
            ),
            discord.SelectOption(
                label="Dogs",
                description=":relieved:!",
                emoji="🐶"
            ),
            discord.SelectOption(
                label="Birds",
                description="Got birds? Prove it!",
                emoji="🦆"
            ),
            discord.SelectOption(
                label="Reptiles",
                description="Pick this if you have a snake, turtle or other scaley bud!",
                emoji="🐍"
            )
        ]
    )
    # the function called when the user is done selecting options
    async def select_callback(self, select, interaction):
        if len(select.values) > 0:
            r = await role_manager(select, interaction, self.bot)

class RolesVirtueView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.select(  # the decorator that lets you specify the properties of the select menu
        # the placeholder text that will be displayed if nothing is selected
        placeholder="Choose your Virtues!",
        custom_id="virtue-select",
        min_values=0,  # the minimum number of values that must be selected by the users
        max_values=4,  # the maxmimum number of values that can be selected by the users
        options=[  # the list of options from which users can choose, a required field
            discord.SelectOption(
                label="No Fags",
                description="I've quit smoking!",
                emoji="🚭"
            ),
            discord.SelectOption(
                label="Born-Again Teetotaller",
                description=":relieved:! I've quit (regular) drinking!",
                emoji="🚱"
            ),
            discord.SelectOption(
                label="Keeping Fit",
                description="Biking, Climbing, Trail Mix - Its all good!",
                emoji="🧗"
            ),
            discord.SelectOption(
                label="Volunteer",
                description="Wana inspire others to volunteer? They're certainly going to ask if you have this!",
                emoji="🦧"
            )
        ]
    )
    # the function called when the user is done selecting options
    async def select_callback(self, select, interaction):
        if len(select.values) > 0:
            r = await role_manager(select, interaction, self.bot)
