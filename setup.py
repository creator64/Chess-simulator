from tkinter import *
from PIL import Image, ImageTk
import time
import json

width=86
custom_bg = "#FC600F"

with open("default.json", "r") as f:
    default=json.load(f)

with open("empty.json", "r") as f:
    empty=json.load(f)

screens = {}

ipawnwhite=Image.open("chess pieces\\pawn white.png"); ipawnblack=Image.open("chess pieces\\pawn black.png")
irookwhite=Image.open("chess pieces\\rook white.png"); irookblack=Image.open("chess pieces\\rook black.png")
ibishopwhite=Image.open("chess pieces\\bishop white.png"); ibishopblack=Image.open("chess pieces\\bishop black.png")
iknightwhite=Image.open("chess pieces\\knight white.png"); iknightblack=Image.open("chess pieces\\knight black.png")
iqueenwhite=Image.open("chess pieces\\queen white.png"); iqueenblack=Image.open("chess pieces\\queen black.png")
ikingwhite=Image.open("chess pieces\\king white.png"); ikingblack=Image.open("chess pieces\\king black.png")


image_dict={("Pawn", "white"): ipawnwhite, ("Pawn", "black"): ipawnblack,
              ("Rook", "white"): irookwhite, ("Rook", "black"): irookblack,
              ("Bishop", "white"): ibishopwhite, ("Bishop", "black"): ibishopblack,
              ("Knight", "white"): iknightwhite, ("Knight", "black"): iknightblack,
              ("Queen", "white"): iqueenwhite, ("Queen", "black"): iqueenblack}


def transform(value):
    if type(value)==list or type(value)==tuple:
        s=value[0]+"_"+str(value[1])
        return s
    elif type(value)==str:
        t=(value[0], int(value[2]))
        return t

#make dictionary key=id, value=coord
list_alphabet=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"];
def create_icd(width, xc=0, yc=0, cols=8, rows=8):
    icd={}
    for x in range(cols):
        for y in range(rows):
            icd[(list_alphabet[x], rows-y)]=(width*x+xc, width*y+yc)
            
    return icd

class Log:
    def __init__(self, canvas, x, y, width, height):
        self.canvas=canvas; self.x=x; self.y=y; self.width=width; self.height=height
        self.data=[]
        self.box = Listbox(self.canvas.master, bg="#FC600F", selectbackground="#9D3802", activestyle="none", font=("vani", 11))
        self.box.place(x=self.x, y=self.y, width=self.width-500, height=self.height)
        self.scrollbar = Scrollbar(self.canvas.master); self.scrollbar.place(x=x+width-50, y=0, width=50, height=100)
        self.box.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.box.yview)

    def write(self, data, index=0, colour="black"):
        self.box.insert(index, data)
        index = list(self.box.get(0, END)).index(data)
        self.box.itemconfig(index, fg=colour)
        self.data.append(data)

class Border:
    def __init__(self, canvas, x, y, width, height, colour="#341809", borderwidth=50):
        self.canvas=canvas; self.borderwidth=borderwidth
        self.canvas.create_rectangle(x-borderwidth, y, x, y+height, fill=colour, outline="")
        self.canvas.create_rectangle(x+width, y, x+width+borderwidth, y+height, fill=colour, outline="")
        self.canvas.create_rectangle(x-borderwidth, y-borderwidth, x+width+borderwidth, y, fill=colour, outline="")
        self.canvas.create_rectangle(x-borderwidth, y+height, x+width+borderwidth, y+height+borderwidth, fill=colour, outline="")


class Board:
    def __init__(self, canvas, xc, yc, width, data={}, borderwidth=10):
        self.data=data
        self.canvas=canvas
        self.xc=xc; self.yc=yc
        self.width=width
        self.total_width=self.width*self.data["cols"]; self.total_height=self.width*self.data["rows"]
        self.icd=create_icd(self.width, xc=self.xc, yc=self.yc)
        self.platformlist=[]; self.piecelist=[]; self.piecelist_white=[]; self.piecelist_black=[]
        self.open(self.data)
        self.border=Border(canvas, self.xc, self.yc, self.total_width, self.total_height, borderwidth=borderwidth)

    def open(self, data, create_platforms=True):
        if create_platforms:
            self.create_platforms(data["cols"], data["rows"])
        self.create_pieces(data)

    def read(self):
        data = {"players": 2, "colors": ["white", "black"], "cols": 8, "rows": 8, "data": {}}
        for pf in self.platformlist:
            piece = self.identify_piece(pf, "both")
            if bool(piece):
                data["data"][transform(pf.id)] = [piece.id, piece.colour]
            else: data["data"][transform(pf.id)] = None

        return data

    def add_piece(self, id, coords, colour):
        dict={"Pawn": Pawn, "Rook": Rook, "Bishop": Bishop, "Knight": Knight, "Queen": Queen, "King": King}
        self.piece=dict[id](coords, colour, self) #self.piece=Pawn(("A", 1), "white", self)
        
        self.piecelist.append(self.piece)
        if colour=="white": self.piecelist_white.append(self.piece)
        elif colour=="black": self.piecelist_black.append(self.piece)

    def put_data(self, data):
        self.clear()
        self.open(data, create_platforms=False) #this doesnt function

    def create_platforms(self, cols, rows):
        xc=self.xc #x-coord on board
        yc=self.yc #y-coord on board
        nmb=0; list=[]
        for x in range(0, self.data["cols"]):
            for y in range(0, self.data["rows"]):
                nmb+=1
                if x%2==0:
                    if y%2==0:
                        exec("self.pf%s=platform(list_alphabet[x], %s-y, xc, yc, 'self.bgw', self)" %(nmb, self.data["rows"])) #white
                    else:
                        exec("self.pf%s=platform(list_alphabet[x], %s-y, xc, yc, 'self.bgb', self)" %(nmb, self.data["rows"])) #black
                else:
                    if y%2==0:
                        exec("self.pf%s=platform(list_alphabet[x], %s-y, xc, yc, 'self.bgb', self)" %(nmb, self.data["rows"])) #black
                    else:
                        exec("self.pf%s=platform(list_alphabet[x], %s-y, xc, yc, 'self.bgw', self)" %(nmb, self.data["rows"])) #white
                yc+=self.width
                exec("list.append(self.pf%s)" %(nmb))
            yc=self.yc
            xc+=self.width
        #ordening platformlist
        for x in range(8):
            for i in range(8, 65, 8):
                r=i-x
                exec("self.platformlist.append(self.pf%s)" %(r))

    def create_pieces(self, data):
        for coord in data["data"]:
            try:
                piece_info=data["data"][coord] #example: coord=("A", 1) and piece_info=["Pawn", "white"]
                coord=transform(coord)
                self.add_piece(piece_info[0].capitalize(), coord, piece_info[1])
            except:
                continue

    def identify_platform(self, x, y):
        for pf in self.platformlist:
            if x>=pf.xc and x<=pf.xc+self.width:
                if y>=pf.yc and y<=pf.yc+self.width:
                    return pf

    def identify_piece(self, platform, turn):
        if not platform: return None
        dict={"white": self.piecelist_white, "black": self.piecelist_black, "both": self.piecelist}
        list=dict[turn]
        for piece in list:
            if piece.coords==platform.id and piece.exist:
                return piece
                break
            if piece==list[len(list)-1]:
                return None

    def horizontal_blockage(self, row, begin_pos, end_pos):
        list=[begin_pos[0], end_pos[0]]
        for pf in self.platformlist:
            if pf.id[1]==row and pf.id[0]>min(list) and pf.id[0]<max(list):
                if bool(self.identify_piece(pf, "both")):
                    return True
        return False

    def vertical_blockage(self, column, begin_pos, end_pos):
        list=[begin_pos[1], end_pos[1]]
        for pf in self.platformlist:
            if pf.id[0]==column and pf.id[1]>min(list) and pf.id[1]<max(list):
                if bool(self.identify_piece(pf, "both")):
                    return True
        return False

    def diagonal_blockage(self, begin_pos, end_pos):
        list_1=[begin_pos[0], end_pos[0]]; list_2=[begin_pos[1], end_pos[1]]
        for pf in self.platformlist:
            diff_x, diff_y = self.get_x_y(begin_pos, pf.id)
            if pf.id[0]>min(list_1) and pf.id[0]<max(list_1) and pf.id[1]>min(list_2) and pf.id[1]<max(list_2) and diff_x==diff_y:
                if bool(self.identify_piece(pf, "both")):
                    return True
        return False
    
    def get_x_y(self, begin_pos, end_pos, absolute=True):
            dict_alphabet={"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8, "I": 9, "J": 10}
            x=dict_alphabet[end_pos[0]]-dict_alphabet[begin_pos[0]]
            y=end_pos[1]-begin_pos[1]
            if absolute:
                diff_x=abs(x); diff_y=abs(y)
                return diff_x, diff_y
            else:
                return x, y

    def identify_platform_2(self, piece):
        for pf in self.platformlist:
            if pf.id==piece.coords:
                return pf

    def identify_platform_3(self, id):
        if type(id)==str:
            id = transform(id)

        for pf in self.platformlist:
            if pf.id==id:
                return pf
        return None


    def identify_king(self, turn):
        if turn=="white":
            list=self.piecelist_white
        else:
            list=self.piecelist_black

        for piece in list:
            if (piece.id=="King" or piece.id=="king") and piece.exist:
                return piece
        for piece in list:
            print(piece.id, piece.colour, piece.exist, piece.coords)
            print("---------------------------")

    def check_if_check(self, turn):
        dict={"white": self.piecelist_black, "black": self.piecelist_white}
        list=dict[turn]

        oppturn=None
        if turn=="white":
            oppturn="black"
        else:
            oppturn="white"

        king=self.identify_king(turn)
        king_platform=self.identify_platform_2(king)

        for piece in list:
            if piece.main_rule(piece.coords, king_platform, oppturn, psc=False) and piece.exist:
                return True
        return False

    def check_if_checkmate(self, turn):
        dict = {"black": self.piecelist_black, "white": self.piecelist_white}
        oppturn=None
        if turn=="white":
            oppturn="black"
        else:
            oppturn="white"
        for piece in dict[turn]:
            for pf in self.platformlist:
                if piece.main_rule(piece.coords, pf, turn) and piece.exist:
                    return False

        return True #checkmate lol

    def clear_all_platforms(self):
        for pf in self.platformlist:
            pf.clear()

    def deselect_all_pieces(self):
        for piece in self.piecelist:
            piece.selected=False

    def identify_selected_piece(self):
        for piece in self.piecelist:
            if piece.selected:
                return piece
        return None
            
    def clear(self):
        for piece in self.piecelist:
            piece.get_kicked()
            
class platform(Board):
    def __init__(self, x, y, xc, yc, im, master, sc=False):
        self.master=master
        self.width=self.master.width; self.canvas=self.master.canvas
        self.icd=create_icd(self.width)
        
        self.imb=Image.open("pfb.gif") #black
        self.imw=Image.open("pfw.gif") #white
        self.imdg=Image.open("pfdg.gif") #brown(black) own
        self.imlg=Image.open("pflg.gif") #brown(white) own
        self.imbs=Image.open("pfbs.gif") #dot(black)
        self.imws=Image.open("pfws.gif") #dot(white)

        #resizing images       
        self.imb=self.imb.resize((self.width, self.width));self.imw=self.imw.resize((self.width, self.width));self.imdg=self.imdg.resize((self.width, self.width))
        self.imlg=self.imlg.resize((self.width, self.width));self.imbs=self.imbs.resize((self.width, self.width));self.imws=self.imws.resize((self.width, self.width))
        
        #opening images        
        self.bgb=ImageTk.PhotoImage(self.imb);self.bgw=ImageTk.PhotoImage(self.imw);self.bgdg=ImageTk.PhotoImage(self.imdg);self.bglg=ImageTk.PhotoImage(self.imlg)
        self.bgbs=ImageTk.PhotoImage(self.imbs);self.bgws=ImageTk.PhotoImage(self.imws)

        #avoiding images getting to garbage
        self.canvas.pics.append(self.bgb);self.canvas.pics.append(self.bgw);self.canvas.pics.append(self.bgbs);self.canvas.pics.append(self.bgws)
        self.canvas.pics.append(self.bgdg);self.canvas.pics.append(self.bglg)
        
        self.imglist=[self.bgb, self.bgw, self.bgdg, self.bglg, self.bgbs, self.bgws]
        self.id=(x, y)
        self.xc=xc; self.yc=yc
        self.im=im
        self.sc=sc
        self.img=self.canvas.create_image(self.xc, self.yc, image=eval(self.im), anchor="nw")

    def clicked(self):
        if self.im=="self.bgw":
            self.canvas.itemconfig(self.img, image=self.imglist[3])
        else:
            self.canvas.itemconfig(self.img, image=self.imglist[2])

    def clickable(self):
        if self.im=="self.bgw": #white platform
            if bool(self.master.identify_piece(self, "both")): #piece on white platform
                self.canvas.itemconfig(self.img, image=self.imglist[3])
            else:  #no piece on white platform
                self.canvas.itemconfig(self.img, image=self.imglist[5])
        else:   #black platform
            if bool(self.master.identify_piece(self, "both")): #piece on black platform
                self.canvas.itemconfig(self.img, image=self.imglist[2])
            else:   #no piece on black platform
                self.canvas.itemconfig(self.img, image=self.imglist[4])
        self.sc=True

    def clear(self):
        self.sc=False
        if self.im=="self.bgw":
            self.canvas.itemconfig(self.img, image=self.imglist[1])
        if self.im=="self.bgb":
            self.canvas.itemconfig(self.img, image=self.imglist[0])
        
class Pieces(Board):
    def __init__(self, coords, colour, master):
        self.master=master
        self.coords=coords
        self.colour=colour
        self.selected=False
        self.exist=True
        self.drag=False
        self.icd=self.master.icd
        self.canvas=self.master.canvas

    def rule_own_piece(self, platform, turn):
        if bool(self.master.identify_piece(platform, turn)):
            return False
        return True

    def prevent_self_check(self, platform, turn, psc):
        if not psc:
            return True
        orig_coords=self.coords
        self.coords=platform.id
        bv=None

        if turn=="white":
            oppturn="black"
        else:
            oppturn="white"
        
        piece=self.master.identify_piece(platform, oppturn)
        if bool(piece):
            #if piece.id == "King" or piece.id == "king":
                #print("ALARM!!!!!!!!!!!!!!!!!!")
                #print(platform.id, turn, psc)
                #print(self.id, self.colour, self.exist)
                #print(piece.id, piece.colour, piece.exist)
            piece.exist=False
            
        if self.master.check_if_check(turn):
            bv=False
        else:
            bv=True
            
        self.coords=orig_coords
        if bool(piece):
            piece.exist=True
        if bv:
            return True
        return False

    def move(self, platform):
        #self.coords
        #platform.id
        #icd
        #goal: move self from <self.coords> to <platform.id> with translation of <icd>
        
        translated_begin_pos=self.icd[self.coords]
        translated_end_pos=self.icd[platform.id]
        diff_x=translated_end_pos[0]-translated_begin_pos[0]
        diff_y=translated_end_pos[1]-translated_begin_pos[1]
        self.coords=platform.id
        times=0
        self.canvas.move(self.img, diff_x, diff_y)

        if self.colour=="white": oppturn="black"
        else: oppturn="white"
            
        piece=self.master.identify_piece(platform, oppturn)
        if bool(piece):
            piece.get_kicked()

        if self.id=="Pawn":
            if self.colour=="white":
                if self.coords[1]==8:
                    self.convert_queen()
            elif self.colour=="black":
                if self.coords[1]==1:
                    self.convert_queen()

    def get_kicked(self):
        self.exist=False
        self.canvas.itemconfig(self.img, state="hidden") 


class Pawn(Pieces):
    def __init__(self, coords, colour, master):
        Pieces.__init__(self, coords, colour, master)
        self.id="Pawn"
        self.imstr=("C:\\Users\\Armani\\Downloads\\project chess\\chess pieces\\pawn %s.png" %(self.colour))
        self.im=Image.open(self.imstr)
        self.im=self.im.resize((self.master.width, self.master.width))
        self.image=ImageTk.PhotoImage(self.im)
        self.master.canvas.pics.append(self.image)
        self.img=self.canvas.create_image(self.icd[self.coords][0], self.icd[self.coords][1], image=self.image, anchor="nw")

    def main_rule(self, begin_pos, platform, turn, psc=True):
        end_pos=platform.id
        diff_x=self.master.get_x_y(begin_pos, end_pos, absolute=True)[0]; diff_y=self.master.get_x_y(begin_pos, end_pos, absolute=False)[1]
        if turn=="white":
            if diff_x==0 and diff_y==1:
                if self.rule_own_piece(platform, turn) and self.prevent_self_check(platform, turn, psc): 
                    if bool(self.master.identify_piece(platform, "black")):
                        return False
                    return True
            elif diff_x==0 and diff_y==2:
                if self.double(begin_pos, turn) and not self.master.vertical_blockage(begin_pos[0], begin_pos, end_pos) and self.prevent_self_check(platform, turn, psc):
                    if bool(self.master.identify_piece(platform, "both")):
                        return False
                    return True
            elif diff_y==1 and diff_x==1:
                if bool(self.master.identify_piece(platform, "black")) and self.prevent_self_check(platform, turn, psc):
                    return True
            
        else:
            if diff_x==0 and diff_y==-1:
                if self.rule_own_piece(platform, turn) and self.prevent_self_check(platform, turn, psc):
                    if bool(self.master.identify_piece(platform, "white")):
                        return False
                    return True
            elif diff_x==0 and diff_y==-2:
                if self.double(begin_pos, turn) and not self.master.vertical_blockage(begin_pos[0], begin_pos, end_pos) and self.prevent_self_check(platform, turn, psc):
                    if bool(self.master.identify_piece(platform, "both")):
                        return False
                    return True
            elif diff_y==-1 and diff_x==1:
                if bool(self.master.identify_piece(platform, "white"))and self.prevent_self_check(platform, turn, psc):
                    return True
        return False

    def double(self, begin_pos, turn):
        if turn=="white" and begin_pos[1]==2:
            return True
        elif turn=="black" and begin_pos[1]==7:
            return True
        return False

    def convert_queen(self):
        coords=self.coords
        colour=self.colour
        self.get_kicked()
        queen=Queen(coords, colour, self.master)
        if colour=="white":
            self.master.piecelist_white.append(queen)
        else:
            self.master.piecelist_black.append(queen)
        self.master.piecelist.append(queen)

class Rook(Pieces):
    def __init__(self, coords, colour, master):
        Pieces.__init__(self, coords, colour, master)
        self.id="Rook"
        self.imstr=("C:\\Users\\Armani\\Downloads\\project chess\\chess pieces\\rook %s.png" %(self.colour))
        self.im=Image.open(self.imstr)
        self.im=self.im.resize((self.master.width, self.master.width))
        self.image=ImageTk.PhotoImage(self.im)
        self.master.canvas.pics.append(self.image)
        self.img=self.canvas.create_image(self.icd[self.coords][0], self.icd[self.coords][1], image=self.image, anchor="nw")

    def main_rule(self, begin_pos, platform, turn, psc=True):
        end_pos=platform.id
        diff_x, diff_y=self.master.get_x_y(begin_pos, end_pos)
        if diff_x==0 and begin_pos!=end_pos:
            if self.rule_own_piece(platform, turn) and not self.master.vertical_blockage(begin_pos[0], begin_pos, end_pos) and self.prevent_self_check(platform, turn, psc):
                return True
        elif diff_y==0 and begin_pos!=end_pos:
            if self.rule_own_piece(platform, turn) and not self.master.horizontal_blockage(begin_pos[1], begin_pos, end_pos) and self.prevent_self_check(platform, turn, psc):
                return True
        return False

class Bishop(Pieces):
    def __init__(self, coords, colour, master):
        Pieces.__init__(self, coords, colour, master)
        self.id="Bishop"
        self.imstr=("C:\\Users\\Armani\\Downloads\\project chess\\chess pieces\\bishop %s.png" %(self.colour))
        self.im=Image.open(self.imstr)
        self.im=self.im.resize((self.master.width, self.master.width))
        self.image=ImageTk.PhotoImage(self.im)
        self.master.canvas.pics.append(self.image)
        self.img=self.canvas.create_image(self.icd[self.coords][0], self.icd[self.coords][1], image=self.image, anchor="nw")
        

    def main_rule(self, begin_pos, platform, turn, psc=True):
        end_pos=platform.id
        diff_x, diff_y=self.master.get_x_y(begin_pos, end_pos)
        if diff_x==diff_y:
            if self.rule_own_piece(platform, turn) and not self.master.diagonal_blockage(begin_pos, end_pos) and self.prevent_self_check(platform, turn, psc):
                return True
        return False
        
class Knight(Pieces):
    def __init__(self, coords, colour, master):
        Pieces.__init__(self, coords, colour, master)
        self.id="Knight"
        self.imstr=("C:\\Users\\Armani\\Downloads\\project chess\\chess pieces\\knight %s.png" %(self.colour))
        self.im=Image.open(self.imstr)
        self.im=self.im.resize((self.master.width, self.master.width))
        self.image=ImageTk.PhotoImage(self.im)
        self.master.canvas.pics.append(self.image)
        self.img=self.canvas.create_image(self.icd[self.coords][0], self.icd[self.coords][1], image=self.image, anchor="nw")

    def main_rule(self, begin_pos, platform, turn, psc=True):
        end_pos=platform.id
        diff_x, diff_y=self.master.get_x_y(begin_pos, end_pos)
        if (diff_x==2 and diff_y==1) or (diff_x==1 and diff_y==2):
            if self.rule_own_piece(platform, turn) and self.prevent_self_check(platform, turn, psc):
                return True
        return False

class Queen(Pieces):
    def __init__(self, coords, colour, master):
        Pieces.__init__(self, coords, colour, master)
        self.id="Queen"
        self.imstr=("C:\\Users\\Armani\\Downloads\\project chess\\chess pieces\\queen %s.png" %(self.colour))
        self.im=Image.open(self.imstr)
        self.im=self.im.resize((self.master.width, self.master.width))
        self.image=ImageTk.PhotoImage(self.im)
        self.master.canvas.pics.append(self.image)
        self.img=self.canvas.create_image(self.icd[self.coords][0], self.icd[self.coords][1], image=self.image, anchor="nw")

    def main_rule(self, begin_pos, platform, turn, psc=True):
        end_pos=platform.id
        diff_x, diff_y=self.master.get_x_y(begin_pos, end_pos)
        if diff_x==0 and begin_pos!=end_pos:
            if self.rule_own_piece(platform, turn) and not self.master.vertical_blockage(begin_pos[0], begin_pos, end_pos) and self.prevent_self_check(platform, turn, psc):
                return True
        elif diff_y==0 and begin_pos!=end_pos:
            if self.rule_own_piece(platform, turn) and not self.master.horizontal_blockage(begin_pos[1], begin_pos, end_pos) and self.prevent_self_check(platform, turn, psc):
                return True
        elif diff_x==diff_y and begin_pos!=end_pos:
            if self.rule_own_piece(platform, turn) and not self.master.diagonal_blockage(begin_pos, end_pos) and self.prevent_self_check(platform, turn, psc):
                return True
        return False

class King(Pieces):
    def __init__(self, coords, colour, master):
        Pieces.__init__(self, coords, colour, master)
        self.id="King"
        self.imstr=("C:\\Users\\Armani\\Downloads\\project chess\\chess pieces\\king %s.png" %(self.colour))
        self.im=Image.open(self.imstr)
        self.im=self.im.resize((self.master.width, self.master.width))
        self.image=ImageTk.PhotoImage(self.im)
        self.master.canvas.pics.append(self.image)
        self.img=self.canvas.create_image(self.icd[self.coords][0], self.icd[self.coords][1], image=self.image, anchor="nw")

    def main_rule(self, begin_pos, platform, turn, psc=True):
        end_pos=platform.id
        diff_x, diff_y=self.master.get_x_y(begin_pos, end_pos)
        if diff_x<=1 and diff_y<=1 and begin_pos!=end_pos:
            if self.rule_own_piece(platform, turn) and self.prevent_self_check(platform, turn, psc):
                return True
        return False


