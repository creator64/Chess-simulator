import sqlite3
import pickle

class database:
    def __init__(self, database):
        self.database=database
        self.connect(self.database)

    def connect(self, database):
        self.conn=sqlite3.connect(database)
        self.c=self.conn.cursor()

    def insert_new(self, table, board_item): #rowid NOT included in board_item
        board_item[1]=pickle.dumps(board_item[1])
        board_item[2]=str(board_item[2])
        board_item=tuple(board_item)
        self.c.execute("INSERT INTO %s VALUES (?,?,?)" %(table), board_item)
        self.conn.commit()

    def update(self, table, index, changes={}):
        try: changes["data"]=pickle.dumps(changes["data"])
        except: pass

        try: changes["date"]=str(changes["date"])
        except: pass
        
        for change in changes:
            self.c.execute("UPDATE %s SET %s=? WHERE rowid=?" %(table, change), (changes[change], str(index)))
        self.conn.commit()

    def delete(self, table, index):
        self.c.execute("DELETE FROM %s WHERE rowid=?" %(table), str(index))
        self.conn.commit()

    def load_all(self, table):
        self.c.execute("SELECT rowid, * FROM %s" %(table))
        board_list=self.c.fetchall()
        for board in board_list:
            try:
                new_board=list(board)
                board_list[board_list.index(board)]=new_board
                data=board_list[board_list.index(new_board)][2]
                c=pickle.loads(data)
                board_list[board_list.index(new_board)][2]=c
                date=board_list[board_list.index(new_board)][3]
                board_list[board_list.index(new_board)][3]=eval(date)
            except:
                pass
                      
        return board_list

#d=database("chess.db")
#d.c.execute("DELETE FROM boards WHERE name='lol'")
#d.conn.commit()
#b=d.load_all("boards")
#print(b)
