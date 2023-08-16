import discord
from discord.ext import commands
import yaml
from yaml.loader import SafeLoader

class VerifyUserModal(discord.ui.Modal, title='Verify Registered User'):
    player_name = discord.ui.TextInput(label='User\'s name')
    verify_user = discord.ui.TextInput(label='Verify user?', max_length=1, placeholder='y/n')

    async def on_submit(self, interaction: discord.Interaction):
        #this check isn't working, not sure why
        print(self.verify_user)
        if self.verify_user == "y" or "Y":
            await interaction.response.send_message(f'User {self.player_name} has been vouched', ephemeral=True,
                                                    delete_after=10)
        else:
            await interaction.response.send_message(f'User {self.player_name} has not been vouched', ephemeral=True,
                                                    delete_after=10)


class EditUserModal(discord.ui.Modal, title='Edit Registered User'):
    player_name = discord.ui.TextInput(label='User\'s name')
    set_mmr = discord.ui.TextInput(label='Set new MMR for user?', max_length=4, required=False)
    remove_verify_role = discord.ui.TextInput(label='Remove verification from user?', max_length=1, required=False)
    ban_user = discord.ui.TextInput(label='Ban user duration? (number = days banned)', max_length=2, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Details for user {self.player_name} have been updated',
                                                ephemeral=True, delete_after=10)


class ViewUsersModal(discord.ui.Modal, title='View Users'):
    player_name = discord.ui.TextInput(label='User\'s name (use "all" for full list)')

    async def on_submit(self, interaction: discord.Interaction):
        if self.player_name == "all":
            #for i in CSV file
            await interaction.response.send_message('Showing all registered users', ephemeral=True, delete_after=10)
        else:
            print(self.player_name)
            #player_id = discord.utils.get(user.id, nick=self.player_name)
            await interaction.response.send_message(f'Showing user {self.player_name} details', ephemeral=True,
                                                delete_after=10)


class RemoveUserModal(discord.ui.Modal, title='Delete User from Database'):
    player_name = discord.ui.TextInput(label='User\'s name')
    confirm_deletion = discord.ui.TextInput(label='Confirm deletion?', max_length=1, placeholder='y/n')

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'User {self.player_name} has been deleted', ephemeral=True,
                                                delete_after=10)


class RegisterUserModal(discord.ui.Modal, title='Player Register'):
    steam_id = discord.ui.TextInput(label='Dotabuff/Steam ID')
    player_mmr = discord.ui.TextInput(label='Player MMR')

    async def on_submit(self, interaction: discord.Interaction):
        #the values which need to be parsed into CSV
        print(interaction.user.id)
        print(self.steam_id)
        print(self.player_mmr)
        await interaction.response.send_message('You\'ve been registered, please wait to be vouched', ephemeral=True,
                                                delete_after=10)


class RoleSelectModal(discord.ui.Modal, title='Set Player Roles'):
    pos_1 = discord.ui.TextInput(label='Carry preference', max_length=1)
    pos_2 = discord.ui.TextInput(label='Midlane preference', max_length=1)
    pos_3 = discord.ui.TextInput(label='Offlane preference', max_length=1)
    pos_4 = discord.ui.TextInput(label='Support preference', max_length=1)
    pos_5 = discord.ui.TextInput(label='Hard Support preference', max_length=1)

    async def on_submit(self, interaction: discord.Interaction):
        #the values which need to be parsed into CSV
        print(self.pos_1)
        print(self.pos_2)
        print(self.pos_3)
        print(self.pos_4)
        print(self.pos_5)
        await interaction.response.send_message('Thank you for updating your role preferences', ephemeral=True,
                                                delete_after=10)


class PlayerViewModal(discord.ui.Modal, title='View Player '):
    player_name = discord.ui.TextInput(label='Player name')

    async def on_submit(self, interaction: discord.Interaction):
        #player_id = discord.utils.get(user.id, nick=self.player_name)
        await interaction.response.send_message(f'Looking for user {self.player_name}', ephemeral=True, delete_after=10)


class AdminChoices(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(placeholder="Select an action here", min_values=1, max_values=1, options=[
        discord.SelectOption(label="Verify", emoji="✅", description="Verify a registered user"),
        discord.SelectOption(label="Edit", emoji="🖊️", description="Edit a user's details and status"),
        discord.SelectOption(label="View", emoji="👀", description="View all registered or a specific user"),
        discord.SelectOption(label="Remove", emoji="❌", description="Delete a registered user"),
        discord.SelectOption(label="Refresh", emoji="♻", description="Select to allow you to refresh options")
    ]
                       )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        match select.values[0]:
            case "Verify":
                await interaction.response.send_modal(VerifyUserModal())
            case "Edit":
                await interaction.response.send_modal(EditUserModal())
            case "View":
                await interaction.response.send_modal(ViewUsersModal())
            case "Remove":
                await interaction.response.send_modal(RemoveUserModal())
            case "Refresh":
                await interaction.response.defer()


class UserChoices(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(placeholder="Select an action here", min_values=1, max_values=1, options=[
        discord.SelectOption(label="Register", emoji="📋", description="Register for the inhouse bot"),
        discord.SelectOption(label="Roles", emoji="🖊️", description="Update what your role preferences are"),
        discord.SelectOption(label="Players", emoji="👀", description="View a player based on their name or steam ID"),
        discord.SelectOption(label="Refresh", emoji="♻", description="Select to allow you to refresh options")
    ]
                       )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        match select.values[0]:
            case "Register":
                await interaction.response.send_modal(RegisterUserModal())
            case "Roles":
                await interaction.response.send_modal(RoleSelectModal())
            case "Players":
                await interaction.response.send_modal(PlayerViewModal())
            case "Refresh":
                await interaction.response.defer()


def load_token():
    with open('../../credentials/discord_token.yml') as f:
        data = yaml.load(f, Loader=SafeLoader)
    return data['TOKEN']


def run_discord_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print('bot now running!')

    @bot.command()
    async def options(ctx):
        await ctx.send("Please choose an option below", view=UserChoices())

    @bot.command()
    async def admin(ctx):
        await ctx.send("Admin options are below", view=AdminChoices())

    @bot.command()
    async def clear(ctx):
        await ctx.channel.purge()


    bot.run(load_token())


if __name__ == '__main__':
    run_discord_bot()
