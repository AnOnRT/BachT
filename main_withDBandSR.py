from flask import Flask, copy_current_request_context, render_template, request, redirect, session, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
from flask_socketio import emit
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

import random
from string import ascii_letters, ascii_lowercase, ascii_uppercase

from _check_spotify import *
from SongRecommender.featurizer import *
from SongRecommender.song_recommendations import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////Path/db/chat.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.config["SECRET_KEY"] = "hermes"
socketio = SocketIO(app)

# client_id = "***"
# client_secret = "***"

client_id = "***"
client_secret = "***"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    messages = db.relationship('Message', backref='user', lazy=True)
    ratings = db.relationship('Rating', backref='user', lazy=True)
    

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

room_songs = db.Table('room_songs',
    db.Column('room_id', db.Integer, db.ForeignKey('room.id'), primary_key=True),
    db.Column('song_id', db.Integer, db.ForeignKey('song.id'), primary_key=True)
)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(80), unique=True, nullable=False)
    max_members = db.Column(db.Integer, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    messages = db.relationship('Message', backref='room', lazy=True)
    songs = db.relationship('Song', secondary=room_songs, lazy='subquery', backref=db.backref('rooms', lazy=True))
    group_full_message_sent = db.Column(db.Boolean, default=False)
    pinned_message = db.Column(db.String(1000))


class Membership(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), primary_key=True)
    joined_message_sent = db.Column(db.Boolean, default=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    spotify_id = db.Column(db.String(200), nullable=False, unique=True)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)

class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    # Store Spotify song IDs as strings without a foreign key constraint
    spotify_song_id = db.Column(db.String(200), nullable=False)

    

@app.route("/", methods=["GET", "POST"])
def start():
    # Check if the user is logged in
    if 'user_id' not in session:
        # User is not logged in, redirect to login page
        return redirect(url_for('login'))
    else:
        # User is logged in, render the home page
        return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email, username=username).first()
        if user and user.check_password(password):
            # User login logic here, like storing user ID in session
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            return 'Invalid email or password.'

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user:
            return 'Email already registered.'

        user = User.query.filter_by(username=username).first()
        if user:
            return 'Username already taken.'
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('signup.html')


def generate_unique_code(length):
    while True:
        code = "".join(random.choices(ascii_uppercase, k=length))
        existing_room = Room.query.filter_by(code=code).first()
        if existing_room is None:
            return code

def add_song_if_not_exists(name, spotify_id):
    existing_song = Song.query.filter_by(spotify_id=spotify_id).first()
    if not existing_song:
        new_song = Song(name=name, spotify_id=spotify_id)
        db.session.add(new_song)
        db.session.commit()
        return new_song
    return existing_song

def assign_songs_to_room(room, song_ids):
    set_song_ids = set(song_ids)
    for song_id in set_song_ids:
        song = Song.query.get(song_id)
        if song:
            room.songs.append(song)
    db.session.commit()

@app.route('/home', methods=["POST", "GET"])
def home():
    # session.clear()
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    if user is None:
        # User not found, possibly log out and redirect to login page
        session.clear()
        return redirect(url_for('login'))
    
    if request.method == "POST":
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)
        max_members = request.form.get("max_members", type=int)
        # #print("Steem")
        
        if join and not code:
            #print("Steem1")
            return "Please enter a room code."
            # return render_template("home.html", error="Please enter a room code.", code=code)

        if create != False:
            if max_members == None:
                return "Please enter a maximum number of members."
                # return render_template("home.html", error="Please enter a maximum number of members.")
            
            #print("Steem4")

            room_code = generate_unique_code(6)
            new_room = Room(code=room_code, max_members=max_members, admin_id=session['user_id'])
            db.session.add(new_room)
            db.session.commit()

            new_membership = Membership(user_id=user_id, room_id=new_room.id)
            db.session.add(new_membership)
            db.session.commit()

            song_ids = []  # Replace with actual logic to select song IDs
            song_wizard = SongWizard(client_id, client_secret)
            songs_to_rate = song_wizard.get_random_song_from_each_playlist()

            for song_info in songs_to_rate:  # Assume get_songs() fetches song data
                song = add_song_if_not_exists(song_info['name'], song_info['spotify_id'])
                song_ids.append(song.id)
            assign_songs_to_room(new_room, song_ids)

            session["room_code"] = room_code

            return redirect(url_for("rate_songs", code=room_code))
        
        if join != False and code:
            room = Room.query.filter_by(code=code).first()
            if room is None:
                #print("Steem5")
                return "Room does not exist."
                # return render_template("home.html", error="Room does not exist.", code=code)
            
            member_count = Membership.query.filter_by(room_id=room.id).count()
            existing_membership = Membership.query.filter_by(user_id=user_id, room_id=room.id).first()
            if not existing_membership:
                if member_count >= room.max_members:
                    return "The room is full"
                
                new_membership = Membership(user_id=user_id, room_id=room.id)
                db.session.add(new_membership)
                db.session.commit()

                # join_message = f"{user.username} has joined the group."
                # socketio.emit('receive_message', {'msg': f'{user.username}: {join_message}'}, room=room_code)

                # # Optionally, you could save this message to the database as well
                # new_message = Message(content=join_message, user_id=user_id, room_id=room.id)
                # db.session.add(new_message)
                # db.session.commit() 
                
                session["room_code"] = code
                return redirect(url_for("rate_songs", code=code))
            else:
                session["room_code"] = code
                return redirect(url_for("rate_songs", code=code))
        
    #print("Steem8")
    # Query the memberships for the current user
    memberships = Membership.query.filter_by(user_id=user_id).all()

    # Get the rooms for each membership
    groups = []
    for membership in memberships:
        room = Room.query.get(membership.room_id)
        if room:
            groups.append({'code': room.code, 'id': room.id})

    return render_template("home.html", user=user, groups=groups)

@app.route("/rate_songs/<code>")
def rate_songs(code):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']

    room = Room.query.filter_by(code=code).first()
    if not room:
        return redirect(url_for('home'))
    
    songs = room.songs
    existing_ratings = Rating.query.filter_by(user_id=user_id, room_id=room.id).all()
    if existing_ratings:
        # User has already rated songs for this room, redirect to chat
        return redirect(url_for('room', code=code))  # Replace 'chat' with your chat route

    return render_template("rate_songs.html", songs=songs, code=code)

@app.route("/submit_ratings/<code>", methods=["POST"])
def submit_ratings(code):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    room = Room.query.filter_by(code=code).first()
    if not room:
        return redirect(url_for('home'))
    
    existing_ratings = Rating.query.filter_by(user_id=user_id, room_id=room.id).all()
    if existing_ratings:
        # User has already rated songs for this room, redirect to chat
        return redirect(url_for('room', code=code))  # Replace 'chat' with your chat route
    
    for song in room.songs:
        rating_value = request.form.get(song.spotify_id)
        if rating_value:
            rating = Rating(
                value=int(rating_value),
                user_id=user_id,
                song_id=song.id,
                room_id=room.id
            )
            db.session.add(rating)
        # #print(song.name, str(rating_value))
        db.session.commit()
        # return redirect(url_for('home'))  # Redirect to chat after submitting ratings

    # Redirect to the chat room after storing ratings
    return redirect(url_for('room', code=code))

@app.route('/room/<code>')
def room(code):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.query.get(user_id)
    room = Room.query.filter_by(code=code).first()

    if not room:
        # Room not found, redirect to home or appropriate page
        return redirect(url_for('home'))

    # Check if user is a member of the room
    membership = Membership.query.filter_by(user_id=user_id, room_id=room.id).first()
    if not membership:
        # User is not a member of the room, handle accordingly
        return "Access Denied", 403
    
    # Fetch past messages
    past_messages = Message.query.filter_by(room_id=room.id).all()

    # Retrieve room members
    memberships = Membership.query.filter_by(room_id=room.id).all()
    members = [User.query.get(membership.user_id) for membership in memberships]

    # Retrieve songs and user's ratings
    songs = room.songs
    user_ratings = Rating.query.filter_by(user_id=user_id, room_id=room.id).all()
    ratings_dict = {rating.song_id: rating.value for rating in user_ratings}

    return render_template('room.html', room=room, user=user, past_messages=past_messages, members=members, songs=songs, ratings=ratings_dict)
    # return render_template('room.html', room=room, user=user, past_messages=past_messages)


def generate_recommendations(room_id, song_ratings):
    # Your algorithm to generate recommendations
    def calculate_overall_average(song_ratings):
        total_sum = 0
        total_count = 0
        for ratings in song_ratings.values():
            total_sum += sum(ratings)
            total_count += len(ratings)
        return total_sum / total_count if total_count else 0
    
    def filter_songs_based_on_ratings(song_ratings, relative_threshold=0.10):
        overall_average = calculate_overall_average(song_ratings)
        threshold = overall_average * (1 + relative_threshold)
        
        selected_songs = []
        for spotify_id, ratings in song_ratings.items():
            average_rating = sum(ratings) / len(ratings) if ratings else 0
            if average_rating >= threshold:
                selected_songs.append(spotify_id)
        return selected_songs
    
    selected_songs = filter_songs_based_on_ratings(song_ratings)
    song_wizard = SongWizard(client_id, client_secret)
    # recommendations = song_wizard.get_recommendations(list(song_ratings.keys()), 2)
    recommendations = song_wizard.get_recommendations(selected_songs, 3)

    
    # Save recommendations to the database
    for song in recommendations:
        # #print(song['name'], song['spotify_id'])
        new_recommendation = Recommendation(room_id=room_id, spotify_song_id=song['spotify_id'])
        db.session.add(new_recommendation)
    db.session.commit()
    
    # Return the list of recommendations (or the IDs or any identifier)
    return recommendations


@socketio.on('join')
def on_join(data):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    room_code = data['room']
    room = Room.query.filter_by(code=room_code).first()
    if not room:
        return  redirect(url_for('home'))

    user_id = session.get('user_id')
    user = User.query.get(user_id)

    membership = Membership.query.filter_by(user_id=user_id, room_id=room.id).first()
    if not membership:
        # User is not a member of the room, handle accordingly
        return "Access Denied", 403
    
    join_room(room_code)

    # memberships = Membership.query.filter_by(room_id=room.id).all()
    # members = [{'username': User.query.get(membership.user_id).username, 'id': membership.user_id} for membership in memberships]
    # emit('update_members', {'members': members}, room=room_code)

    # Check if the room is full
    membership = Membership.query.filter_by(user_id=user_id, room_id=room.id).first()
    if membership and not membership.joined_message_sent:
        join_message = f"Joined the group."
        emit('receive_message', {'msg': f'{new_message.user.username}: {join_message}'}, room=room_code)
        # emit('receive_message', {'msg': join_message}, room=room_code)
        membership.joined_message_sent = True
        db.session.commit()
        new_message = Message(content=join_message, user_id=user.id, room_id=room.id)
        db.session.add(new_message)
        db.session.commit()

    member_count = Membership.query.filter_by(room_id=room.id).count()
    if member_count >= room.max_members:
        # Room is full - send a message to the room from the admin
        admin_message = "The group is now full. Let's get started!"
        admin = User.query.get(room.admin_id)
        if admin and not room.group_full_message_sent:

            songs = room.songs

            # Retrieve all ratings for each song associated with the room
            song_ratings = {}
            for song in songs:
                ratings = Rating.query.filter_by(song_id=song.id, room_id=room.id).all()
                if ratings:
                    # Use Spotify ID as the key
                    song_ratings[song.spotify_id] = [rating.value for rating in ratings]

            
            recommendations = generate_recommendations(room.id, song_ratings)
            recommendations_link = url_for('view_recommendations', code=room_code, _external=True)
            admin_message = f"The group is now full. Let's get started! View recommendations: {recommendations_link}"


            new_message = Message(content=admin_message, user_id=admin.id, room_id=room.id)
            db.session.add(new_message)
            db.session.commit()

            room.pinned_message = admin_message
            db.session.commit()
            emit('receive_message', {'msg': f'{admin.username}: {admin_message}', 'pinned':True}, room=room_code)
            # Update the flag to indicate the message has been sent
            room.group_full_message_sent = True
            db.session.commit()
            # emit('receive_message', {'msg': f'{admin.username}: {admin_message}'}, room=room_code)
    

    if room.pinned_message:
        emit('receive_message', {'msg': room.pinned_message, 'pinned': True}, room=room_code)
    # Additional logic for when a user joins a room

@socketio.on('send_message')
def handle_send_message_event(data):
    room_code = data['room']
    message_content = data['data']
    user_id = session.get('user_id')

    room = Room.query.filter_by(code=room_code).first()
    if not room or not user_id:
        return redirect(url_for('home'))

    if len(message_content) == 0:
        return
    new_message = Message(content=message_content, user_id=user_id, room_id=room.id)
    db.session.add(new_message)
    db.session.commit()

    emit('receive_message', {'msg': f'{new_message.user.username}: {message_content}'}, room=room_code)
    


@app.route('/recommendations/<code>')
def view_recommendations(code):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.query.get(user_id)
    room = Room.query.filter_by(code=code).first()

    if not room:
        # Room not found, redirect to home or appropriate page
        return redirect(url_for('home'))

    # Check if user is a member of the room
    membership = Membership.query.filter_by(user_id=user_id, room_id=room.id).first()
    if not membership:
        # User is not a member of the room, handle accordingly
        return "Access Denied", 403
    
    # Query recommendations from the database
    recommendations = Recommendation.query.filter_by(room_id=room.id).all()
    return render_template('recommendations.html', recommendations=recommendations)

@socketio.on('leave')
def on_leave(data):
    room_code = data['room']
    leave_room(room_code)

    #room = Room.query.filter_by(code=room_code).first()
    # if room:
    #     memberships = Membership.query.filter_by(room_id=room.id).all()
    #     members = [{'username': User.query.get(membership.user_id).username, 'id': membership.user_id} for membership in memberships]
    #     emit('update_members', {'members': members}, room=room_code)
        # for i in members:
        #     #print(i['username'])



@app.route('/logout')
def logout():
# Clear the user's session
    session.clear()
    # Redirect to the login page or another appropriate page
    return redirect(url_for('login'))


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    # db.create_all()
    socketio.run(app, debug=True, port=8000)