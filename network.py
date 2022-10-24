import socket
import pickle
import time
from setup import *
from _thread import *


class Network:
    def __init__(self):
        self.host="192.168.1.11"
        self.port=5555
        self.client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.player_id=self.connect()

    def connect(self):
        self.client.connect((self.host, self.port))
        player_id = pickle.loads(self.client.recv(2048))
        return player_id

    def get_game(self):
        self.client.send(pickle.dumps(("GG",)))
        game = pickle.loads(self.client.recv(2048))
        
        if game.game_id!=self.player_id[1]:
            print("[GAME-ERROR] wrong game sent by server!!")
            
        return game

    def change_turn_to(self, turn):
        self.client.send(pickle.dumps(("CT", turn)))

    def send_move(self, move):
        self.client.send(pickle.dumps(("MP", move)))
