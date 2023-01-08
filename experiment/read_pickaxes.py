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


def plot_pickaxe_completion_times():
    agent_amounts = [2, 3]
    worlds = [
        ("ta", "the test arena", "output_g10spmdw_wide.csv"),
        ("dwg", "the authentic world", "output_g10sp_wide.csv")
    ]

    for id, world_name, file_name in worlds:
        world_data = read_csv(file_name)

        for agents in agent_amounts:

            agent_data = world_data[world_data.agents == agents]

            stats = agent_data.groupby(['pickaxe', 'collaborative']).agg({"time": ["mean", "std"]})
            stats.columns = ["time_mean", "time_std"]
            stats = stats.reset_index()

            stats = stats.groupby("pickaxe").apply(add_time_mean_diff)

            fig, ax = plt.subplots()
            for cooperativity, color in COOPERATIVITY_COLORS.items():
                data = stats[stats.collaborative == cooperativity]
                time_mean = [float(data[data.pickaxe == pickaxe].time_mean) for pickaxe in PICKAXES]
                time_std = [float(data[data.pickaxe == pickaxe].time_std) for pickaxe in PICKAXES]
                ax.errorbar(PICKAXES, time_mean, yerr=time_std, fmt="o", color=color, markerfacecolor=color,
                            markeredgecolor='k', capsize=2)
                plt.legend(COOPERATIVITY_NAMES, title="Cooperativity", title_fontproperties={"weight": "bold"})
            plt.ylim([0, 100])
            ax.set_xticks(PICKAXES)
            ax.set_xticklabels(["None", "Wooden Pickaxe", "Stone Pickaxe", "Iron Pickaxe", "Diamond Pickaxe"])
            ax.set_xlabel("Pickaxe", size=12)

            ax.set_ylabel("Average completion time (s)")

            plt.title(f"Gathering scenario in {world_name} with {agents} agents")

            plt.savefig(f"pickaxe_completion_times_{id}_{agents}.png")
            plt.show()


def add_time_mean_diff(stats_sub):
    baseline = stats_sub.loc[stats_sub.collaborative == "False"].time_mean.values[0]
    stats_sub["time_mean_diff"] = stats_sub["time_mean"].apply(lambda x: x / baseline)
    return stats_sub


if __name__ == "__main__":
    plot_pickaxe_completion_times()
