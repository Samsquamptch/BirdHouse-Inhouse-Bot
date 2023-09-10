import discord
import data_management

register_list = []

def user_embed(data_list, player_data, server):
    roles_id = data_management.load_config_data(server, 'ROLES')
    role_verified = discord.utils.get(server.roles, id=roles_id['verified_role'])
    role_banned = discord.utils.get(server.roles, id=roles_id['banned_role'])
    role_champion = discord.utils.get(server.roles, id=roles_id['champions_role'])
    if role_banned in player_data.roles:
        user_status = "User is currently banned 😢"
        user_clr = 0x000000
    elif role_champion in player_data.roles:
        user_status = "User is a champion!"
        user_clr = 0xFFD700
    elif role_verified in player_data.roles:
        user_status = "User is verified"
        user_clr = 0x00ff00
    else:
        user_status = "User is not verified"
        user_clr = 0xFF0000
    # Due to how the role balancer calculations work, number weighting is saved the opposite to how users are used to
    # (which is higher number = more pref and lower number = less pref). This swap shows what users expect to see,
    # instead of what is actually happening behind the scenes (low num = more pref and high num = less pref)
    data_numbers = [3, 4, 5, 6, 7]
    for n in data_numbers:
        match data_list[n]:
            case 1:
                data_list[n] = 5
            case 2:
                data_list[n] = 4
            case 3:
                data_list[n] = 3
            case 4:
                data_list[n] = 2
            case 5:
                data_list[n] = 1
    view_user_embed = discord.Embed(title=f'{player_data.global_name}', description=f'{user_status}',
                                    color=user_clr)
    if player_data.avatar != None:
        view_user_embed.set_thumbnail(url=f'{player_data.avatar}')
    view_user_embed.add_field(name='Dotabuff',
                              value=f'[{data_list[1]}](https://www.dotabuff.com/players/{data_list[1]})'
                                    f'\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC', inline=True)
    view_user_embed.add_field(name='MMR', value=f'{data_list[2]} \u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC',
                              inline=True)
    view_user_embed.add_field(name='Rank', value=f'N/A \u1CBC\u1CBC\u1CBC\u1CBC', inline=True)
    view_user_embed.add_field(name='Matches', value=f'0', inline=True)
    view_user_embed.add_field(name='Wins', value=f'0', inline=True)
    view_user_embed.add_field(name='Losses', value=f'0', inline=True)
    view_user_embed.add_field(name='Role Preferences', value='', inline=False)
    view_user_embed.add_field(name='Carry', value=f'{data_list[3]}', inline=False)
    view_user_embed.add_field(name='Midlane', value=f'{data_list[4]}', inline=False)
    view_user_embed.add_field(name='Offlane', value=f'{data_list[5]}', inline=False)
    view_user_embed.add_field(name='Soft Support', value=f'{data_list[6]}', inline=False)
    view_user_embed.add_field(name='Hard Support', value=f'{data_list[7]}', inline=False)
    return view_user_embed


def user_exists(server, user_name):
    try:
        user_account = discord.utils.get(server.members, global_name=user_name)
        if user_account is None:
            user_account = discord.utils.get(server.members, name=user_name)
        user_in_database = data_management.check_for_value(user_account.id)
    except AttributeError:
        user_in_database = False
        user_account = None
    return user_in_database, user_account


# For checking whether details for users are already stored on the database
def registered_check(check_id):
    test = data_management.check_for_value(check_id)
    if test:
        already_exists = True
    else:
        already_exists = False
    return already_exists


def check_role_priority(user):
    core_roles = [user[3], user[4], user[5]]
    supp_roles = [user[6], user[7]]
    if 1 in core_roles and 1 not in supp_roles:
        role_pref = "Core"
    elif 1 in supp_roles and 1 not in core_roles:
        role_pref = "Support"
    else:
        core_avg = (user[3] + user[4] + user[5]) / 3
        supp_avg = (user[6] + user[7]) / 2
        role_balance = core_avg - supp_avg
        match role_balance:
            case _ if role_balance > 1:
                role_pref = "Support"
            case _ if role_balance < 0:
                role_pref = "Core"
            case _:
                role_pref = "Balanced"
    return role_pref


def user_list(list_condition, user=None):
    global register_list
    match list_condition:
        case "Add":
            register_list.append(user)
        case "Remove":
            register_list.remove(user)
        case _:
            pass
    return register_list
