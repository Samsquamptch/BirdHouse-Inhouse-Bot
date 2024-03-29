import pandas as pd
import team_balancer
import sqlite3
import yaml
import random
from datetime import datetime
from yaml.loader import SafeLoader
import networkx as nx
from networkx.algorithms import bipartite


def load_token():
    with open('../../credentials/discord_token.yml') as f:
        data = yaml.load(f, Loader=SafeLoader)
    return data['TOKEN']


def load_default_config(category):
    with open('../../data/default_config.yml') as f:
        data = yaml.load(f, Loader=SafeLoader)
    return data[category]


def load_config_data(server, category, sub_category=None):
    with open(f'../../data/{server.id}_config.yml') as f:
        data = yaml.load(f, Loader=SafeLoader)
    if sub_category is None:
        return data[category]
    else:
        return data[category][sub_category]


def update_config(server, category, sub_category, new_value):
    with open(f'../../data/{server.id}_config.yml') as f:
        data = yaml.load(f, Loader=SafeLoader)
    data[category][sub_category] = new_value
    with open(f'../../data/{server.id}_config.yml', 'w') as f:
        yaml.dump(data, f)


def initialise_database(server):
    conn = sqlite3.connect(f'../../data/inhouse_{server.id}.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS Users(disc INTEGER PRIMARY KEY, steam INTEGER, mmr INTEGER, 
                pos1 INTEGER, pos2 INTEGER, pos3 INTEGER, pos4 INTEGER, pos5 INTEGER, last_updated timestamp)""")
    cur.close()
    print("Database created successfully")


def update_user_data(discord_id, column, new_data, server):
    conn = sqlite3.connect(f'../../data/inhouse_{server.id}.db')
    cur = conn.cursor()
    if column == "roles":
        new_data.append(discord_id)
        cur.execute("UPDATE Users SET pos1 = ?, pos2 = ?, pos3 = ?, pos4 = ?, pos5 = ? WHERE disc=?", new_data)
    else:
        cur.execute(f"UPDATE Users SET {column} = ? WHERE disc = ?", [new_data, discord_id])
    conn.commit()
    cur.close()


def check_for_value(column, value_check, server):
    conn = sqlite3.connect(f'../../data/inhouse_{server.id}.db')
    cur = conn.cursor()
    cur.execute(f"SELECT EXISTS(SELECT 1 FROM Users WHERE {column} = ?)", [value_check])
    item = cur.fetchone()[0]
    if item == 0:
        variable = False
    else:
        variable = True
    conn.close()
    return variable


def view_user_data(discord_id, server):
    conn = sqlite3.connect(f'../../data/inhouse_{server.id}.db')
    cur = conn.cursor()
    user_data_list = list(cur.execute("SELECT * from Users WHERE disc=?", [discord_id]))
    return list(user_data_list[0])


def add_user_data(player, server):
    player.append(datetime.today().strftime('%Y-%m-%d'))
    conn = sqlite3.connect(f'../../data/inhouse_{server.id}.db')
    cur = conn.cursor()
    cur.execute("""INSERT INTO Users (disc, steam, mmr, pos1, pos2, pos3, pos4, pos5, last_updated) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", player)
    conn.commit()
    conn.close()


def remove_user_data(discord_id, server):
    conn = sqlite3.connect(f'../../data/inhouse_{server.id}.db')
    cur = conn.cursor()
    cur.execute("""DELETE FROM Users where disc=?""", [discord_id])
    conn.commit()
    conn.close()


def assign_teams(queue_ids, server):
    id_tuple = tuple(queue_ids)
    conn = sqlite3.connect(f'../../data/inhouse_{server.id}.db')
    user_data = pd.read_sql_query("SELECT * FROM Users WHERE disc IN {};".format(id_tuple), conn)
    queue = user_data.sort_values('mmr', ascending=False)
    team_uno = team_balancer.sort_balancer(queue['mmr'].tolist())
    team_dos = team_balancer.mean_balancer(queue['mmr'].tolist())
    team_tres = team_balancer.draft_balancer(queue['mmr'].tolist())
    queue["team_uno"] = team_uno
    queue["team_dos"] = team_dos
    queue["team_tres"] = team_tres
    delta1 = abs(queue.loc[queue['team_uno'] == "Team 1", 'mmr'].mean() - queue.loc[
        queue['team_uno'] == "Team 2", 'mmr'].mean())
    delta2 = abs(queue.loc[queue['team_dos'] == "Team 1", 'mmr'].mean() - queue.loc[
        queue['team_dos'] == "Team 2", 'mmr'].mean())
    delta3 = abs(queue.loc[queue['team_tres'] == "Team 1", 'mmr'].mean() - queue.loc[
        queue['team_tres'] == "Team 2", 'mmr'].mean())
    delta_list = [delta1, delta2, delta3]
    allowed_range = 100
    delta_choices = []
    while not delta_choices:
        delta_choices = [i for i in delta_list if i < allowed_range]
        allowed_range += 50
    print(delta_list)
    print(delta_choices)
    random_delta = random.choice(delta_choices)
    print(random_delta)
    if random_delta == delta1:
        queue = queue.drop(columns="team_dos")
        queue = queue.drop(columns="team_tres")
        queue = queue.rename(columns={"team_uno": "team"})
    elif random_delta == delta2:
        queue = queue.drop(columns="team_uno")
        queue = queue.drop(columns="team_tres")
        queue = queue.rename(columns={"team_dos": "team"})
    else:
        queue = queue.drop(columns="team_uno")
        queue = queue.drop(columns="team_dos")
        queue = queue.rename(columns={"team_tres": "team"})
    team1 = queue.loc[queue['team'] == "Team 1"]
    team2 = queue.loc[queue['team'] == "Team 2"]
    pos1 = role_allocation(team1)
    team1["pos"] = [11, 12, 13, 14, 15]
    team1.at[pos1[5001], 'pos'] = 1
    team1.at[pos1[5002], 'pos'] = 2
    team1.at[pos1[5003], 'pos'] = 3
    team1.at[pos1[5004], 'pos'] = 4
    team1.at[pos1[5005], 'pos'] = 5
    team1 = team1.sort_values('pos')
    pos2 = role_allocation(team2)
    team2["pos"] = [11, 12, 13, 14, 15]
    team2.at[pos2[5001], 'pos'] = 1
    team2.at[pos2[5002], 'pos'] = 2
    team2.at[pos2[5003], 'pos'] = 3
    team2.at[pos2[5004], 'pos'] = 4
    team2.at[pos2[5005], 'pos'] = 5
    team2 = team2.sort_values('pos')
    # queue = pd.concat([team1, team2])
    # queue.to_csv("../../data/match.csv", index=False)
    # with open('../../data/activate.txt', 'r+') as f:
    #     f.truncate(0)
    #     f.write('yes')
    return team1['disc'].tolist(), team2['disc'].tolist()


def role_allocation(team):
    graph = nx.Graph()
    for i in range(0, 5):
        graph.add_node(team.index[i])
        for j in range(1, 6):
            graph.add_node(j + 5000)
            graph.add_edge(team.index[i], j + 5000, weight=team.iloc[[i], [j + 2]].values.min())
    return bipartite.minimum_weight_full_matching(graph, top_nodes=None, weight='weight')
