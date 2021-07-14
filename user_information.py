import sqlite3
        

class Introduction:
    def __init__(self):
        self.con = sqlite3.connect("user_information.db", check_same_thread=False)
        self.cur = self.con.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS introductions (
            user text not null,
            content text not null
        )""")

    def fetch_introduction(self, user):
        self.cur.execute("SELECT content FROM introductions WHERE user = (?)", (user,))
        return self.cur.fetchone()[0]
    
    def update_introduction(self, user, content):
        if not self.has_introduction(user):
            self.cur.execute("INSERT INTO introductions VALUES (?, ?)", (user, content))
            self.con.commit()
        
        else:
            self.cur.execute("UPDATE introductions SET content = (?) WHERE user = (?)", (content, user))
            self.con.commit()


    def has_introduction(self, user):
        self.cur.execute("SELECT * FROM introductions WHERE user = (?)", (user,))
        return len(self.cur.fetchall()) == 1


class Topics:

    def __init__(self):
        self.con = sqlite3.connect("user_information.db", check_same_thread=False)
        self.cur = self.con.cursor()
        self.levels = ["Beginner", "Intermediate", "Advanced", "Expert", "Master"]

        self.cur.execute("""CREATE TABLE IF NOT EXISTS user_topics (
            user text not null,
            topic text not null,
            level integer
        )""")
    
    def has_added(self, user, topic):
        self.cur.execute("SELECT * FROM user_topics WHERE user = (?) AND topic = (?)", (user, topic))
        return len(self.cur.fetchall()) == 1

    def add(self, user, topic):
        self.cur.execute("INSERT INTO user_topics VALUES (?, ?, ?)", (user, topic, 0))
        self.con.commit()

    def delete(self, user, topic):
        self.cur.execute("DELETE FROM user_topics WHERE topic = (?) AND user = (?)", (topic, user))
        self.con.commit()
    
    def fetch_added(self, user):
        self.cur.execute("SELECT * FROM user_topics WHERE user = (?)", (user,))
        return list(map(lambda x: (x[1], self.levels[x[2]]), self.cur.fetchall()))
    
    def change_level(self, user, topic, to):
        self.cur.execute("UPDATE user_topics SET level = (?) WHERE topic = (?) AND user = (?)", (to, topic, user))
        self.con.commit()
