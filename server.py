import socket
import pickle
from _thread import *
from setup import *
from copy import copy
import sys

max_players = 2


class Game:
    def __init__(self, game_id):
        self.game_id = game_id
        self.players = 0
        self.ready = False
        self.turn = 0
        self.board_data = copy(default)
        self.last_move = None

    def change_turn_to(self, turn):
        self.turn = turn

    def move_piece(self, move):
        move["begin_pos"] = transform(move["begin_pos"]); move["end_pos"] = transform(move["end_pos"])
        self.board_data["data"][move["end_pos"]] = self.board_data["data"][move["begin_pos"]]
        self.board_data["data"][move["begin_pos"]] = None
        self.last_move = move
        print(f"in game {self.game_id} player {move['player_id']} moved their {move['piece']} from {move['begin_pos']} to {move['end_pos']}")
        #move[0]: playerid
        #move[1]: piece (id not object)
        #move[2]: begin_pos
        #move[3]: end_pos

class server:
    def __init__(self):
        self.host = ""
        self.port = 5555
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.games = {1: Game(1)}
        self.player_id = 0
        self.run()

    def get_next_game(self):
        for game_id in self.games:
            game = self.games[game_id]
            if not game.ready:
                return game_id

    def change_turn_to(self, game, turn):
        game.change_turn_to(turn)

    def move_piece(self, game, move):
        game.move_piece(move)

    def handle_client(self, conn, game_id):
        game = self.games[game_id]
        while True:
            game = self.games[game_id]
            try:
                message = pickle.loads(conn.recv(2048))
                commands = {"GG": lambda game=game: conn.send(pickle.dumps(game)),
                            "CT": lambda game=game: self.change_turn_to(game, message[1]),
                            "MP": lambda game=game: self.move_piece(game, message[1])
                                }
                commands[message[0]]()
            except:
                if not game.ready:
                   self.player_id-=1
                print(f"connection lost with {conn}")
                conn.close()
                break

    def run(self):
        self.server.listen()
        print(f"server object {id(self)} is started and waiting for clients")
        while True:
            conn, addr = self.server.accept()
            print(f"{addr} joined the server")
            game_id = self.get_next_game(); game = self.games[game_id]
            conn.send(pickle.dumps((self.player_id, game_id)))
            if self.player_id==max_players-1:
                game.ready=True
                self.player_id = -1
                self.games[game_id+1] = Game(game_id+1)
                print(f"game {game_id} is started and game {game_id+1} is created!")
            start_new_thread(self.handle_client, (conn, game_id))
            self.player_id+=1


if (sys.argv[0].split("\\")[-1])=="server.py":
    s=server()
