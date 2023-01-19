import matplotlib.pyplot as plt
import pandas as pd

from experiment.test import EXPERIMENT_PATH
from utils.file import get_project_root

CAPSIZE = 10
FULL_WIDTH = 0.8

COOPERATIVITY_COLORS = {
    "False": "r",
    "True": "g",
    "Both": "b"
}

COOPERATIVITY_NAMES = ["Independent", "Collaborative", "Proposed Method"]


def read_csv(file_name):
    return pd.read_csv(get_project_root() / EXPERIMENT_PATH / file_name)


def plot_completion_times(fpp, flat_world):
    files = get_files(flat_world, fpp)
    dfs = [pd.read_csv(get_project_root() / EXPERIMENT_PATH / file).astype({"collaborative": str}) for file in files]
    df = pd.concat(dfs)

    stats = df.groupby(['agents', 'collaborative']).agg({"time": ["mean", "std"]})
    stats.columns = ["time_mean", "time_std"]

    df_we = df[(df.time < 300) & (df.time >= 0)]
    stats_we = df_we.groupby(['agents', 'collaborative']).agg({"time": ["mean", "std"]})
    stats_we.columns = ["time_mean_we", "time_std_we"]
    stats_full = pd.concat([stats, stats_we], axis=1).reset_index()

    df_edges = df[df.time >= 300]

    print(df_edges.groupby(['agents', 'collaborative']).count())

    cooperativities = len(stats_full.collaborative.unique())
    width = FULL_WIDTH / cooperativities
    for without_edges in [False, True]:
        x = [row.agents + get_delta_x(row.collaborative, cooperativities, width) for _, row in stats_full.iterrows()]
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
        plt.xticks(get_ticks(cooperativities, width, x))
        ax.set_xticklabels(get_labels(cooperativities, stats_full))
        ax.tick_params(axis='x', which='both', length=0)

        plt.ylabel('Average completion time (s)')

        ymax = 150
        plt.ylim([0, ymax])

        runs = int(len(df) / (cooperativities * len(stats_full.agents.unique())))
        title = get_title(flat_world, fpp, runs)
        plt.title(title)
        filename = get_file_name(flat_world, fpp, runs, without_edges)
        plt.savefig(filename)
        plt.show()


def get_title(flat_world, fpp, runs):
    if fpp:
        generator = "flat world generator" if flat_world else "default world generator"
        return f"{runs} runs each using {generator}"
    else:
        return f"{runs} runs each in the stone pickaxe scenario"


def get_file_name(flat_world, fpp, runs, without_edges):
    we = "we_" if without_edges else ""
    if fpp:
        gen = "fwg" if flat_world else "dwg"
        return f"{gen}_{we}{runs}"
    else:
        return f"sp_{we}{runs}"


def get_files(flat_world, fpp):
    if fpp and flat_world:
        return ["output_fwg_2.csv", "output_fwg_3.csv"]
    elif fpp and not flat_world:
        return ["output_dwg_7.csv", "output_dwg_8.csv"]
    else:
        return ["output_fwz.csv"]


def get_delta_x(collaborative, cooperativities, width):
    if cooperativities == 3:
        if collaborative == "Both":
            return width
        elif collaborative == "True":
            return 0
        else:
            return -width
    else:
        if collaborative == "True" or collaborative:
            return width / 2
        else:
            return -width / 2


def get_labels(cooperativities, stats_full):
    labels = []
    if cooperativities == 2:
        for agent in stats_full.agents.unique():
            labels += ['Indep', f"\n{agent} {'agents' if agent > 1 else 'agent'}", 'Collab']
    elif cooperativities == 3:
        for agent in stats_full.agents.unique():
            labels += ['Indep', f"\n{agent} {'agents' if agent > 1 else 'agent'}", 'Collab', "Both"]
    return labels


def get_ticks(cooperativities, width, x):
    ticks = []
    for t in x[::cooperativities]:
        if cooperativities == 3:
            ticks += [t - 2 * width, t - width + 0.0001, t - width, t]
        elif cooperativities == 2:
            ticks += [t, t + width / 2, t + width]
    return ticks


def plot_variable_values(ax, stats, values, key):
    for cooperativity, color in COOPERATIVITY_COLORS.items():
        data = stats[stats.collaborative == cooperativity]
        time_mean = [float(data[data[key] == value].time_mean) for value in values]
        time_std = [float(data[data[key] == value].time_std) for value in values]
        ax.errorbar(values, time_mean, yerr=time_std, fmt="o", color=color, markerfacecolor=color,
                    markeredgecolor='k', capsize=2)
        plt.legend(COOPERATIVITY_NAMES, title="Cooperativity", title_fontproperties={"weight": "bold"})


if __name__ == '__main__':
    plot_completion_times(False, True)
