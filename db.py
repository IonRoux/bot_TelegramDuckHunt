import sqlite3


class DBHelper:
    def __init__(self, dbname="ducksettings.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)
        stmt = "CREATE TABLE IF NOT EXISTS 'chats' (chat_id string, chat_name string, duckprob integer, ducktime integer, duckwaittime integer, duckdeployed boolean, duckenabled boolean, duckflyaway integer, nextroll integer, logging boolean, init boolean, setting boolean, roll boolean, shots boolean, newuser boolean, timer boolean)"
        self.conn.execute(stmt)

    def setup(self, chat, chat_name):
        stmt1 = "INSERT INTO  'chats' (chat_id, chat_name, duckprob, ducktime, duckwaittime, duckdeployed, duckenabled, duckflyaway, nextroll, logging, init, setting, roll, shots, newuser, timer) VALUES ({0}, '{1}', 30, 30, 30, 'false', 'false', '0', '0', 'true', 'true', 'true', 'true', 'true', 'true', 'true')".format(chat, chat_name)
        stmt3 = "CREATE TABLE IF NOT EXISTS 'scores{0}' (player_id integer, score integer)".format(chat)
        self.conn.execute(stmt1)
        self.conn.execute(stmt3)
        self.conn.commit()
    

    def set(self, chatid, setting, value):
        stmt = "UPDATE chats SET {0} = '{2}' WHERE chat_id = {1}".format(setting, chatid, value)
        self.conn.execute(stmt)
        self.conn.commit()

    def get(self, chatid, setting):
        stmt = "SELECT {1} FROM chats WHERE chat_id= {0}".format(chatid, setting)
        self.conn.execute(stmt)
        self.conn.commit()
        return [x[0] for x in self.conn.execute(stmt)]        
        
    def get_chats(self):
        stmt = "SELECT chat_id FROM chats"
        self.conn.execute(stmt)
        self.conn.commit()
        return [x[0] for x in self.conn.execute(stmt)]    

    def newchat(self, chat):
        stmt = "SELECT count(*) FROM chats WHERE chat_id = {0} ".format(chat)
        return [x[0] for x in self.conn.execute(stmt)]

    def newuser(self, chat, user):
        stmt = "SELECT count(*) FROM 'scores{0}' WHERE player_id = {1} ".format(chat, user)
        return [x[0] for x in self.conn.execute(stmt)]
    
    def adduser(self, chat, user):
        stmt = "INSERT INTO  'scores{0}' (player_id, score) VALUES ({1}, '0')".format(chat, user)
        self.conn.execute(stmt)
        self.conn.commit()
    
    def scoreset(self, chat, user, score):
        stmt = "UPDATE 'scores{0}' SET score = '{2}' WHERE player_id = {1}".format(chat, user, score)
        self.conn.execute(stmt)
        self.conn.commit()
    def scoreget(self, chat, user):
        stmt = "SELECT score FROM 'scores{0}' WHERE player_id= {1}".format(chat, user)
        self.conn.execute(stmt)
        self.conn.commit()
        return [x[0] for x in self.conn.execute(stmt)]