import matplotlib.pyplot as plt
import pandas as pd

from experiment.start import EXPERIMENT_PATH
from utils.file import get_project_root

CAPSIZE = 10
FULL_WIDTH = 0.5

files = ["output_g10spmdw_5.csv"]
fpp = False
flat_world = False
without_edges = True

dfs = [pd.read_csv(get_project_root() / EXPERIMENT_PATH / file) for file in files]
df = pd.concat(dfs)

print(df)

print(df.time.mean())

stats = df.groupby(['agents', 'collaborative']).agg({"time": ["mean", "std"]})
stats.columns = ["time_mean", "time_std"]

df_we = df[df.time < 300]
stats_we = df_we.groupby(['agents', 'collaborative']).agg({"time": ["mean", "std"]})
stats_we.columns = ["time_mean_we", "time_std_we"]
stats_full = pd.concat([stats, stats_we], axis=1)
stats_full = stats_full.reset_index()

df_edges = df[df.time >= 300]

print(df_edges.groupby(['agents', 'collaborative']).count())

cooperativities = len(stats_full.collaborative.unique())
width = FULL_WIDTH / cooperativities
for without_edges in [False, True]:

    def get_delta_x(collaborative):
        if cooperativities == 3:
            if collaborative == "Both":
                return width
            elif collaborative == "True":
                return 0
            else:
                return -width
        else:
            if collaborative:
                return width / 2
            else:
                return -width / 2


    x = [row.agents + get_delta_x(row.collaborative) for _, row in stats_full.iterrows()]
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
        width=width
    )

    ticks = []
    print(stats_full)

    for t in x[::cooperativities]:
        if cooperativities == 3:
            ticks += [t - 2 * width, t - width, t - width, t]
        elif cooperativities == 2:
            ticks += [t, t + width / 2, t + width]

    labels = []
    if cooperativities == 2:
        for agent in stats_full.agents.unique():
            labels += ['Indep', f"\n{agent} {'agents' if agent > 1 else 'agent'}", 'Collab']
    elif cooperativities == 3:
        for agent in stats_full.agents.unique():
            labels += ['I', f"\n{agent} {'agents' if agent > 1 else 'agent'}", 'C', "B"]
    plt.xticks(ticks)
    ax.set_xticklabels(labels)
    ax.tick_params(axis='x', which='both', length=0)

    plt.ylabel('Average completion time (s)')

    if fpp:
        ymax = 300
    else:
        ymax = 200
    plt.ylim([0, ymax])

    runs = int(len(df) / (cooperativities * len(stats_full.agents.unique())))
    if fpp:
        generator = "flat world generator" if flat_world else "default world generator"
        plt.title(f'{runs} runs each using {generator}')
    else:
        plt.title(f'{runs} runs each in the stone pickaxe scenario')

    we = "we_" if without_edges else ""
    if fpp:
        gen = "fwg" if flat_world else "dwg"
        filename = f"{gen}_{we}{runs}"
    else:
        filename = f"sp_{we}{runs}"
    plt.savefig(filename)
    plt.show()
