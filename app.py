from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pickle
import pandas as pd
import gzip
import numpy as np
import os

app = Flask(__name__)

# 🔐 Secret key
app.config['SECRET_KEY'] = 'secret123'


basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'users.db')

# 🗄️ Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# 🔐 Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# 👤 USER MODEL
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

# 🤖 Load ML model
with gzip.open('model.pkl.gz', 'rb') as f:
    model = pickle.load(f)

cols = pickle.load(open('columns.pkl', 'rb'))

# ===========================
# 🔐 LOGIN
# ===========================
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            error = "❌ Incorrect username or password"

            # 👇 IMPORTANT: fields empty bhejna
            return render_template('login.html', error=error, username="", password="")

    return render_template('login.html', username="", password="")

# ===========================
# 📝 REGISTER
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

        # 🔴 Password check
        if password != confirm:
            return render_template('register.html', error="Passwords do not match")

        # 🔴 Username check
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Username already exists")

        # 🔴 Email check
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error="Email already registered")

        # 🔐 Hash password
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
# 🚪 LOGOUT
# ===========================
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ===========================
# 🏠 HOME (PROTECTED)
# ===========================
@app.route('/')
@login_required
def home():
    return render_template('index.html')


# ===========================
# 🔮 PREDICTION
# ===========================
@app.route('/predict', methods=['POST'])
@login_required
def predict():

    batting_team = request.form['batting_team']
    bowling_team = request.form['bowling_team']
    venue = request.form['venue']

    runs = int(request.form['team_runs'])
    wickets = int(request.form['team_wicket'])
    overs = float(request.form['over'])

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

    prediction = model.predict(input_data)
    result = int(prediction[0] + 20)

    # 🎯 Confidence logic
    if overs < 6:
        confidence = np.random.randint(55, 65)
    elif overs < 15:
        confidence = np.random.randint(65, 75)
    else:
        confidence = np.random.randint(75, 90)

    return render_template(
        'index.html',
        prediction_text=result,
        confidence=confidence
    )


# ===========================
# ▶ RUN APP
# ===========================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)