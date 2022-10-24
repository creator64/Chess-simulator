from setup import *
from _thread import *

class game_screen:
    def __init__(self, canvas, cols=8, rows=8, start_data=default):
        self.canvas=canvas; self.canvas.update(); w=self.canvas.winfo_width(); h=self.canvas.winfo_width()
        self.selected=False
        self.check=False
        self.checkmate=False
        self.turn="white"
        self.oppturn="black"
        self.running=True
        x=(w/2)-((width*8)/2); y=10; borderwidth=10
        self.board=Board(self.canvas, x, y, width, data=start_data)
        self.wturn=Label(self.canvas.master, text="white is on turn", font=("Courier", 20), bg="#FC600F"); self.wturn.place(x=25, y=70)
        self.log=Log(self.canvas, x+self.board.total_width+borderwidth, 0, int(w-x+self.board.total_width+borderwidth), h)
        self.back_btn=Button(self.canvas.master, text="quit", bg="red", font=("courier", 20), command=self.quit_game)
        self.back_btn.place(x=0, y=0, width=100, height=50)

    def change_turns(self):
        if self.turn=="white":
            self.turn="black"
            self.oppturn="white"
        else:
            self.turn="white"
            self.oppturn="black"

    def quit_game(self):
        if messagebox.askokcancel("Quit?", "Do you really want to quit the game?"):
            self.running = False
            screens["show"](screens["menu_screen"], args=(self.canvas,))

    def update_stats(self):
        self.wturn.config(text="%s is on turn" %(self.turn))
    
    def run(self):
        self.canvas.bind("<Button-1>", self.click)
        self.log.write("The game has started. Good luck")
        while self.running:
            self.update_stats()

    def click(self, evt, x=0, y=0):
        if bool(evt):
            x=evt.x; y=evt.y
        if not self.selected:   #no piece selected
            platform=self.board.identify_platform(x, y)
            piece=self.board.identify_piece(platform, self.turn)
            if bool(piece):
                platform.clicked()
                self.selected=True; piece.selected=True
                for pf in self.board.platformlist:
                    if piece.main_rule(piece.coords, pf, self.turn):
                        pf.clickable()
        else:    # there is a piece selected
            platform=self.board.identify_platform(x, y)

            #can move to this platform
            if platform.sc:
                selected_piece=self.board.identify_selected_piece()
                oc=selected_piece.coords; mc=platform.id
                selected_piece.move(platform)
                self.board.clear_all_platforms(); self.board.deselect_all_pieces()
                self.selected=False
                self.log.write(f"player {self.turn} moved their {selected_piece.id} from {oc[0]}{oc[1]} to {mc[0]}{mc[1]}")
                self.change_turns()
                if self.board.check_if_checkmate(self.turn):
                    self.log.write(f"player {self.turn} is checkmate!"); self.log.write(f"player {self.oppturn} won the game", colour="orange")
                elif self.board.check_if_check(self.turn):
                    self.check=True
                    self.log.write(f"player {self.turn} is check")

            
            #cant move to this platform
            else:
                piece=self.board.identify_piece(platform, self.turn)
                if bool(piece):
                    self.board.clear_all_platforms()
                    self.selected=False
                    if not piece.selected:
                        self.board.deselect_all_pieces()
                        self.click(None, x=x, y=y)
                    else: self.board.deselect_all_pieces()
