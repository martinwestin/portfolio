import sqlite3
from datetime import date


class DBConnection:
    def __init__(self):
        self.con = sqlite3.connect("messages.db", check_same_thread=False)
        self.cur = self.con.cursor()

        self.cur.execute("""CREATE TABLE IF NOT EXISTS messages (
            content text not null,
            sent_date text not null,
            sender text not null,
            room_id intege not null,
            message_id integer primary key autoincrement
        )""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS rooms (
            user_1 text not null,
            user_2 text not null,
            room_id integer primary key autoincrement
        )""")


class Message(DBConnection):
    def __init__(self, content, sender):
        super().__init__()
        self.content = content
        self.sender = sender

    def add(self, room_id):
        current_date = date.today()
        self.cur.execute("INSERT INTO messages VALUES (?, ?, ?, ?, ?)", (self.content, current_date, self.sender, room_id, None))
        self.con.commit()


class Messages(DBConnection):
    def __init__(self):
        super().__init__()
    
    def create_dm_room(self, user, _with):
        self.cur.execute("INSERT INTO rooms VALUES (?, ?, ?)", (user, _with, None))
        self.con.commit()
    
    def fetch_messages(self, room_id):
        self.cur.execute("SELECT * FROM messages WHERE room_id = (?)", (room_id,))
        return self.cur.fetchall()

    def fetch_room_id(self, user, _with):
        self.cur.execute("SELECT * FROM rooms")
        self.cur.execute("SELECT room_id FROM rooms WHERE user_1 = (?) AND user_2 = (?) OR user_1 = (?) AND user_2 = (?)", (user, _with, _with, user))
        all = self.cur.fetchall()
        if len(all) == 0:
            self.create_dm_room(user, _with)

        self.cur.execute("SELECT room_id FROM rooms WHERE user_1 = (?) AND user_2 = (?) OR user_1 = (?) AND user_2 = (?)", (user, _with, _with, user))
        return self.cur.fetchone()[0]
