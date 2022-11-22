import matplotlib.pyplot as plt
import pandas as pd

CAPSIZE = 10
WIDTH = 0.25

df = pd.read_csv("output3.csv")

stats = df.groupby(['agents', 'collaborative']).agg({"time": ["mean", "std"]})
stats.columns = ["time_mean", "time_std"]
df_we = df[df.time < 300]
stats_we = df_we.groupby(['agents', 'collaborative']).agg({"time": ["mean", "std"]})
stats_we.columns = ["time_mean_we", "time_std_we"]
stats_full = pd.concat([stats, stats_we], axis=1)
stats_full = stats_full.reset_index()

x = [row.agents + (WIDTH / 2 if row.collaborative else -WIDTH / 2) for _, row in stats_full.iterrows()]
palette = ['r', 'g', 'b']
colors = [palette[row.agents - 1] for _, row in stats_full.iterrows()]
fig, ax = plt.subplots()
ax.bar(
    x=x,
    height=stats_full.time_mean_we,
    yerr=stats_full.time_std_we,
    color=colors,
    edgecolor='black',
    capsize=CAPSIZE,
    width=WIDTH
)
ticks = []
for t in x[::2]:
    ticks += [t, t + WIDTH / 2, t + WIDTH]
labels = []
for agent in stats_full.agents.unique():
    labels += ['Indep', f"\n{agent} {'agents' if agent > 1 else 'agent'}", 'Collab']
plt.xticks(ticks)
ax.set_xticklabels(labels)
plt.ylabel('Completion time (s)')
plt.title('Average completion time for fence building experiment')
ax.tick_params(axis='x', which='both', length=0)

plt.show()
