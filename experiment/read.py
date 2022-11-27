import matplotlib.pyplot as plt
import pandas as pd

CAPSIZE = 10
WIDTH = 0.25

files = ["output10.csv", "output11.csv"]
flat_world = False
without_edges = False

dfs = [pd.read_csv(file) for file in files]
df = pd.concat(dfs)

print(df.time.mean())

stats = df.groupby(['agents', 'collaborative']).agg({"time": ["mean", "std"]})
stats.columns = ["time_mean", "time_std"]

df_we = df[df.time < 300]
stats_we = df_we.groupby(['agents', 'collaborative']).agg({"time": ["mean", "std"]})
print(len(df_we.groupby(['agents', 'collaborative'])))
stats_we.columns = ["time_mean_we", "time_std_we"]
stats_full = pd.concat([stats, stats_we], axis=1)
stats_full = stats_full.reset_index()

df_edges = df[df.time >= 300]

print(df_edges.groupby(['agents', 'collaborative']).count())

for without_edges in [False, True]:

    x = [row.agents + (WIDTH / 2 if row.collaborative else -WIDTH / 2) for _, row in stats_full.iterrows()]
    palette = ['r', 'g', 'b']
    colors = [palette[row.agents - 1] for _, row in stats_full.iterrows()]
    fig, ax = plt.subplots()

    if without_edges:
        y = stats_full.time_mean_we
        yerr = stats_full.time_std_we
    else:
        y = stats_full.time_mean
        yerr = stats_full.time_std

    ax.bar(
        x=x,
        height=y,
        yerr=yerr,
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
    ax.tick_params(axis='x', which='both', length=0)

    plt.ylabel('Average completion time (s)')
    plt.ylim([0, 300])

    runs = int(len(df) / (2 * len(stats_full.agents.unique())))
    generator = "flat world generator" if flat_world else "default world generator"
    we_title = " (without edge cases)" if without_edges else ""
    plt.title(f'{runs} runs each using {generator}{we_title}')

    gen = "fwg" if flat_world else "dwg"
    we = "we_" if without_edges else ""
    filename = f"{gen}_{we}{runs}"
    plt.savefig(filename)
    plt.show()
