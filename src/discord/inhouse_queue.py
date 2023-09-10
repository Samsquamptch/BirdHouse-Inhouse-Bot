import discord
import data_management
import check_user
import random
from datetime import datetime


# The modal for admins to kick users from the queue. Full usernames or global nicknames must be used for this to work
class AdminKickPlayerModal(discord.ui.Modal, title='Kick User in Queue'):
    def __init__(self):
        super().__init__()
        self.user_acc = None
        self.user_name = ""

    player_name = discord.ui.TextInput(label='User\'s global name or username', min_length=3)

    async def on_submit(self, interaction: discord.Interaction):
        server = interaction.guild
        self.user_name = str(self.player_name)
        if self.user_name.lower() == "all" or self.user_name == "clear":
            self.user_acc = "clear"
            await interaction.response.defer()
        else:
            check_if_exists = check_user.user_exists(server, self.user_name)
            if check_if_exists[0]:
                self.user_acc = check_if_exists[1]
                await interaction.response.defer()
        self.stop()


# The modal for users to votekick when the queue is full. Will be left for a later date
# class VoteKickPlayerModal(discord.ui.Modal, title='Votekick User in Queue'):
#     def __init__(self):
#         super().__init__()
#         self.user_name = ""
#
#     player_name = discord.ui.TextInput(label='User\'s global name or username')
#
#     async def on_submit(self, interaction: discord.Interaction):
#         self.user_name = str(self.player_name)
#         self.stop()

class WaitingRoom(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.waiting_list = []
        self.channel_id = None
        self.message = None

    async def send_embed(self, server):
        channel = discord.utils.get(server.channels, id=self.channel_id)
        self.message = await channel.send(content="Users in the waiting room are below", view=self)
        await self.update_message()

    def create_embed(self, queue_list):
        if queue_list:
            embed_desc = f"{len(queue_list)} People currently in waiting list"
            embed_clr = 0x00ff00
        else:
            embed_desc = "Waiting list is currently empty"
            embed_clr = 0xFF0000
        queue_embed = discord.Embed(title="Inhouse Waiting List", description=f'{embed_desc}',
                                    color=embed_clr)
        for user in queue_list:
            user_data = data_management.view_user_data(user.id)
            queue_embed.add_field(name=user.global_name, value=f'MMR: {user_data[2]}', inline=True)
        update_time = datetime.now().strftime("%H:%M:%S")
        queue_embed.set_footer(text=f'Waiting list updated at: {update_time}')
        return queue_embed

    async def delete_message(self):
        try:
            await self.message.delete()
        except discord.errors.NotFound:
            pass

    async def update_message(self):
        await self.message.edit(embed=self.create_embed(self.waiting_list), view=self)


# Embed and buttons for the inhouse queue
class InhouseQueue(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.queued_players = []
        self.preload_modal = WaitingRoom()
        self.roles_id = None
        self.channel_id = None
        self.message = None

    async def test_add_user(self, interaction: discord.Interaction):
        server = interaction.guild
        test_list = ["Abfr0", "FaultForce", "Flossine", "FlukeY", "Harry XcX", "Jam!", "Owley", "Teky",
                     "sonnet", "Zetsyuu"]
        for user in test_list:
            check_if_exists = check_user.user_exists(server, user)
            if user not in self.queued_players:
                self.queued_players.append(check_if_exists[1])

    async def send_embed(self, channel, server):
        self.preload_modal.channel_id = self.channel_id
        self.message = await channel.send(view=self)
        await self.update_message(self.queued_players, server)

    def full_queue_embed(self, queue_list, server):
        queue_ids = [user.id for user in queue_list]
        queue_roles = ["Carry", "Midlane", "Offlane", "Soft Supp", "Hard Supp"]
        queue_teams = data_management.team_balancer(queue_ids)
        queue_embed = discord.Embed(title="Inhouse queue", description=f'Queue is full, please join the lobby!',
                                    color=0x00ff00)
        icon_url = server.icon.url
        queue_embed.set_thumbnail(url=f'{icon_url}')
        queue_embed.add_field(name='Roles', value='', inline=True)
        queue_embed.add_field(name='Radiant', value='', inline=True)
        queue_embed.add_field(name='Dire', value='', inline=True)
        coin = random.randint(1, 2)
        if coin == 1:
            radiant_team = queue_teams[0]
            dire_team = queue_teams[1]
        elif coin == 2:
            radiant_team = queue_teams[1]
            dire_team = queue_teams[0]
        x = 0
        mmr_total_radiant = 0
        mmr_total_dire = 0
        while x < 5:
            user_acc_radiant = discord.utils.get(server.members, id=radiant_team[x])
            user_acc_dire = discord.utils.get(server.members, id=dire_team[x])
            user_radiant = data_management.view_user_data(radiant_team[x])
            user_dire = data_management.view_user_data(dire_team[x])
            mmr_total_radiant = mmr_total_radiant + user_radiant[2]
            mmr_total_dire = mmr_total_dire + user_dire[2]
            queue_embed.add_field(name=f'{queue_roles[x]}',
                                  value='\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC',
                                  inline=True)
            queue_embed.add_field(name=user_acc_radiant.global_name,
                                  value=f'MMR: {user_radiant[2]} \u1CBC\u1CBC\u1CBC\u1CBC\u1CBC \n'
                                        f'[Dotabuff](https://www.dotabuff.com/players/{user_radiant[1]})',
                                  inline=True)
            queue_embed.add_field(name=user_acc_dire.global_name,
                                  value=f'MMR: {user_dire[2]} \n'
                                        f'[Dotabuff](https://www.dotabuff.com/players/{user_dire[1]})',
                                  inline=True)
            x += 1
        mmr_avg_radiant = mmr_total_radiant / 5
        mmr_avg_dire = mmr_total_dire / 5
        queue_embed.add_field(name=f'Average MMR', value='', inline=True)
        queue_embed.add_field(name=f'{mmr_avg_radiant}', value='', inline=True)
        queue_embed.add_field(name=f'{mmr_avg_dire}', value='', inline=True)
        update_time = datetime.now().strftime("%H:%M:%S")
        queue_embed.add_field(name='Players',
                              value=f'<@{radiant_team[0]}> <@{radiant_team[1]}> <@{radiant_team[2]}> <@{radiant_team[3]}>'
                                    f'<@{radiant_team[4]}> <@{dire_team[0]}> <@{dire_team[1]}> <@{dire_team[2]}> <@{dire_team[3]}>'
                                    f'<@{dire_team[4]}>')
        queue_embed.set_footer(text=f'Teams created at: {update_time}')
        return queue_embed

    # Creates the embed used for displaying the inhouse queue
    def create_embed(self, queue_list, server):
        if queue_list:
            role_champions = discord.utils.get(server.roles, id=self.roles_id['champions_role'])
            champion_check = any(check in queue_list for check in role_champions.members)
            if champion_check:
                embed_desc = f"A champion is in the queue! {len(queue_list)} players currently in the queue"
                embed_clr = 0xFFD700
            else:
                embed_desc = f"{len(queue_list)} players currently in the queue"
                embed_clr = 0x00ff00
        else:
            embed_desc = "The queue is currently empty. You change that!"
            embed_clr = 0xFF0000
        queue_embed = discord.Embed(title="Inhouse queue", description=f'{embed_desc}',
                                    color=embed_clr)
        icon_url = server.icon.url
        queue_embed.set_thumbnail(url=f'{icon_url}')
        mmr_total = 0
        for user in queue_list:
            user_data = data_management.view_user_data(user.id)
            mmr_total = mmr_total + user_data[2]
            role_preference = check_user.check_role_priority(user_data)
            queue_embed.add_field(name=user.global_name,
                                  value=f'MMR: {user_data[2]} | [Dotabuff](https://www.dotabuff.com/players/{user_data[1]}) | Preference: {role_preference}',
                                  inline=False)
        update_time = datetime.now().strftime("%H:%M:%S")
        if queue_list:
            average_mmr = mmr_total / len(queue_list)
            queue_embed.set_footer(text=f'Queue updated at: {update_time} | Average MMR: {average_mmr}')
        else:
            queue_embed.set_footer(text=f'Queue updated at: {update_time}')
        return queue_embed

    async def update_message(self, queue_list, server):
        if len(queue_list) == 10:
            await self.message.edit(embed=self.full_queue_embed(queue_list, server), view=self)
            await self.preload_modal.send_embed(server)
            # TODO uncomment when going live
            # channel = discord.utils.get(server.channels, id=self.channel_id)
            # await channel.send(f'Queue has popped, can the following users please head to the lobby: \n'
            #                    f'<@{queue_list[0].id}> <@{queue_list[1].id}> <@{queue_list[2].id}>'
            #                    f'<@{queue_list[3].id}> <@{queue_list[4].id}> <@{queue_list[5].id}>'
            #                    f'<@{queue_list[6].id}> <@{queue_list[7].id}> <@{queue_list[8].id}>'
            #                    f'<@{queue_list[9].id}>', delete_after=600)
        else:
            await self.message.edit(embed=self.create_embed(queue_list, server), view=self)

    async def waiting_room_transfer(self, server):
        if not self.queued_players and self.preload_modal.waiting_list:
            for user in self.preload_modal.waiting_list:
                self.queued_players.append(user)
                if len(self.queued_players) == 10:
                    break
            self.preload_modal.waiting_list = [i for i in self.preload_modal.waiting_list if i not in self.queued_players]
            await self.preload_modal.delete_message()
            await self.update_message(self.queued_players, server)
        elif self.preload_modal.waiting_list:
            for user in self.preload_modal.waiting_list:
                self.queued_players.append(user)
                await self.preload_modal.update_message()
                if len(self.queued_players) == 10:
                    break
            self.preload_modal.waiting_list = [i for i in self.preload_modal.waiting_list if i not in self.queued_players]
            await self.preload_modal.delete_message()
            await self.update_message(self.queued_players, server)
        else:
            await self.preload_modal.delete_message()

    # Button to join the inhouse queue
    @discord.ui.button(label="Join Queue", emoji="✅",
                       style=discord.ButtonStyle.green)
    async def join_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        server = interaction.user.guild
        role_verify = discord.utils.get(server.roles, id=self.roles_id['verified_role'])
        role_banned = discord.utils.get(server.roles, id=self.roles_id['banned_role'])
        if role_banned in interaction.user.roles:
            await interaction.response.send_message(content="You are currently banned from joining the queue",
                                                    ephemeral=True, delete_after=5)
        elif role_verify in interaction.user.roles:
            if interaction.user in self.queued_players:
                await interaction.response.send_message(content="You are already queued", ephemeral=True,
                                                        delete_after=5)
            elif len(self.queued_players) == 10 and interaction.user not in self.preload_modal.waiting_list:
                self.preload_modal.waiting_list.append(interaction.user)
                await self.preload_modal.update_message()
                await interaction.response.defer()
            else:
                self.queued_players.append(interaction.user)
                await self.update_message(self.queued_players, server)
                await interaction.response.defer()
        else:
            await interaction.response.send_message(
                content="Please register and wait to be verified to join the queue", ephemeral=True,
                delete_after=5)

    # Button to leave the inhouse queue
    @discord.ui.button(label="Leave Queue", emoji="❌",
                       style=discord.ButtonStyle.red)
    async def leave_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        server = interaction.user.guild
        if interaction.user in self.queued_players:
            if len(self.queued_players) == 10:
                await interaction.response.send_message(content="You cannot leave a full queue!", ephemeral=True,
                                                        delete_after=5)
            else:
                self.queued_players.remove(interaction.user)
                await self.update_message(self.queued_players, server)
                await interaction.response.defer()
        else:
            if len(self.queued_players) == 10 and interaction.user in self.preload_modal.waiting_list:
                self.preload_modal.waiting_list.remove(interaction.user)
                await self.preload_modal.update_message()
                await interaction.response.defer()
            else:
                await interaction.response.send_message(content="You aren't in the queue", ephemeral=True,
                                                        delete_after=5)

    # Button to kick players from the inhouse queue
    @discord.ui.button(label="Kick User", emoji="🥾",
                       style=discord.ButtonStyle.blurple)
    async def kick_from_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        server = interaction.user.guild
        role_admin = discord.utils.get(server.roles, id=self.roles_id['admin_role'])
        if role_admin in interaction.user.roles:
            admin_modal = AdminKickPlayerModal()
            await interaction.response.send_modal(admin_modal)
            await admin_modal.wait()
            if admin_modal.user_acc == "clear":
                self.queued_players.clear()
                await self.update_message(self.queued_players, server)
                await self.waiting_room_transfer(server)
                await interaction.followup.send(content=f'queue has been cleared', ephemeral=True)
            elif admin_modal.user_acc in self.queued_players:
                self.queued_players.remove(admin_modal.user_acc)
                await self.update_message(self.queued_players, server)
                await self.waiting_room_transfer(server)
                await interaction.followup.send(content=f'{admin_modal.user_name} has been kicked from the queue',
                                                ephemeral=True)
            else:
                await interaction.followup.send(content=f'{admin_modal.user_name} isn\'t in the queue', ephemeral=True)
        # # elif len(self.queued_players) == 10 and interaction.user in self.queued_players:
        # elif interaction.user in self.queued_players:
        #     votekick_modal = VoteKickPlayerModal()
        #     await interaction.response.send_modal(votekick_modal)
        #     await votekick_modal.wait()
        #     for user in self.queued_players:
        #         if votekick_modal.user_name in user.global_name:
        #             number = 1
        #             await interaction.channel.send(content=f'{interaction.user.global_name} wants to kick {user.global_name} from the queue! {3 - number} votes left to kick')
        #         # await interaction.followup.send(content=f'{votekick_modal.user_name} isn't in the queue', ephemeral=True)
        # elif len(self.queued_players) < 10 and interaction.user in self.queued_players:
        #     await interaction.response.send_message(content="Votekick can only be held once queue is full", ephemeral=True, delete_after=5)
        # else:
        #     await interaction.response.send_message(content="You can't initiate a votekick if you're not in the queue!", ephemeral=True, delete_after=5)
        else:
            await interaction.response.send_message(
                content="Only admins are able to kick users from the queue (votekick to be added later)",
                ephemeral=True, delete_after=5)

    # @discord.ui.button(label="Add User (test)", emoji="🖥️",
    #                    style=discord.ButtonStyle.blurple)
    # async def add_user_test(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     server = interaction.user.guild
    #     role_admin = discord.utils.get(server.roles, id=self.roles_id['admin_role'])
    #     if role_admin in interaction.user.roles:
    #         await self.test_add_user(interaction)
    #         await self.update_message(self.queued_players, server)
    #         await interaction.response.defer()
