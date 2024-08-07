import math

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch

from experiment.test import EXPERIMENT_PATH
from utils.file import get_project_root
from utils.plot import save_figure

CAPSIZE = 10
FULL_WIDTH = 0.8
TIMEOUT = 300

COOPERATIVITY_COLORS = {
    "False": "r",
    "True": "g",
    "Both": "b"
}
COOPERATIVITY_NAMES = ["Independent", "Collaborative", "Collaborative w. backup"]
COOPERATIVITY_TITLE = "Mode of Cooperation"


def read_csv(file_name):
    return pd.read_csv(get_project_root() / EXPERIMENT_PATH / file_name)


def plot_completion_times(fpp, flat_world, hide_backup=False):
    files = get_files(flat_world, fpp)
    dfs = [read_csv(file).astype({"collaborative": str}) for file in files]
    df = pd.concat(dfs)
    if hide_backup:
        df = df[df.collaborative != "Both"]

    groups = ["agents", "collaborative"]

    stats = get_time_stats(df, groups, ["time_mean", "time_std"])

    df_we = df[(df.time < TIMEOUT) & (df.time >= 0)]
    stats_we = get_time_stats(df_we, groups, ["time_mean_we", "time_std_we"])
    stats_full = pd.concat([stats, stats_we], axis=1).reset_index()

    df_edges = df[df.time >= TIMEOUT]

    print(df_edges.groupby(['agents', 'collaborative']).count())

    cooperativities = len(stats_full.collaborative.unique())
    width = FULL_WIDTH / cooperativities
    for without_edges in [False, True]:
        x = [row.agents + get_delta_x(row.collaborative, cooperativities, width) for _, row in stats_full.iterrows()]
        colors = [COOPERATIVITY_COLORS[row.collaborative] for _, row in stats_full.iterrows()]
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
        ax.set_xticks(get_ticks(cooperativities, width, x))
        labels = get_labels(cooperativities, stats_full)
        ax.set_xticklabels(labels)
        ax.tick_params(axis='x', which='both', length=0)

        group_n = cooperativities + 1
        fig.canvas.draw()

        tick_labels = ax.xaxis.get_ticklabels()
        cooperativity_labels = [tick_labels[i] for i in range(len(tick_labels)) if i % group_n != 0]
        print(cooperativity_labels)
        for cooperativity_label in cooperativity_labels:
            cooperativity_label.set_rotation(90)

        max_width = max(cooperativity_label.get_window_extent().height for cooperativity_label in cooperativity_labels)
        text_height = tick_labels[0].get_window_extent().height
        tall_whitespace = "".join(["\n"] * math.ceil(max_width / text_height))
        new_labels = [tall_whitespace + labels[i] if i % group_n == 0 else labels[i] for i in range(len(labels))]
        ax.set_xticklabels(new_labels)

        plt.ylabel('Average completion time (s)')

        plt.ylim([0, get_y_max(fpp, flat_world)])

        n_agents_unique = len(stats_full.agents.unique())
        runs = int(len(df) / (cooperativities * n_agents_unique))
        plt.title(get_title(flat_world, fpp))

        cooperativities_unique = df.collaborative.unique()
        legend_items = [Patch(facecolor=COOPERATIVITY_COLORS[coop], edgecolor='k') for coop in cooperativities_unique]
        plt.legend(legend_items, COOPERATIVITY_NAMES, title=COOPERATIVITY_TITLE,
                   title_fontproperties={"weight": "bold"})

        plt.tight_layout()
        save_figure(get_file_name(flat_world, fpp, runs, without_edges, hide_backup))
        plt.show()


def get_title(flat_world, fpp):
    if fpp:
        generator = "flat world" if flat_world else "default world"
        return f"The fence post placement scenario in the {generator}"
    else:
        arena = "test arena" if flat_world else "default world"
        return f"The stone pickaxe scenario in the {arena}"


def get_file_name(flat_world, fpp, runs, without_edges, hide_backup):
    we = "we_" if without_edges else ""
    hb = "hb_" if hide_backup else ""
    if fpp:
        gen = "fwg" if flat_world else "dwg"
        return f"{gen}_{we}{hb}{runs}"
    else:
        gen = "_spmdw" if flat_world else ""
        return f"sp_{we}{hb}{runs}{gen}"


def get_y_max(fpp, flat_world):
    if fpp:
        if flat_world:
            return 250
        else:
            return 150
    else:
        if flat_world:
            return 100
        else:
            return 200


def get_files(flat_world, fpp):
    if fpp:
        if flat_world:
            return ["output_fwg_2.csv", "output_fwg_3.csv"]
        else:
            return ["output_dwg_7.csv", "output_dwg_8.csv"]
    else:
        if flat_world:
            return ["output_g10spmdw_3.csv"]
        else:
            return ["output_g10sp1.csv"]


def get_delta_x(collaborative, cooperativities, width):
    if cooperativities == 3:
        if collaborative == "Both":
            return width
        elif collaborative == "True":
            return 0
        else:
            return -width
    else:
        if collaborative == "True":
            return width / 2
        else:
            return -width / 2


def get_labels(cooperativities, stats_full):
    labels = []
    cooperativity_labels = ["Independent", "Collaborative", "Backup"]
    for agent in stats_full.agents.unique():
        agents_label = f"{agent} {'agents' if agent > 1 else 'agent'}"
        labels += [f"{agents_label}"] + cooperativity_labels[:cooperativities]
    return labels


def get_ticks(cooperativities, width, x):
    ticks = []
    for t in x[::cooperativities]:
        if cooperativities == 3:
            ticks += [t - width + 0.0001, t - 2 * width, t - width, t]
        elif cooperativities == 2:
            ticks += [t + width / 2, t, t + width]
    return ticks


def get_time_stats(data, groups, columns=None):
    if columns is None:
        columns = ["time_mean", "time_std"]
    stats = data.groupby(groups).agg({"time": ["mean", "std"]})
    stats.columns = columns
    return stats


def plot_variable_values(ax, stats, values, key):
    for cooperativity, color in COOPERATIVITY_COLORS.items():
        data = stats[stats.collaborative == cooperativity].set_index(key)
        ax.errorbar(
            values,
            data["time_mean"],
            yerr=data["time_std"],
            fmt="o",
            color=color,
            markerfacecolor=color,
            markeredgecolor='k',
            capsize=2
        )
        plt.legend(COOPERATIVITY_NAMES, title=COOPERATIVITY_TITLE, title_fontproperties={"weight": "bold"})


if __name__ == '__main__':
    plot_completion_times(fpp=True, flat_world=True, hide_backup=True)
    plot_completion_times(fpp=True, flat_world=False, hide_backup=True)
    plot_completion_times(fpp=False, flat_world=True, hide_backup=True)
    plot_completion_times(fpp=False, flat_world=False, hide_backup=True)

