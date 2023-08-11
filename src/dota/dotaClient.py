from steam.client import SteamClient
from dota2.client import Dota2Client
import multiprocessing
import dota2
import os
import sys
sys.path.append(f'{os.getcwd()}/src/utils')
from connections import getCredentialsSteam
import logging
from eventemitter import EventEmitter
from multiprocessing.connection import Client
import time
import pandas as pd
event = EventEmitter()

logging.basicConfig(format='[%(asctime)s] %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
(user, password) = getCredentialsSteam()
client = SteamClient()
dota = Dota2Client(client)
dota_channel_manager = dota2.features.chat.ChannelManager(dota, 'logger')

def check_lobby_status():
    pass

@client.on('logged_on')
def start_dota():
    dota.launch()
    print("Running...")
 

#@dota.on('ready')
#def fetch_profile_card():
    #dota.request_profile_card(70388657)

@client.on('disconnected')
def kill_lobby():
    dota.destroy_lobby()
@dota.on('dota_welcome')
def create_base_lobby(filler):

    dota.destroy_lobby()
    opt = {
            'game_name': 'Doghouse Test Lobby2',
            'game_mode': dota2.enums.DOTA_GameMode.DOTA_GAMEMODE_CM,
            'fill_with_bots': False,
            'allow_spectating': True,
            'allow_cheats': False,
            'allchat': False,
            'dota_tv_delay': 0,  # TODO: this is LobbyDotaTV_10
            'pause_setting': 0,  # TODO: LobbyDotaPauseSetting_Unlimited
        }
    dota.create_practice_lobby(password="sttsq1", options=opt)
    dota.channels.join_lobby_channel()
    dota_channel_manager.join_lobby_channel()
    dota.join_practice_lobby_team()  # jump to unassigned players
    event.emit('check_queue')

@dota.on(dota2.features.Lobby.EVENT_LOBBY_NEW) 
def do_dota_wait(lobby):
    dota.emit('start_queue', lobby)


@dota.on('starting_queue')
def do_queue(lobby, idList):
    dota.emit('queue_full', idList)
    print('Queue Full...')
@dota.on('queue_full')
def dota_invite(ids):    
    print('Inviting...')
    for i in ids:
        print(f'inviting {i}')
        dota.invite_to_lobby(i)

@dota.on('lobby_changed')
def change_lobby(lobby):
    pass
@event.on('check_queue')
def check_queue():
    if os.path.isfile('data/activate.txt'):
        df = pd.DataFrame(pd.read_csv('data/users.csv'))
        ids = list(df['id'])
        os.remove('data/activate.txt')
        dota.emit('queue_full', ids)
    time.sleep(0.1)
    event.emit('check_queue')
@dota_channel_manager.on('message')
def read_message(c, message):
    if message.text.startswith('!'):
        print(message)
        if message.text == '!start':
            print(dota.lobby)
client.cli_login(username=user, password=password)
client.run_forever()