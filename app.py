from flask import Flask, render_template, request
import pickle
import pandas as pd

app = Flask(__name__)

model = pickle.load(open('model.pkl','rb'))
cols = pickle.load(open('columns.pkl','rb'))

# ✅ HOME ROUTE
@app.route('/')
def home():
    return render_template('index.html')

# ✅ PREDICT ROUTE
@app.route('/predict', methods=['GET','POST'])
def predict():
    if request.method == 'POST':

        batting_team = request.form['batting_team']
        bowling_team = request.form['bowling_team']
        venue = request.form['venue']

        runs = int(request.form['team_runs'])
        wickets = int(request.form['team_wicket'])
        overs = float(request.form['over'])

        # ✅ Create temp dataframe
        temp_df = pd.DataFrame({
            'batting_team': [batting_team],
            'bowling_team': [bowling_team],
            'over': [overs],
            'team_runs': [runs],
            'team_wicket': [wickets],
            'venue': [venue]
        })

        # ✅ Encoding
        temp_df = pd.get_dummies(temp_df)

        # ✅ Align with training columns
        input_data = temp_df.reindex(columns=cols, fill_value=0)

        # ✅ Prediction
        prediction = model.predict(input_data)
        result = int(prediction[0]+20)

        return render_template('index.html', prediction_text=result)

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)