# For all functions relating to adding/removing/amending/viewing from users.csv

import pandas as pd
import csv
import psycopg2
import yaml
def connect_to_database():
    with open("../../credentials/databaseconnect.yml", "r") as con_info:
        con = (yaml.safe_load(con_info))
        host = con['HOST']
        port = con['PORT']
        user = con['USER']
        password = con['PASSWORD']
    try:
        connection = psycopg2.connect(user=user, host=host, password=password, port=port, database='doghouse')
        return connection
    except Exception as e:
        print('Error while connecting to database. Is the connection string correct? ', e)
        return False
def update_user_data(discord_id, columns, new_data):
    df = pd.DataFrame(pd.read_csv("../../data/users.csv", header=0, index_col=0))
    index = df.loc[(df['disc'] == int(discord_id))].index.values.astype(int)[0]
    df.loc[index, 'pos1'] = new_data[0]
    df.loc[index, 'pos2'] = new_data[1]
    df.loc[index, 'pos3'] = new_data[2]
    df.loc[index, 'pos4'] = new_data[3]
    df.loc[index, 'pos5'] = new_data[4]
    df.to_csv("../../data/users.csv")
    roles = [str(i) for i in new_data]
    user_role = str(''.join(roles))
    connection = connect_to_database()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute(f"SELECT role FROM players WHERE discord = '{discord_id}';")
            record = cursor.fetchone()
            cursor.execute(f"UPDATE players SET role = '{user_role}' WHERE discord = '{discord_id}';")
            connection.commit()
            print(f'Successfully updated user with discord_id {discord_id} role from {record[0]} to {user_role} to the database.')
        except (psycopg2.errors.UniqueViolation) as error:
            print("Error when updating user details in the database. Is the user in the database? ", error)
            print(f'WARNING: DB update of user with discord id {discord_id} failed.')
    else:
        print(f'WARNING: DB update of user with discord id {discord_id} failed.')

  

def check_for_value(value_check):
    user_data = pd.read_csv("../../data/users.csv")
    if value_check not in user_data.values:
        variable = False
        return variable
    else:
        variable = True
        return variable

def view_user_data(discord_id):
    user_data = pd.read_csv("../../data/users.csv")
    user_data_list = user_data.query(f'disc=={discord_id}').values.flatten().tolist()
    return user_data_list

def add_user_data(player):
    df = pd.DataFrame(pd.read_csv("../../data/users.csv", header=0, index_col=0))
    df.loc[len(df.index)] = player
    df.to_csv("../../data/users.csv")
    user_discord_id = player[0]
    user_dota_id = player[1]
    user_mmr = player[2]
    roles = [str(i) for i in player[3:]]
    user_role = str(''.join(roles))
    connection = connect_to_database()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute(f"INSERT INTO players (discord, dota, mmr, role) VALUES ({user_discord_id}, {user_dota_id}, {user_mmr}, {user_role}) RETURNING *;")
            connection.commit()
            print(f'Successfully added user with details {player} to the database.')
        except (psycopg2.errors.UniqueViolation) as error:
            print("Error when inserting into the database. Is the user already registered? ", error)
            print(f'WARNING: DB insertion of user with details {player} failed.')
    else:
        print(f'WARNING: DB insertion of user with details {player} failed.')