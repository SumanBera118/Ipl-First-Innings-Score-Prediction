# ==============================
# BALL-BY-BALL → OVER-LEVEL
# ==============================

import pandas as pd

# STEP 1: Load dataset
df = pd.read_csv("C:\\Users\\suman\\Desktop\\IPL Project\\IPL.csv", low_memory=False)

# STEP 2: First innings filter
df = df[df['innings'] == 1]

# STEP 3: Select required columns
df = df[['match_id','batting_team','bowling_team','over','team_runs','team_wicket','venue']]

# STEP 4: Convert to OVER-LEVEL DATA 🔥
df_over = df.groupby(
    ['match_id','over','batting_team','bowling_team','venue']
).agg({
    'team_runs': 'max',      # last runs in that over
    'team_wicket': 'max'     # total wickets till that over
}).reset_index()

# STEP 5: Check output
print(df_over.head())
print("Shape:", df_over.shape)

# STEP 6: Save new dataset (optional)
df_over.to_csv("over_level_data.csv", index=False)

print("✅ Over-level dataset created successfully!")

# ==============================
# ADD FINAL SCORE COLUMN
# ==============================

final_score = df_over.groupby('match_id')['team_runs'].max().reset_index()
final_score.rename(columns={'team_runs': 'final_score'}, inplace=True)

df_over = df_over.merge(final_score, on='match_id')

print(df_over.head())

# ==============================
# FEATURES & TARGET
# ==============================

X = df_over[['batting_team','bowling_team','over','team_runs','team_wicket','venue']]
y = df_over['final_score']


# ==============================
# ENCODING
# ==============================

X = pd.get_dummies(X)


# ==============================
# TRAIN TEST SPLIT
# ==============================

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)


# ==============================
# TRAIN MODEL
# ==============================

from sklearn.ensemble import RandomForestRegressor

model = RandomForestRegressor()
model = RandomForestRegressor(
    n_estimators=100,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)


# ==============================
# CHECK ERROR
# ==============================

from sklearn.metrics import mean_absolute_error

pred = model.predict(X_test)
print("MAE Error:", mean_absolute_error(y_test, pred))

import pickle

pickle.dump(model, open('model.pkl','wb'))
pickle.dump(X.columns, open('columns.pkl','wb'))

print("✅ Model saved successfully!")