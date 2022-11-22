import pandas as pd

df = pd.read_csv("output2.csv")

stats = df.groupby(['collaborative', 'agents']).agg({"time": ["mean", "std"]})
stats.columns = ["time_mean", "time_std"]
df_we = df[df.time < 300]
stats_we = df_we.groupby(['collaborative', 'agents']).agg({"time": ["mean", "std"]})
stats_we.columns = ["time_mean_we", "time_std_we"]
stats_full = pd.concat([stats, stats_we], axis=1)
stats_full = stats_full.reset_index()
print(stats_full)
