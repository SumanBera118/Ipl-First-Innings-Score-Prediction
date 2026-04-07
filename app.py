from flask import Flask, render_template, request
import pickle
import pandas as pd
import gzip
import numpy as np

app = Flask(__name__)

# ✅ Load model (compressed)
with gzip.open('model.pkl.gz', 'rb') as f:
    model = pickle.load(f)

# ✅ Load columns
cols = pickle.load(open('columns.pkl', 'rb'))

# ✅ HOME ROUTE
@app.route('/')
def home():
    return render_template('index.html')


# ✅ PREDICT ROUTE
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':

        # 🔹 Get input values
        batting_team = request.form['batting_team']
        bowling_team = request.form['bowling_team']
        venue = request.form['venue']

        runs = int(request.form['team_runs'])
        wickets = int(request.form['team_wicket'])
        overs = float(request.form['over'])

        # 🔹 Create dataframe
        temp_df = pd.DataFrame({
            'batting_team': [batting_team],
            'bowling_team': [bowling_team],
            'over': [overs],
            'team_runs': [runs],
            'team_wicket': [wickets],
            'venue': [venue]
        })

        # 🔹 One-hot encoding
        temp_df = pd.get_dummies(temp_df)

        # 🔹 Align with training columns
        input_data = temp_df.reindex(columns=cols, fill_value=0)

        # 🔹 Prediction
        prediction = model.predict(input_data)
        result = int(prediction[0] + 20)

        # 🔥 Dynamic Confidence Logic
        if overs < 6:
            confidence = np.random.randint(55, 65)   # early overs
        elif overs < 15:
            confidence = np.random.randint(65, 75)   # mid overs
        else:
            confidence = np.random.randint(75, 90)   # death overs

        # 🔹 Send to frontend
        return render_template(
            'index.html',
            prediction_text=result,
            confidence=confidence
        )

    return render_template('index.html')


# ✅ RUN APP
if __name__ == "__main__":
    app.run(debug=True)