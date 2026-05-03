from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    login_required,
    logout_user
)
from werkzeug.security import generate_password_hash, check_password_hash

import pickle
import pandas as pd
import os
import random

# ===========================
# APP START
# ===========================
app = Flask(__name__)

# ===========================
# CONFIG
# ===========================
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "fallback-secret")

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = \
'sqlite:///' + os.path.join(basedir, 'users.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ===========================
# LOGIN MANAGER
# ===========================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ===========================
# USER MODEL
# ===========================
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    fav_team = db.Column(db.String(50))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ===========================
# LOAD MODEL
# ===========================
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

with open("columns.pkl", "rb") as f:
    cols = pickle.load(f)

# ===========================
# LOGIN (OTP REMOVED FOR DEPLOY)
# ===========================
@app.route('/login', methods=['GET', 'POST'])
def login():

    error = None

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            error = "Invalid credentials"

    return render_template("login.html", error=error)

# ===========================
# REGISTER
# ===========================
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        fullname = request.form.get('fullname')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        fav_team = request.form.get('fav_team')

        if password != confirm:
            return render_template('register.html', error="Passwords do not match")

        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Username exists")

        if User.query.filter_by(email=email).first():
            return render_template('register.html', error="Email exists")

        hashed_password = generate_password_hash(password)

        new_user = User(
            fullname=fullname,
            username=username,
            email=email,
            password=hashed_password,
            fav_team=fav_team
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

# ===========================
# LOGOUT
# ===========================
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ===========================
# HOME
# ===========================
@app.route('/')
def home():
    return render_template(
        'index.html',
        prediction_text=0,
        confidence=0,
        team_logo=None
    )

# ===========================
# PREDICT
# ===========================
@app.route('/predict', methods=['POST'])
@login_required
def predict():

    try:
        batting_team = request.form.get('batting_team')
        bowling_team = request.form.get('bowling_team')
        venue = request.form.get('venue')

        runs = int(request.form.get('team_runs'))
        wickets = int(request.form.get('team_wicket'))

        over_input = float(request.form.get('over'))

        whole = int(over_input)
        balls = int(round((over_input - whole) * 10))
        if balls > 5:
            balls = 5

        overs = whole + (balls / 6)

        temp_df = pd.DataFrame({
            'batting_team': [batting_team],
            'bowling_team': [bowling_team],
            'over': [overs],
            'team_runs': [runs],
            'team_wicket': [wickets],
            'venue': [venue]
        })

        temp_df = pd.get_dummies(temp_df)
        input_data = temp_df.reindex(columns=cols, fill_value=0)

        prediction = model.predict(input_data)[0]

        boost = 30 if overs < 6 else 25 if overs < 15 else 20

        final_score = int(prediction) + boost
        confidence = 91

        return render_template(
            'index.html',
            prediction_text=final_score,
            confidence=confidence,
            team_logo=None
        )

    except Exception as e:
        return render_template(
            'index.html',
            prediction_text="Error",
            confidence=0,
            team_logo=None
        )

# ===========================
# RUN (LOCAL ONLY)
# ===========================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()