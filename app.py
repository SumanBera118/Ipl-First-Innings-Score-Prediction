from flask import Flask, render_template, request
import pickle
import pandas as pd

app = Flask(__name__)

model = pickle.load(open('model.pkl','rb'))
cols = pickle.load(open('columns.pkl','rb'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    
    input_data = pd.DataFrame(columns=cols)
    input_data.loc[0] = 0

    # Get form data
    batting_team = request.form['batting_team']
    bowling_team = request.form['bowling_team']
    venue = request.form['venue']
    runs = int(request.form['runs'])
    wickets = int(request.form['wickets'])
    overs = float(request.form['overs'])

    # Fill numeric
    input_data['over'] = overs
    input_data['team_runs'] = runs
    input_data['team_wicket'] = wickets

    # Fill categorical
    input_data['batting_team_' + batting_team] = 1
    input_data['bowling_team_' + bowling_team] = 1
    input_data['venue_' + venue] = 1

    # Predict
    prediction = model.predict(input_data)
    result = int(prediction[0])

    return render_template('index.html', prediction_text=result)

if __name__ == "__main__":
    app.run(debug=True)