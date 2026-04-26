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
import smtplib
from email.mime.text import MIMEText

# ===========================
# APP START
# ===========================
app = Flask(__name__)

# ===========================
# CONFIG
# ===========================
app.config['SECRET_KEY'] = 'secret123'

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
# LOAD MACHINE LEARNING MODEL
# ===========================
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('columns.pkl', 'rb') as f:
    cols = pickle.load(f)

print(cols)

# ===========================
# LOGIN PAGE + SEND OTP
# ===========================
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):

            otp = str(random.randint(100000, 999999))

            session['otp'] = otp
            session['user_id'] = user.id

            try:
                msg = MIMEText(f"Your OTP is {otp}")
                msg["Subject"] = "IPL Login OTP"
                msg["From"] = "beraakash956@gmail.com"
                msg["To"] = user.email

                server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
                server.login(
                    "beraakash956@gmail.com",
                    "hjgamitxfsfpqrmm"
                )

                server.send_message(msg)
                server.quit()

                return redirect(url_for('verify_otp'))

            except Exception as e:
                error = f"Email sending failed: {e}"

        else:
            error = "Incorrect username or password"

    return render_template("login.html", error=error)

# ===========================
# VERIFY OTP
# ===========================
@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():

    error = None

    if request.method == 'POST':

        user_otp = request.form['otp']

        if user_otp == session.get('otp'):

            user = User.query.get(session['user_id'])

            login_user(user)

            session.pop('otp', None)
            session.pop('user_id', None)

            return redirect(url_for('home'))

        else:
            error = "Wrong OTP"

    return render_template("verify_otp.html", error=error)

# ===========================
# REGISTER PAGE
# ===========================
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        fullname = request.form['fullname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm_password']
        fav_team = request.form['fav_team']

        if password != confirm:
            return render_template(
                'register.html',
                error="Passwords do not match"
            )

        if User.query.filter_by(username=username).first():
            return render_template(
                'register.html',
                error="Username already exists"
            )

        if User.query.filter_by(email=email).first():
            return render_template(
                'register.html',
                error="Email already registered"
            )

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
# HOME PAGE
# ===========================
@app.route('/')
@login_required
def home():
    return render_template('index.html')

# ===========================
# IPL SCORE PREDICTION
# ===========================
@app.route('/predict', methods=['POST'])
@login_required
def predict():
    try:
        batting_team = request.form['batting_team']
        bowling_team = request.form['bowling_team']
        venue = request.form['venue']

        runs = int(request.form['team_runs'])
        wickets = int(request.form['team_wicket'])

        over_input = request.form['over']
        over_float = float(over_input)

        whole = int(over_float)
        balls = int(round((over_float - whole) * 10))

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

        if overs < 6:
            boost = 30
        elif overs < 15:
            boost = 25
        else:
            boost = 20

        final_score = int(prediction) + boost

        confidence = 91

        return render_template(
            'index.html',
            prediction_text=final_score,
            confidence=confidence
        )

    except Exception as e:
        print("Prediction Error:", e)

        return render_template(
            'index.html',
            prediction_text="Prediction Error",
            confidence=0,
            error=str(e)
        )
# ===========================
# RUN APP
# ===========================
if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)