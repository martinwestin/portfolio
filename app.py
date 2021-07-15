from flask import Flask, render_template, redirect, url_for, session, request
from flask.helpers import flash
from flask_socketio import SocketIO, emit
from user_models import DBModels
from user_information import Introduction, Topics, Education
from direct_messages import Message, Messages
import hashlib
from datetime import date


app = Flask(__name__)

app.config["SECRET_KEY"] = b'Y\xbe\xbf7\xd7\x16\xcf\xee2z$\xae1\xca\x84\x890\x84=~@\xae\xabP'
socketio = SocketIO(app)

models_instance = DBModels()
user_info_instance = Introduction()
topics_instance = Topics()
education_instance = Education()
messages_instance = Messages()

active_rooms = {}


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        try:
            first_name = str(request.form["first_name"]).lower().title()
            last_name = str(request.form["last_name"]).lower().title()
            username = request.form["username"]
            password = request.form["password"]
            confirm = request.form["confirm"]
            question = request.form["question"]
            answer = request.form["answer"]
            if models_instance.username_available(username):
                if password == confirm:
                    m = hashlib.sha512()
                    m.update(bytes(password, "utf-8"))
                    password = models_instance.clean(m.digest())
                    m = hashlib.sha512()
                    m.update(bytes(answer.lower(), "utf-8"))
                    answer = models_instance.clean(m.digest())

                    models_instance.create_user(first_name, last_name, username, password, question, answer)
                    flash("Account created. You can now login.")
                    return render_template("index.html")

                flash("Make sure to confirm password.")
                return render_template("index.html")

            flash("Username not available")
            return render_template("index.html")
        except:
            username = request.form["login_username"]
            password = request.form["login_password"]
            m = hashlib.sha512()
            m.update(bytes(password, "utf-8"))
            password = models_instance.clean(m.digest())

            if models_instance.successful_login(username, password):
                session["user"] = username
                return redirect(url_for("portfolio"))
            
            flash("Account not found.")
            return render_template("index.html")

    return render_template("index.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/my_portfolio")
def portfolio():
    if "user" in session:
        user = session["user"]
        has_profile_pic = models_instance.user_has_profile_picture(user)
        profile_pic_id = models_instance.fetch_profile_picture_id(user) if has_profile_pic else None
        added_topics = topics_instance.fetch_added(user)
        education = education_instance.fetch_added(user)
        if not user_info_instance.has_introduction(user):
            user_info_instance.update_introduction(user, "")

        return render_template("portfolio.html", intro=user_info_instance.fetch_introduction(user), has_profile_pic=has_profile_pic, profile_pic_id=str(profile_pic_id), topics=added_topics, education=education, is_owner=True)
    
    flash("You have been logged out!")
    return redirect(url_for("index"))


@app.route("/portfolio/<other_user>")
def other_user_portfolio(other_user):
    if "user" in session:
        if models_instance.user_exists(other_user):
            if other_user != session["user"]:

                has_profile_pic = models_instance.user_has_profile_picture(other_user)
                profile_pic_id = models_instance.fetch_profile_picture_id(other_user) if has_profile_pic else None
                added_topics = topics_instance.fetch_added(other_user)
                education = education_instance.fetch_added(other_user)
                if not user_info_instance.has_introduction(other_user):
                    user_info_instance.update_introduction(other_user, "")

                return render_template("portfolio.html", intro=user_info_instance.fetch_introduction(other_user), has_profile_pic=has_profile_pic, profile_pic_id=str(profile_pic_id), topics=added_topics, education=education, is_owner=False, user=models_instance.fetch_first_name(other_user), username=other_user)
            return redirect(url_for("portfolio"))

        return "The requested user could not be found."
    
    flash("You have been logged out!")
    return redirect(url_for("index"))


@app.route("/messages/<other_user>")
def messages(other_user):
    if "user" in session:
        user = session["user"]
        room_id = messages_instance.fetch_room_id(user, other_user)
        messages = messages_instance.fetch_messages(room_id)
        return render_template("messages.html", logged_user=user, _with=other_user, first_name=models_instance.fetch_first_name(other_user), messages=messages)

    flash("You have been logged out!")
    return redirect(url_for("index"))


@socketio.on("select_profile_pic")
def set_profile_picture(msg):
    if "user" in session:
        img = msg["img"]
        file_name = msg["name"]
        valid_file_endings = ["jpg", "png", "jpeg", "gif"]
        if file_name.split(".")[-1] in valid_file_endings:
            user = session["user"]
            models_instance.add_user_photo(user, img)
            emit("reload", room=request.sid)
        else:
            emit("non_valid_file", room=request.sid)


@socketio.on("save_user_introduction")
def save_user_introduction(msg):
    if "user" in session:
        content = msg["content"]
        user = session["user"]
        user_info_instance.update_introduction(user, content)
        emit("reload", room=request.sid)

@socketio.on("new_topic")
def new_merit(msg):
    if "user" in session:
        topic = msg["data"]
        user = session["user"]
        if not topics_instance.has_added(user, topic):
            topics_instance.add(user, topic)
            emit("reload", room=request.sid)
        else:
            emit("has_already_added", {"type": "merit"}, room=request.sid)


@socketio.on("change_level")
def change_level(msg):
    if "user" in session:
        to = msg["type"]
        topic = msg["topic"]
        current_level = msg["current"]
        user = session["user"]
        current_index = topics_instance.levels.index(current_level)
        
        if current_index + to < 5 and current_index + to > -1:
            topics_instance.change_level(user, topic, current_index + to)
            emit("reload", room=request.sid)


@socketio.on("change_education_level")
def change_education_level(msg):
    if "user" in session:
        to = msg["type"]
        topic = msg["topic"]
        current_level = msg["current"]
        user = session["user"]
        current_index = education_instance.levels.index(current_level)
        if current_index + to < 6 and current_index + to > -1:
            education_instance.change_level(user, topic, current_index + to)
            emit("reload", room=request.sid)


@socketio.on("delete_merit")
def delete_merit(msg):
    if "user" in session:
        topic = msg["topic"]
        user = session["user"]

        if topics_instance.has_added(user, topic):
            topics_instance.delete(user, topic)
            emit("reload", room=request.sid)

@socketio.on("delete_education_merit")
def delete_education_merit(msg):
    if "user" in session:
        topic = msg["topic"]
        user = session["user"]
        if education_instance.has_added(user, topic):
            education_instance.delete(user, topic)
            emit("reload", room=request.sid)


@socketio.on("new_education_merit")
def new_education_merit(msg):
    if "user" in session:
        topic = msg["data"]
        user = session["user"]
        if not education_instance.has_added(user, topic):
            education_instance.add(user, topic)
            emit("reload", room=request.sid)
        else:
            emit("has_already_added", {"type": "educational merit"}, room=request.sid)


@socketio.on("user_search")
def user_search(msg):
    if "user" in session:
        search = msg["user"]
        user = session["user"]
        # keeping a list of all the users that could show up in this search.
        # if the user searched for "martin", and there is a user with username "martin",
        # that user will show up. Other users, that perhaps have "martin" as their first
        # name, will also show up.
        relevant_results = []
        if models_instance.user_exists(search):
            relevant_results.append(search)
        relevant_results += models_instance.fetch_relevant_search_results(search)
        # convert to a set because the same username could show up twice if the searched user has a similar username and first/last name
        relevant_results = list(set(list(filter(lambda x: x != user, relevant_results))))
        relevant_results = list(map(lambda x: (models_instance.fetch_first_name(x), models_instance.fetch_last_name(x), x), relevant_results))

        emit("search_response", {"results": relevant_results}, room=request.sid)


@socketio.on("connected_dm")
def connected_dm(msg):
    if "user" in session:
        user = session["user"]
        other_user = msg["_with"]
        active_rooms[user] = [messages_instance.fetch_room_id(user, other_user), request.sid]


@socketio.on("new_message")
def new_message(msg):
    if "user" in session:
        user = session["user"]
        content = msg["data"]
        active_room_id = active_rooms[user][0]

        message = Message(content, user)
        message.add(active_room_id)
        rooms = list(filter(lambda x: x[0] == active_room_id, list(map(lambda x: active_rooms[x], active_rooms))))
        sids = list(map(lambda x: x[1], rooms))
        for sid in sids:
            emit("new_message", {"content": content, "sender": user, "published": str(date.today())}, room=sid)


if __name__ == "__main__":
    socketio.run(app, debug=True)
