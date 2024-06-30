from datetime import datetime
from flask import Flask, request, render_template, url_for, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from os.path import join, abspath, dirname
from init_db import create_table_and_load_data
import pandas as pd, plotly.express as px
import plotly, json
from flask import jsonify
import logging, os
import psycopg2

# set up logging to file
logging.basicConfig(
     filename='log_flaskedge.log',
     level=logging.INFO, 
     format= '[%(asctime)s] [%(levelname)s] {%(pathname)s:%(lineno)d} - %(message)s',
     datefmt='%H:%M:%S'
 )

# set up logging to console
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)

# set a format which is simpler for console use
formatter = logging.Formatter('[%(asctime)s] {%(pathname)s:%(lineno)d} [%(levelname)s] - %(message)s')
console.setFormatter(formatter)

# add the handler to the root logger
logging.getLogger('').addHandler(console)

logger = logging.getLogger(__name__)



basedir = abspath(dirname(__file__))

app = Flask(__name__)
app.secret_key = "FLASK_APP_SECRET_KEY"

##### INITIALIZE DB ##########
logger.info('Setting up database')
POSTGRES_PASSWORD=os.getenv("POSTGRES_ROOT_PASSWORD")
POSTGRES_USER_NAME=os.getenv("POSTGRES_USER_NAME")
POSTGRES_DB_NAME=os.getenv("POSTGRES_DB_NAME")

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{POSTGRES_USER_NAME}:{POSTGRES_PASSWORD}@postgres-service:5432/{POSTGRES_DB_NAME}' #'sqlite:///' + join(basedir,"edgeapi.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Rooms(db.Model):
    # Inherit the db.Model to this class.

    id = db.Column(db.Integer,primary_key=True)
    room_name = db.Column(db.String(200),nullable=False, unique=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    room_id = db.relationship('Temperatures', cascade='all,delete' ,backref='rooms')

    def __repr__(self):
        logger.info(f'Creating new room {self.room_name}')
        return f"<Rooms {self.room_name}>"

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Temperatures(db.Model):

    id = db.Column(db.Integer,primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    temperature = db.Column(db.Float, nullable=False)
    room_id = db.Column(db.Integer,db.ForeignKey('rooms.id'), nullable=False)
    # user_id = db.Column(db.Integer,db.ForeignKey('users.id'), nullable=False)


    def __repr__(self) -> str:
        logger.info(f'Setting temp={self.temperature} on room={self.room_id}')
        return f"<Temperatures {self.room_id} {self.temperature}>"

class Users(db.Model):
    id = db.Column(db.Integer,primary_key=True, autoincrement=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def __repr__(self) -> str:
        logger.info(f'Setting user {self.username}')
        return f"<Users {self.username} {self.password_hash}>"
    
create_table_and_load_data(app, db, Rooms, Temperatures, Users)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = generate_password_hash(password)

        new_user = Users(username=username, password_hash=password_hash)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('You have successfully signed up! Login NOW', 'success')
            logger.info(f'New user "{username}" added')
            return redirect("/login")

        except Exception as e:
            db.session.rollback()
            if 'psycopg2.errors.UniqueViolation' in e:
                logger.error(f"Error User already exists: {e}")
                flash(f'User "{username}" already exists', 'error')
            else:
                logger.error(f"Error signing up: {e}")
                flash('Sign up failed', 'error')
            return redirect(url_for('signup'))
 
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Users.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            logger.info(f'"{username}" successfully logged in')
            flash('You have successfully logged in!', 'success')
            return redirect("/rooms")
        else:
            logger.error(f'Authentication failed for {username}')
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
        
    return render_template('login.html')

@app.route("/")
def index():
    logger.info('Redirect login page')
    return redirect('/login')

@app.route("/rooms", methods=['GET'])
def get_rooms():
    if request.method == "GET":
        logger.info('Fetching all rooms')
        rooms = Rooms.query.order_by(Rooms.date).all()
        
        logger.debug('Rendering all rooms')
        return render_template('index.html',rooms=rooms)

@app.route("/room/create", methods=['POST'])
def add_room():
    room_name = request.form['room_name']
    if request.method == "POST":
        new_room = Rooms(room_name=room_name)

        try:
            db.session.add(new_room)
            db.session.commit()
            return redirect("/rooms")
        except Exception as e:
            return {"message":f"Room add failed {e}"}
    else:
        return {"message":"Does not support GET"}

@app.route("/rooms/update/<int:room_id>", methods=['POST','GET'])
def update_room(room_id):
    room = Rooms.query.get_or_404(room_id)

    if request.method == "POST":
        room.room_name = request.form['room_name']

        try:
            db.session.commit()
            return redirect("/rooms")
        except Exception as e:
            return {"message":f"Room update failed {e}"}
    else:
        return render_template('update_room.html',room=room)

@app.route("/rooms/delete/<int:room_id>", methods=['GET'])
def delete_room(room_id):
    room = Rooms.query.get_or_404(room_id)

    if request.method == "GET":

        try:
            db.session.delete(room)
            db.session.commit()
            return redirect("/rooms")
        except Exception as e:
            return {"message":f"Room delete failed {e}"}


@app.route("/temperature/<string:room_id>", methods=['POST'])
def add_temp(room_id):
    if request.method == "POST":
        temp = request.form['temperature_value']
        new_temp = Temperatures(room_id=room_id,temperature=float(temp))

        try:
            db.session.add(new_temp)
            db.session.commit()
            return redirect(f'/temperatures/room/{room_id}')
        except Exception as e:
            return {"message":f"Temperature add failed {e}"}
    else:
        return {"message":"Does not support GET"}



@app.route("/temperatures/all-rooms", methods=['GET'])
def get_all_temperatures():
    if request.method == "GET":
        temps = Temperatures.query.order_by(Temperatures.date).all()
        temp_dict={}
        for temp in temps:
            temp_dict[temp.id] = {
                'id':temp.id,
                'temperature': temp.temperature,
                'date':temp.date
            } 
        return temp_dict

@app.route("/temperatures/room/<int:room_id>", methods=['GET'])
def get_room_temperatures(room_id):
    if request.method == "GET":
        room = Rooms.query.get_or_404(room_id)
        temps = Temperatures.query.with_entities(Temperatures.id,Temperatures.temperature,Temperatures.date)\
                        .join(Rooms, Temperatures.room_id == Rooms.id)\
                        .filter(Temperatures.room_id==room_id).all()

        date_values = [d.date.strftime("%Y-%m-%d %H:%M:%S") for d in temps ]
        temp_values = [d.temperature for d in temps]

        df = pd.DataFrame(list(zip(date_values, temp_values)),columns =['DateTime', 'Temperature'])
        fig = px.line(df, x='DateTime', y='Temperature')
        fig.update_layout({'plot_bgcolor':'rgba(0,0,0,0)','paper_bgcolor':'rgba(0,0,0,0)'})
        
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        return render_template('room_temperatures.html',room_name=room.room_name,temperatures=temps,room_id=room_id,graphJSON=graphJSON)


@app.route("/avgtemp/<int:room_id>", methods=['GET'])
def get_avg_temp_by_room_id(room_id):
    if request.method == "GET":
        temps1 = Temperatures.query\
                        .with_entities(
                            Rooms.room_name,
                            func.avg(Temperatures.temperature).label('avg')
                        )\
                        .join(Rooms, Temperatures.room_id == Rooms.id)\
                        .filter(Temperatures.room_id==room_id).all()
        result = {
            "room_id":room_id,
            "data":{temps1[0][0]:temps1[0][1]}
        }
        return result

########### ERROR HANDLING


@app.errorhandler(404) 
def invalid_route(e): 
    return render_template('404.html')


if __name__ == '__main__':
    
    app.run()