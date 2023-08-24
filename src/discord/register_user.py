import discord
import data_management
import set_roles


class RegisterUserModal(discord.ui.Modal, title='Player Register'):
    dotabuff_url = discord.ui.TextInput(label='Dotabuff User URL')
    player_mmr = discord.ui.TextInput(label='Player MMR')

    async def on_submit(self, interaction: discord.Interaction):
        server = interaction.user.guild
        role = discord.utils.get(server.roles, name="inhouse")
        disc = interaction.user.id
        steam = str(self.dotabuff_url)
        mmr = str(self.player_mmr)
        try:
            int_mmr = int(mmr)
            if "players/" in steam:
                steam = steam.split("players/")
                steam = steam[1]
                player = [disc, steam, int_mmr, 5, 5, 5, 5, 5]
                data_management.add_user_data(player)
                await interaction.user.add_roles(role)
                await interaction.response.send_message(
                    'You\'ve been registered, please set your roles (from top to bottom) and wait to be vouched',
                    view=set_roles.RolePreferenceSelect(), ephemeral=True)
            else:
                await interaction.response.send_message('Please enter your full Dotabuff user url when registering',
                                                        ephemeral=True,
                                                        delete_after=10)
        except ValueError as e:
            print(e)
            await interaction.response.send_message('Please only enter numbers when providing your MMR',
                                                    ephemeral=True,
                                                    delete_after=10)


class RegisterButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Click to register for inhouse", emoji="📋",
                       style=discord.ButtonStyle.green)
    async def register(self, interaction: discord.Interaction, button: discord.ui.Button):
        server = interaction.user.guild
        role = discord.utils.get(server.roles, name="inhouse")
        if role in interaction.user.roles:
            await interaction.response.send_message(content="You are already registered", ephemeral=True,
                                                    delete_after=10)
        else:
            await interaction.response.send_modal(RegisterUserModal())
