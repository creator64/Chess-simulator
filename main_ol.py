from setup import *
from tkinter import *
from _thread import *
import network
import time


class load_screen:
    def __init__(self, canvas):
        self.canvas = canvas
        self.n = network.Network()
        self.running = True
        self.leave_btn = Button(self.canvas.master, text="quit", bg="red", command=self.quit); self.leave_btn.place(x=500, y=300, width=400, height=200)

    def run(self):
        self.label_ready = Label(self.canvas.master, text="looking for players"); self.label_ready.place(x=100, y=200)
        while self.running:
            game = self.n.get_game()
            if game.ready:
                g = screens["show"](screens["game_screen_ol"], args=(self.canvas, self.n))
                start_new_thread(g.run, ())
                break

    def quit(self):
        self.running = False
        screens["show"](screens["menu_screen"], args=(self.canvas,))


class game_screen:
    def __init__(self, canvas, network, start_data=default):
        self.canvas = canvas; self.canvas.update(); w=self.canvas.winfo_width(); h=self.canvas.winfo_width()
        self.n = network
        self.player_id = self.n.player_id
        self.colour = {0: "white", 1: "black"}[self.player_id[0]]
        self.l = Label(self.canvas.master, text="", bg=custom_bg); self.l.place(x=50, y=20)
        self.onturn = []
        x=(w/2)-((width*8)/2); y=10; borderwidth=10
        self.board=Board(self.canvas, x, y, width, data=start_data)
        self.log = Log(self.canvas, x+self.board.total_width+borderwidth, 0, int(w-x+self.board.total_width+borderwidth), h); self.log.write("lol")
        game = self.n.get_game()
        self.label_game = Label(self.canvas.master, text="you are joined to game"+str(game.game_id)); self.label_game.place(x=300, y=200)

    def send_move(self, move):
        self.n.send_move(move)

    def change_turns(self):
        dict = {0: 1, 1: 0}
        self.n.change_turn_to(dict[self.player_id[0]])

    def set_turn(self):
        g = self.n.get_game()
        if g.turn==self.player_id[0]:
            self.onturn = [True, g.turn]
        else:
            self.onturn = [False, g.turn]

    def run(self):
        dict = {True: "you are on turn", False: "opponents turn"}
        self.canvas.bind("<Button-1>", self.click)
        t=time.time()
        while True:
            g = self.n.get_game()
            if time.time()-t>1:
                print("not lagging")
                t=time.time()
            self.set_turn()
            self.l.config(text=dict[self.onturn[0]])
            if self.board.read()["data"] !=  g.board_data["data"]:
                print("lol")
                self.board.put_data(g.board_data)
                #move = g.last_move
                #platform_b = self.board.identify_platform_3(move["begin_pos"]); platform_e = self.board.identify_platform_3(move["end_pos"])
                #piece = self.board.identify_piece(platform_b, "both")
                #piece.move(platform_e)

    def click(self, evt, x=0, y=0):
        if self.onturn[0]:
            if bool(evt):
                x=evt.x; y=evt.y
            #print("clicked at", x, y)
            if not self.board.identify_selected_piece():   #no piece selected
                platform=self.board.identify_platform(x, y)
                piece=self.board.identify_piece(platform, self.colour)
                if bool(piece):
                    platform.clicked()
                    piece.selected=True
                    for pf in self.board.platformlist:
                        if piece.main_rule(piece.coords, pf, self.colour):
                            pf.clickable()
            else:    # there is a piece selected
                platform=self.board.identify_platform(x, y)

                #can move to this platform
                if platform.sc:
                    selected_piece=self.board.identify_selected_piece()
                    oc=selected_piece.coords; mc=platform.id
                    self.board.clear_all_platforms(); self.board.deselect_all_pieces()
                    #self.log.write(f"player {self.turn} moved their {selected_piece.id} from {oc[0]}{oc[1]} to {mc[0]}{mc[1]}")
                    self.change_turns()
                    move = {"player_id": self.player_id, "piece": selected_piece.id, "begin_pos": oc, "end_pos": mc}
                    self.send_move(move)
                    
                    #if self.board.check_if_checkmate(self.turn):
                    #    self.log.write(f"player {self.turn} is checkmate!"); self.log.write(f"player {self.oppturn} won the game", colour="orange")
                    #elif self.board.check_if_check(self.turn):
                    #    self.check=True
                    #    self.log.write(f"player {self.turn} is check")
                
                #cant move to this platform
                else:
                    piece=self.board.identify_piece(platform, self.colour)
                    if bool(piece):
                        self.board.clear_all_platforms()
                        self.selected=False
                        if not piece.selected:
                            self.board.deselect_all_pieces()
                            self.click(None, x=x, y=y)
                        else: self.board.deselect_all_pieces()
