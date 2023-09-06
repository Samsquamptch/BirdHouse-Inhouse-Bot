import discord
import yaml
from yaml.loader import SafeLoader


def update_config(interaction, category, sub_category, new_value):
    with open(f'../../data/{interaction.guild.id}_config.yml') as f:
        data = yaml.load(f, Loader=SafeLoader)
    data[category][sub_category] = new_value
    with open(f'../../data/{interaction.guild.id}_config.yml', 'w') as f:
        yaml.dump(data, f)


class SetRolesModal(discord.ui.Modal, title='User Roles Configuration'):
    def __init__(self):
        super().__init__(timeout=None)

    admin_role = discord.ui.TextInput(label='Set admin role')
    inhouse_role = discord.ui.TextInput(label='Set inhouse role')
    verified_role = discord.ui.TextInput(label='Set verified role')
    banned_role = discord.ui.TextInput(label='Set banned role')
    champions_role = discord.ui.TextInput(label='Set champions role')

    async def on_submit(self, interaction: discord.Interaction):
        admin_str = str(self.admin_role)
        inhouse_str = str(self.inhouse_role)
        verified_str = str(self.verified_role)
        banned_str = str(self.banned_role)
        champions_str = str(self.champions_role)
        roles_dict = {'admin_role': admin_str, 'registered_role': inhouse_str, 'verified_role': verified_str,
                        'champions_role': champions_str, 'banned_role': banned_str}
        role_list = [admin_str, inhouse_str, verified_str, banned_str, champions_str]
        premade_roles = []
        for role in roles_dict:
            check_user = discord.utils.get(interaction.guild.roles, name=roles_dict[role])
            if not check_user:
                await interaction.guild.create_role(name=roles_dict[role])
                check_user = discord.utils.get(interaction.guild.roles, name=roles_dict[role])
            else:
              premade_roles.append(roles_dict[role])
            update_config(interaction, 'ROLES', role, check_user.id)
        yes_no = YesNoButtons()
        yes_no.config_user = interaction.user
        yes_no.setup_position = 4
        yes_no.clear_channel_list = [i for i in role_list if i not in premade_roles]
        await interaction.response.send_message(
            f'You\'ve created the following roles: \n'
            f'{role_list[0]} \n {role_list[1]} \n {role_list[2]} \n {role_list[3]} \n {role_list[4]} \n'
            f'Do you wish to keep these?', view=yes_no)


class SetupChannelsModal(discord.ui.Modal, title='Text Channels Configuration'):
    def __init__(self):
        super().__init__(timeout=None)

    inhouse_category = discord.ui.TextInput(label='Set inhouse channel category')
    admin_channel = discord.ui.TextInput(label='Set admin channel')
    queue_channel = discord.ui.TextInput(label='Set queue channel')
    notif_channel = discord.ui.TextInput(label='Set notification channel')
    chat_channel = discord.ui.TextInput(label='Set chat channel')

    async def on_submit(self, interaction: discord.Interaction):
        cat_str = str(self.inhouse_category)
        admin_str = str(self.admin_channel)
        queue_str = str(self.queue_channel)
        notif_str = str(self.notif_channel)
        chat_channel = str(self.chat_channel)
        channel_dict = {'admin_channel': admin_str, 'queue_channel': queue_str, 'notification_channel': notif_str,
                        'chat_channel': chat_channel}
        channel_list = [admin_str, queue_str, notif_str, chat_channel]
        check_categ = discord.utils.get(interaction.guild.categories, name=cat_str)
        if not check_categ:
            await interaction.guild.create_category(name=cat_str)
            check_categ = discord.utils.get(interaction.guild.categories, name=cat_str)
        update_config(interaction, 'CHANNELS', 'inhouse_category', check_categ.id)
        set_category = discord.utils.get(interaction.guild.categories, name=cat_str)
        premade_channels = []
        for channel in channel_dict:
            check_chann = discord.utils.get(set_category.text_channels, name=channel_dict[channel])
            if not check_chann:
                match channel:
                    case 'admin_channel':
                        overwrites = {
                            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                            interaction.guild.me: discord.PermissionOverwrite(read_messages=True)
                        }
                    case 'queue_channel' | 'notification_channel':
                        overwrites = {
                            interaction.guild.default_role: discord.PermissionOverwrite(send_messages=False),
                            interaction.guild.me: discord.PermissionOverwrite(send_messages=True)
                        }
                    case _:
                        overwrites = {
                            interaction.guild.me: discord.PermissionOverwrite(send_messages=True)
                        }
                await interaction.guild.create_text_channel(name=channel_dict[channel], category=set_category, overwrites=overwrites)
                check_chann = discord.utils.get(set_category.text_channels, name=channel_dict[channel])
            else:
                premade_channels.append(channel_dict[channel])
            update_config(interaction, 'CHANNELS', channel, check_chann.id)
        yes_no = YesNoButtons()
        yes_no.config_user = interaction.user
        yes_no.setup_position = 3
        yes_no.category = set_category
        yes_no.clear_channel_list = [i for i in channel_list if i not in premade_channels]
        await interaction.response.send_message(
            f'You\'ve created the category {cat_str} with the channels: \n'
            f'{channel_list[0]} \n {channel_list[1]} \n {channel_list[2]} \n {channel_list[3]} \n'
            f'Do you wish to keep these?', view=yes_no)


class VoiceChannelButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.voice_category = None
        self.config_user = None

    @discord.ui.button(label="Yes", emoji="👍",
                       style=discord.ButtonStyle.green)
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.config_user:
            channel_list = ["Casting Channel", "Waiting Room", "Radiant Voice", "Dire Voice"]
            for channel in channel_list:
                check_chann = discord.utils.get(self.voice_category.voice_channels, name=channel)
                if not check_chann:
                    await interaction.guild.create_voice_channel(name=channel, category=self.voice_category)
            await interaction.response.send_modal(SetRolesModal())
            await interaction.message.delete()
        else:
            await interaction.response.defer()

    @discord.ui.button(label="No", emoji="👎",
                       style=discord.ButtonStyle.green)
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.config_user:
            await interaction.response.send_modal(SetRolesModal())
            await interaction.message.delete()
        else:
            await interaction.response.defer()

class YesNoButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.setup_position = 0
        self.config_user = None
        self.category = None
        self.clear_list = []

    @discord.ui.button(label="Yes", emoji="👍",
                       style=discord.ButtonStyle.green)
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.config_user:
            match self.setup_position:
                case 1:
                    await interaction.response.send_message(content="Proceeding with automated setup")
                case 2:
                    await interaction.response.send_modal(SetupChannelsModal())
                case 3:
                    voice_buttons = VoiceChannelButtons()
                    voice_buttons.config_user = interaction.user
                    voice_buttons.voice_category = self.category
                    await interaction.response.send_message("Do you want to add voice channels?", view=voice_buttons)
        else:
            await interaction.response.defer()
        await interaction.message.delete()

    @discord.ui.button(label="No", emoji="👎",
                       style=discord.ButtonStyle.green)
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        match self.setup_position:
            case 1 | 2:
                self.setup_position = 0
                await interaction.response.defer()
            case 3:
                if self.clear_list:
                    for channel in self.clear_list:
                        del_channel = discord.utils.get(interaction.guild.channels, name=channel)
                        await del_channel.delete(reason="inhouse bot instructed")
                await interaction.response.send_modal(SetupChannelsModal())
            case 4:
                if self.clear_list:
                    for role in self.clear_list:
                        del_role = discord.utils.get(interaction.guild.roles, name=role)
                        await del_role.delete(reason="inhouse bot instructed")
                await interaction.response.send_modal(SetRolesModal())
        await interaction.message.delete()
        self.stop()


class ConfigButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        with open("../../data/setup.txt", "r") as setup:
            self.setup_guide = setup.read().split("\n\n")

    async def config_start(self, ctx):
        self.config_user = ctx.author
        self.message = await ctx.channel.send(self.setup_guide[0], view=self)

    async def select_option(self, channel):
        self.message = await channel.send(content="", view=self)

    async def update_buttons(self, num=0):
        if num == 0:
            self.auto_setup.disabled = False
            self.manual_setup.disabled = False
        else:
            self.auto_setup.disabled = True
            self.manual_setup.disabled = True
        await self.message.edit(view=self)

    @discord.ui.button(label="Automated Setup", emoji="🤖",
                       style=discord.ButtonStyle.green)
    async def auto_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.config_user:
            yes_no_view = YesNoButtons()
            yes_no_view.setup_position = 1
            yes_no_view.config_user = self.config_user
            await self.update_buttons(yes_no_view.setup_position)
            await interaction.response.send_message(content="Automated setup was selected. Confirm?", view=yes_no_view)
            await yes_no_view.wait()
            if yes_no_view.setup_position == 0:
                await self.update_buttons(yes_no_view.setup_position)
                await interaction.response.defer()
            else:
                await interaction.response.defer()
        else:
            await interaction.response.defer()

    @discord.ui.button(label="Manual Setup", emoji="👨‍💻",
                       style=discord.ButtonStyle.green)
    async def manual_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.config_user:
            yes_no_view = YesNoButtons()
            yes_no_view.setup_position = 2
            yes_no_view.config_user = self.config_user
            await self.update_buttons(yes_no_view.setup_position)
            await interaction.response.send_message(content="Manual setup was selected. Confirm?", view=yes_no_view)
            await yes_no_view.wait()
            if yes_no_view.setup_position == 0:
                await self.update_buttons(yes_no_view.setup_position)
                await interaction.response.defer()
            else:
                await interaction.response.defer()
        else:
            await interaction.response.defer()
