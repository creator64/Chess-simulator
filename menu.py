from tkinter import *
from tkinter import messagebox
from _thread import *
from PIL import Image, ImageTk
import copy
import main_mp
import main_ol
from server import Game
from setup import *
from database import database
import time


selected_board = default
def change_board(board):
    global selected_board
    selected_board = board
    show_screen(menu_screen, args=(c,))


class custom_canvas(Canvas):
    def __init__(self, **kwargs):
        self.commands={}
        self.pics=[]
        super(custom_canvas, self).__init__(**kwargs)
    
    def clear(self, exceptions=[]):
        for item in self.find_all():
            if item not in exceptions:
                self.delete(item)
                try:
                    del self.commands[item]
                except:
                    pass

        for item in self.master.winfo_children():
            if item not in exceptions and item!=self:
                item.destroy()

class menu_screen:
    def __init__(self, canvas):
        self.canvas=canvas
        self.button_cl=Button(self.canvas.master, text="play", command=self.play)
        self.button_cl.grid(column=0, row=0)
        
        self.button_mp=Button(self.canvas.master, text="boards", command=self.manipulation)
        self.button_mp.grid(column=1, row=0)

        self.button_ol=Button(self.canvas.master, text="play online", command=self.play_on)
        self.button_ol.grid(column=2, row=0)

        self.board_lb=Label(self.canvas.master, text="board:", bg=custom_bg, font=("courier", 50))
        self.board_lb.place(x=500, y=200)
        self.show_board=Board(self.canvas, 500, 300, 40, data=selected_board, borderwidth=5)

    def manipulation(self):
        show_screen(view_screen, args=(self.canvas,))

    def play(self):
        global g
        g=show_screen(main_mp.game_screen, args=(self.canvas,), kwargs={"start_data": selected_board})
        start_new_thread(g.run, ())

    def play_on(self):
        g=show_screen(main_ol.load_screen, args=(self.canvas,))
        start_new_thread(g.run, ())

class view_screen:
    def __init__(self, canvas):
        self.canvas=canvas; w=self.canvas.winfo_width(); h=self.canvas.winfo_height()
        self.col1=(200, 300)
        self.col2=(300, 800)
        self.col3=(800, 1100)
        self.col4=(1100, 1300)
        self.rows = 5
        self.label_name=Label(self.canvas.master, text="NAME", font=("courier", 30), anchor="w")
        self.label_date=Label(self.canvas.master, text="DATE CREATED", font=("courier", 30), anchor="w", bg="orange")
        self.label_name.place(y=0, x=self.col2[0], width=self.col2[1]-self.col2[0], height=50); self.label_date.place(y=0, x=self.col3[0], width=self.col3[1]-self.col3[0], height=50)
        self.new_btn=Button(self.canvas.master, text="+", font=("courier", 30), bg="#AB6078", command=self.new); self.new_btn.place(x=0, y=0, width=50, height=50)
        self.back_btn=Button(self.canvas.master, text="back", font=("courier", 15), bg="red", command=self.back); self.back_btn.place(x=w-100, y=h-50, width=100, height=50)
        self.d=database("chess.db")
        self.load_boards()

    def new(self):
        self.canvas.clear()
        label=Label(self.canvas.master, text="Enter the name of the board", font=("courier", 50), bg="#FC600F"); label.place(x=150, y=150)
        width=700; btn_width=350; w=self.canvas.winfo_width(); h=self.canvas.winfo_height()
        e=Entry(self.canvas.master, borderwidth=3, font=("courier", 35), justify="center")
        t=time.localtime()
        proceed_btn=Button(self.canvas.master, text="next", bg="green", font=("courier", 25),\
                           command=lambda: self.edit([e.get(), empty, (t[2], t[1], t[0])], new=True))
        proceed_btn.place(x=(1/2)*w-((1/2)*btn_width), y=500, width=btn_width, height=110); e.place(x=(1/2)*w-((1/2)*width), y=300, width=width, height=100)
        back_btn=Button(self.canvas.master, text="back", bg="red", font=("courier", 20), command=self.back_new); back_btn.place(x=0, y=0, width=125, height=75)

    def rename_screen(self, index, orig_name):
        self.canvas.clear()
        label=Label(self.canvas.master, text="Enter the new name of the board", font=("courier", 50), bg="#FC600F"); label.place(x=100, y=150)
        width=700; btn_width=350; w=self.canvas.winfo_width(); h=self.canvas.winfo_height()
        e=Entry(self.canvas.master, borderwidth=3, font=("courier", 35), justify="center")
        e.place(x=(1/2)*w-((1/2)*width), y=300, width=width, height=100); e.insert(END, orig_name)
        proceed_btn=Button(self.canvas.master, text="finish", bg="green", font=("courier", 25),\
                           command=lambda: self.rename("boards", index, changes={"name": e.get()}))
        proceed_btn.place(x=(1/2)*w-((1/2)*btn_width), y=500, width=btn_width, height=110)
        back_btn=Button(self.canvas.master, text="back", bg="red", font=("courier", 20), command=self.back_new); back_btn.place(x=0, y=0, width=125, height=75)

    def back(self):
        show_screen(menu_screen, args=(self.canvas,))

    def back_new(self):
        show_screen(view_screen, args=(self.canvas,))

    def load_boards(self):
        board_list=self.d.load_all("boards")
        board_list.insert(0, [None, "default", default, None])
        y = -1
        row_height = int((self.col1[1]-self.col1[0])/8)*8
        for board in board_list:
            y+=1

            #labels
            l=Label(self.canvas.master, text=board[1], font=("courier", 30))
            l.place(x=self.col2[0], y=row_height*y+100, width=self.col2[1]-self.col2[0], height=row_height)

            #board
            proto_board=Board(self.canvas, self.col1[0], row_height*y+100, int(row_height/8), data=board[2], borderwidth=0)
            
            if bool(board[0]):
                fixed_date=str(board[3][0])+"/"+str(board[3][1])+"/"+str(board[3][2])
            
                l=Label(self.canvas.master, text=fixed_date, font=("courier", 30))
                l.place(x=self.col3[0], y=row_height*y+100, width=self.col3[1]-self.col3[0], height=row_height)
            
                #buttons
                b=Button(self.canvas.master, text="edit", bg="orange", command=lambda board=board: self.edit(board))
                b.place(x=self.col4[0], y=row_height*y+100, width=0.5*(self.col4[1]-self.col4[0]), height=0.5*row_height)
                b=Button(self.canvas.master, text="rename", bg="yellow", command=lambda board=board: self.rename_screen(board[0], board[1]))
                b.place(x=self.col4[0]+0.5*(self.col4[1]-self.col4[0]), y=row_height*y+100, width=0.5*(self.col4[1]-self.col4[0]), height=0.5*row_height)
                b=Button(self.canvas.master, text="delete", bg="red", command=lambda board=board: self.delete("boards", board[0]))
                b.place(x=self.col4[0], y=row_height*y+100+0.5*row_height, width=0.5*(self.col4[1]-self.col4[0]), height=0.5*row_height)
            b=Button(self.canvas.master, text="select", bg="green", command=lambda board=board: change_board(board[2]))
            b.place(x=self.col4[0]+0.5*(self.col4[1]-self.col4[0]), y=row_height*y+100+0.5*row_height, width=0.5*(self.col4[1]-self.col4[0]), height=0.5*row_height)

    def rename(self, table, index, changes={}):
        self.d.update(table, index, changes=changes)
        show_screen(view_screen, args=(self.canvas,))
        

    def delete(self, table, index):
        if messagebox.askyesno("delete board", "Are you really sure that you want to remove this board?"):
            self.d.delete(table, index)
            show_screen(view_screen, args=(self.canvas,))

    def edit(self, board_item, new=False):
        if new:
            self.d.insert_new("boards", board_item)
            board_item=self.d.load_all("boards")[-1]
            show_screen(editor_screen, args=(self.canvas, board_item), kwargs={"new": True})
        else:
            show_screen(editor_screen, args=(self.canvas, board_item))
        
class editor_screen:
    def __init__(self, canvas, board_item, new=False):
        self.canvas=canvas;  w=self.canvas.winfo_width(); h=self.canvas.winfo_height()
        self.board_item=board_item
        self.board_width=70; self.total_width=self.board_width*8
        self.board=Board(self.canvas, (w/2)-(self.total_width/2), (h/2)-(self.total_width/2)+30, self.board_width, data=board_item[2])
        if new:
            self.board.add_piece("King", ("E", 1), "white")
            self.board.add_piece("King", ("E", 8), "black")
        self.slbt=[]
        self.data_list=[self.board.read()]
        self.index=0
        self.blundo=False
        self.saved=False
        self.d=database("chess.db")

        self.name_label=Label(self.canvas.master, text=self.board_item[1], font=("courier", 50)); self.name_label.place(x=(w/2), y=0)
        self.create_buttons(2, 5, 100, 100)
        self.del_btn=Delete_Button(self, 0, 500, 200, 100, "#d28460", "#8b4727"); self.slbt.append(self.del_btn)
        self.undo_btn=Button(self.canvas.master, text="undo", command=lambda: self.undo(None)); self.undo_btn.place(x=0, y=600, width=200, height=100)
        #self.btn=Button(tk, text="show data", command=self.check_data); self.btn.place(x=300, y=100)
        self.bck_btn=Button(self.canvas.master, text="back", bg="red", command=lambda: self.back(None)); self.bck_btn.place(x=w-200, y=h-100, width=200, height=100)
        self.save_btn=Button(self.canvas.master, text="save", bg="green", command=lambda: self.save(None))
        self.save_btn.place(x=w-200, y=100, width=200, height=100)
        self.canvas.bind("<Button-1>", self.edit_board)
        self.canvas.bind("<B1-Motion>", self.drag_or_swipe)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)
        self.canvas.master.bind("<Control-z>", self.undo)
        self.canvas.master.bind("<Control-s>", self.save)
        self.canvas.master.bind("<Control-q>", self.back)

    def back(self, evt):
        if self.saved:
            show_screen(view_screen, args=(self.canvas,))
        elif messagebox.askokcancel("unsaved", "You have not saved the board. Do you want to save and continue?"): #ok is True
            succeed=self.save(None)
            if succeed:
                show_screen(view_screen, args=(self.canvas,))

    def save(self, evt):
        if self.board.check_if_check("white"):
            messagebox.showerror("invalid board", "invalid board: player white is check")
            return False
        elif self.board.check_if_check("black"):
            messagebox.showerror("invalid board", "invalid board: player black is check")
            return False
        else:
            self.d.update("boards", self.board_item[0], changes={"data": self.board.read()})
            self.saved=True
            self.save_btn.config(bg="gray")
            return True


    def create_buttons(self, cols, rows, bt_width, bt_height):
        list=[("pawn_bt_w", "Pawn", "white"),
          ("rook_bt_w", "Rook", "white"),
          ("bishop_bt_w", "Bishop", "white"),
          ("knight_bt_w", "Knight", "white"),
          ("queen_bt_w", "Queen", "white"),
          ("pawn_bt_b", "Pawn", "black"),
          ("rook_bt_b", "Rook", "black"),
          ("bishop_bt_b", "Bishop", "black"),
          ("knight_bt_b", "Knight", "black"),
          ("queen_bt_b", "Queen", "black")]

        nmb=0
        for x in range(0, cols):
            for y in range(0, rows):
                absx=x*bt_width; absy=y*bt_height
                exec("self.%s=Piece_Button(self, absx, absy, bt_width, bt_height, '#737373', 'white', '%s', '%s')" %(list[nmb][0], list[nmb][1], list[nmb][2]))
                self.slbt.append(eval("self." + list[nmb][0]))
                nmb+=1
                
    def fix_index(self):
        if self.blundo:
            for board in self.data_list[self.index+1:]:
                self.data_list.remove(board)
            self.blundo = False
        self.data_list.append(self.board.read())
        self.index+=1
        self.saved=False
        self.save_btn.config(bg="green")

    #def check_data(self):
    #    print(self.index) 

    def edit_board(self, evt, mode="click"):
        platform=self.board.identify_platform(evt.x, evt.y)
        piece=self.board.identify_piece(platform, "both")
        selected_button=self.check_selected_button()
        if mode=="swipe":
            if not bool(piece):
                self.board.add_piece(selected_button.piece, platform.id, selected_button.colour)
                self.fix_index()
            else:
                if "Delete_Button" in str(selected_button):
                    if piece.id!="King":
                        piece.get_kicked()
                        self.fix_index()
        elif mode=="click":
            if not bool(piece):
                if bool(selected_button):
                    p=selected_button.piece; colour=selected_button.colour
                    self.board.add_piece(p, platform.id, colour)
                    self.fix_index()
            else:
                if "Delete_Button" in str(selected_button):
                    if piece.id!="King":
                        piece.get_kicked()
                        self.fix_index()
                else:
                    self.start_drag(evt)

    def check_selected_button(self):
        for button in self.slbt:
            if button.selected:
                return button

    def deselect_buttons(self):
        for btn in self.slbt:
            btn.deselect()

    def start_drag(self, evt):
        platform=self.board.identify_platform(evt.x, evt.y)
        piece=self.board.identify_piece(platform, "both")
        if piece: piece.drag=True

    def drag_or_swipe(self, evt):
        #drag
        x=evt.x; y=evt.y
        for piece in self.board.piecelist:
            if piece.drag and piece.exist:
                size_x=self.board_width; size_y=self.board_width
                xplace=x-(1/2*size_x); yplace=y-(1/2*size_y)
                coords=self.canvas.coords(piece.img)
                self.canvas.move(piece.img, xplace-coords[0], yplace-coords[1])
                return 0

        #swipe
        self.edit_board(evt, mode="swipe")

    def stop_drag(self, evt):
        for piece in self.board.piecelist:
            if piece.drag and piece.exist:
                platform=self.board.identify_platform(evt.x, evt.y)
                
                if not platform:
                    self.board.add_piece(piece.id.capitalize(), piece.coords, piece.colour)
                    piece.get_kicked()
                    return 0
                
                p=self.board.identify_piece(platform, "both")
                if p:
                    if p.id == "King":
                        self.board.add_piece(piece.id.capitalize(), piece.coords, piece.colour)
                        piece.get_kicked()
                        self.fix_index()
                    #elif p!=piece:
                    #    p.get_kicked()
                    else:
                        p.get_kicked()
                        piece.get_kicked()
                        self.board.add_piece(piece.id.capitalize(), platform.id, piece.colour)
                        self.fix_index()
                else:
                    piece.get_kicked()
                    self.board.add_piece(piece.id.capitalize(), platform.id, piece.colour)
                    self.fix_index()

    def undo(self, evt):
        self.index-=1
        if self.index>=0:
            data = self.data_list[self.index]
            self.board.put_data(data)
        else:
            self.index=0
        self.blundo = True

class Slbt:
    def __init__(self, master, x, y, width, height, bgact, bgpass):
        self.master=master
        self.x=x; self.y=y; self.width=width; self.height=height
        self.selected=False
        self.bgact=bgact; self.bgpass=bgpass

    def select(self):
        self.master.deselect_buttons()
        self.selected=True
        self.id.config(bg=self.bgact)

    def deselect(self):
        self.selected=False
        self.id.config(bg=self.bgpass)

    def select_or_deselect(self):
        if self.selected:
            self.deselect()
        else:
            self.select()

class Delete_Button(Slbt):
    def __init__(self, master, x, y, width, height, bgact, bgpass):
        Slbt.__init__(self, master, x, y, width, height, bgact, bgpass)
        self.id=Button(self.master.canvas.master, text="delete", bg=self.bgpass, font=("courier", 12), command=self.select_or_deselect)
        self.id.place(x=self.x, y=self.y, width=self.width, height=self.height)
            

class Piece_Button(Slbt):
    def __init__(self, master, x, y, width, height, bgact, bgpass, piece, colour):
        Slbt.__init__(self, master, x, y, width, height, bgact, bgpass)
        self.piece=piece
        self.colour=colour
        self.im=image_dict[(self.piece, self.colour)]
        self.im=self.im.resize((self.width, self.width))
        self.im=ImageTk.PhotoImage(self.im)
        self.id=Button(self.master.canvas.master, image=self.im, command=self.select_or_deselect)
        self.id.place(x=self.x, y=self.y, width=self.width, height=self.height)

screens["menu_screen"] = menu_screen
screens["view_screen"] = view_screen
screens["editor_screen"] = editor_screen
screens["game_screen_mp"] = main_mp.game_screen
screens["game_screen_ol"] = main_ol.game_screen
screens["load_screen_ol"] = main_ol.load_screen


tk=Tk()
tk.state("zoomed")
#tk.resizable(0, 0)
w=tk.winfo_width()
h=tk.winfo_height()
c=custom_canvas(width=w, height=h, bg="#FC600F", highlightthickness=0)
c.place(relx=0, rely=0, relwidth=1, relheight=1)


def show_screen(screen, args=(), kwargs={}, canvas=c):
    canvas.clear()
    s=screen(*args, **kwargs)
    return s

screens["show"] = show_screen

show_screen(menu_screen, args=(c,))
tk.mainloop()
