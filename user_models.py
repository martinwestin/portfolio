import sqlite3
from PIL import Image, ImageDraw
import numpy as np
import os
import re
from base64 import b64encode
from difflib import SequenceMatcher


class DBModels:
    def __init__(self):
        self.con = sqlite3.connect("data.db", check_same_thread=False)
        self.cur = self.con.cursor()
        
        self.cur.execute("""CREATE TABLE IF NOT EXISTS users (
            first_name text not null,
            last_name text not null,
            username text not null,
            password text not null
        )""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS images (
            user text not null,
            image_id integer primary key autoincrement
        )""")
    
    def create_user(self, first_name, last_name, username, password):
        self.cur.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (first_name, last_name, username, password))
        self.con.commit()
    
    def successful_login(self, username, password):
        self.cur.execute("SELECT * FROM users WHERE username = (?) AND password = (?)", (username, password))
        return len(self.cur.fetchall()) == 1
    
    def username_available(self, username):
        self.cur.execute("SELECT * FROM users WHERE username = (?)", (username,))
        return len(self.cur.fetchall()) == 0
    
    def add_user_photo(self, user, img_data):
        if self.user_has_profile_picture(user):
            self.delete_profile_picture(user)
        
        self.cur.execute("INSERT INTO images VALUES (?, ?)", (user, None))
        self.con.commit()
        id = self.cur.lastrowid
        
        # get the last image id
        self.cur.execute("SELECT * FROM images")
        PATH = f"static/images/user_pic{id}.png"
        with open(PATH, "wb") as file:
            file.write(img_data)
        
        img = Image.open(PATH).convert("RGB")
        np_image = np.array(img)
        height, width = img.size

        # create same size alpha layer with circle
        alpha = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(alpha)
        draw.pieslice([0, 0, width, width], 0, 360, fill=255)
        np_alpha = np.array(alpha)
        np_image = np.dstack((np_image, np_alpha))
        Image.fromarray(np_image).save(PATH)
    
    def user_has_profile_picture(self, user):
        self.cur.execute("SELECT * FROM images WHERE user = (?)", (user,))
        return len(self.cur.fetchall()) == 1
    
    def fetch_profile_picture_id(self, user):
        if self.user_has_profile_picture(user):
            self.cur.execute("SELECT image_id FROM images WHERE user = (?)", (user,))
            return self.cur.fetchone()[0]
        
        raise Exception("the user has not yet added a profile picture.")
    
    def delete_profile_picture(self, user):
        PATH = f"static/images/user_pic{self.fetch_profile_picture_id(user)}.png"
        self.cur.execute("DELETE FROM images WHERE user = (?)", (user,))
        self.con.commit()
        os.remove(PATH)
    
    def user_exists(self, user):
        self.cur.execute("SELECT * FROM users WHERE username = (?)", (user,))
        return len(self.cur.fetchall()) == 1
    
    def clean(self, str):
        return " ".join(re.findall(r"[a-zA-Z0-9]+", b64encode(str).decode("utf-8")))
    
    def fetch_first_name(self, username):
        self.cur.execute("SELECT first_name FROM users WHERE username = (?)", (username,))
        return self.cur.fetchone()[0]
    
    def fetch_last_name(self, username):
        self.cur.execute("SELECT last_name FROM users WHERE username = (?)", (username,))
        return self.cur.fetchone()[0]
    
    def fetch_relevant_search_results(self, searched):
        self.cur.execute("SELECT * FROM users")
        return list(map(lambda x: x[2], list(filter(lambda x: SequenceMatcher(None, searched.lower(), " ".join([x[0], x[1]]).lower()).ratio() >= 0.8 or 
        SequenceMatcher(None, searched.lower(), x[0].lower()).ratio() >= 0.8 or SequenceMatcher(None, searched.lower(), x[1].lower()).ratio() >= 0.8
        or searched.lower() in " ".join([x[0], x[1]]).lower(), self.cur.fetchall()))))
