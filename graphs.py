# Agar ek hi graph show ho raha hai to save karke dekhna best hai

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("over_level_data.csv")

final_score = df.groupby("match_id")["team_runs"].max().reset_index()
final_score.rename(columns={"team_runs":"final_score"}, inplace=True)

df = df.merge(final_score,on="match_id")

# ===============================
# GRAPH 1
# ===============================
plt.figure(figsize=(12,6))
team_avg = df.groupby("batting_team")["final_score"].mean().sort_values()
team_avg.plot(kind="bar", color="skyblue")
plt.title("Team Wise Average Score")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("graph1.png")
plt.close()

# ===============================
# GRAPH 2
# ===============================
plt.figure(figsize=(10,6))
sns.scatterplot(data=df,x="team_wicket",y="final_score",color="red")
plt.title("Impact of Wickets on Final Score")
plt.tight_layout()
plt.savefig("graph2.png")
plt.close()

# ===============================
# GRAPH 3
# ===============================
plt.figure(figsize=(10,6))
sns.lineplot(data=df,x="over",y="team_runs",color="green")
plt.title("Runs Growth by Overs")
plt.tight_layout()
plt.savefig("graph3.png")
plt.close()

# ===============================
# GRAPH 4
# ===============================
plt.figure(figsize=(12,6))
venue_avg = df.groupby("venue")["final_score"].mean().sort_values().tail(10)
venue_avg.plot(kind="barh", color="orange")
plt.title("Venue Wise Average Score")
plt.tight_layout()
plt.savefig("graph4.png")
plt.close()

# ===============================
# GRAPH 5
# ===============================
plt.figure(figsize=(8,5))
sns.heatmap(df[['over','team_runs','team_wicket','final_score']].corr(),annot=True,cmap="coolwarm")
plt.title("Correlation Heatmap")
plt.tight_layout()
plt.savefig("graph5.png")
plt.close()

print("✅ All graphs saved in project folder")