import pandas as pd

df = pd.read_csv("output2.csv")

agents_values = df.agents.unique()
collaborative_values = df.collaborative.unique()

for collaborative in collaborative_values:
    for agents in agents_values:
        filtered = df[(df.agents == agents) & (df.collaborative == collaborative)]
        mean = filtered.time.mean()
        without_extremes = filtered[filtered.time < 300]
        we_mean = without_extremes.time.mean()
        print(f"Collaborative: {collaborative}, Agents {agents}, Avg Time: {mean}, Avg Time (w.o. extremes): {we_mean}")
print(df.mean())
