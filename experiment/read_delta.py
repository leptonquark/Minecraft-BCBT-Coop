import matplotlib.pyplot as plt

from experiment.read import read_csv
from items import items

PICKAXES = ["None", items.WOODEN_PICKAXE, items.STONE_PICKAXE, items.IRON_PICKAXE, items.DIAMOND_PICKAXE]

COOPERATIVITY_COLORS = {
    "False": "r",
    "True": "g",
    "Both": "b"
}

COOPERATIVITY_NAMES = ["Independent", "Collaborative", "Proposed Method"]
BAR_WIDTH = 0.5


def plot_delta():
    world_id = "fwg"
    world_name = "the flat world"
    file_name = "output_fwg_delta.csv"

    world_data = read_csv(file_name)

    agents = 3

    agent_data = world_data[world_data.agents == agents]

    stats = agent_data.groupby(['delta', 'collaborative']).agg({"time": ["mean", "std"]})
    stats.columns = ["time_mean", "time_std"]
    stats = stats.reset_index()

    stats = stats.groupby("delta").apply(add_time_fractions)

    deltas = stats.delta.unique()

    plot_delta_completion_times(agents, deltas, world_id, stats, world_name)

    plot_delta_completion_time_fractions(agents, deltas, world_id, stats, world_name)


def plot_delta_completion_times(agents, deltas, world_id, stats, world_name):
    fig, ax = plt.subplots()
    for cooperativity, color in COOPERATIVITY_COLORS.items():
        data = stats[stats.collaborative == cooperativity]
        time_mean = [float(data[data.delta == delta].time_mean) for delta in deltas]
        time_std = [float(data[data.delta == delta].time_std) for delta in deltas]
        ax.errorbar(deltas, time_mean, yerr=time_std, fmt="o", color=color, markerfacecolor=color,
                    markeredgecolor='k', capsize=2)
        plt.legend(COOPERATIVITY_NAMES, title="Cooperativity", title_fontproperties={"weight": "bold"})
    plt.ylim([0, 200])
    ax.set_xlabel("Pickaxe", size=12)
    ax.set_ylabel("Average completion time (s)")
    plt.title(f"Fence post placement in {world_name} with {agents} agents")
    plt.savefig(f"pickaxe_completion_times_{world_id}_{agents}.png")
    plt.show()


def plot_delta_completion_time_fractions(agents, deltas, world_id, stats, world_name):
    fig, ax = plt.subplots()
    for cooperativity, color in COOPERATIVITY_COLORS.items():
        if cooperativity == "True" or cooperativity == "Both":
            data = stats[stats.collaborative == cooperativity]
            time_mean_diff = [float(data[data.delta == delta].time_mean_diff) for delta in deltas]
            time_std_diff = [float(data[data.delta == delta].time_std_diff) for delta in deltas]
            if cooperativity == "True":
                deltas_collab = deltas - BAR_WIDTH / 2
            else:
                deltas_collab = deltas + BAR_WIDTH / 2
            ax.bar(deltas_collab, time_mean_diff, yerr=time_std_diff, color=color, capsize=2, edgecolor="k", width=0.5)
            plt.legend(["Collaborative", "Proposed Method"], title="Cooperativity",
                       title_fontproperties={"weight": "bold"})
    plt.ylim([0, 1])
    ax.set_xlabel("Distance between fence posts $\Delta$ (blocks)", size=12)
    ax.set_ylabel("Fraction of average completion time of baseline ")
    plt.title(f"Fence post placement in {world_name} with {agents} agents")
    plt.savefig(f"pickaxe_ct_fractions_{world_id}_{agents}.png")
    plt.show()


def add_time_fractions(stats_sub):
    baseline = stats_sub.loc[stats_sub.collaborative == "False"].time_mean.values[0]
    stats_sub["time_mean_diff"] = stats_sub["time_mean"].apply(lambda x: x / baseline)
    stats_sub["time_std_diff"] = stats_sub.apply(lambda x: calculate_std_diff(x, baseline), axis=1)
    return stats_sub


def calculate_std_diff(stats_sub, baseline):
    rel_std = stats_sub["time_std"] / stats_sub["time_mean"]
    return stats_sub["time_mean"] / baseline * rel_std


if __name__ == "__main__":
    plot_delta()
