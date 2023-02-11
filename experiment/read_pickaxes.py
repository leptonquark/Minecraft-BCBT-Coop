import matplotlib.pyplot as plt

from experiment.read import read_csv, plot_variable_values, get_time_stats
from items import items
from utils.plot import save_figure

PICKAXES = ["None", items.WOODEN_PICKAXE, items.STONE_PICKAXE, items.IRON_PICKAXE, items.DIAMOND_PICKAXE]


def plot_pickaxe_completion_times():
    agent_amounts = [2, 3]
    worlds = [
        ("ta", "the test arena", "output_g10spmdw_wide.csv"),
        ("dwg", "the authentic world", "output_g10sp_wide.csv")
    ]

    for world_id, world_name, file_name in worlds:
        world_data = read_csv(file_name)

        for agents in agent_amounts:
            agent_data = world_data[world_data.agents == agents]
            stats = get_time_stats(agent_data, ['pickaxe', 'collaborative']).reset_index()

            fig, ax = plt.subplots()
            plot_variable_values(ax, stats, PICKAXES, "pickaxe")

            ax.set_xticks(PICKAXES)
            ax.set_xticklabels(["None", "Wooden Pickaxe", "Stone Pickaxe", "Iron Pickaxe", "Diamond Pickaxe"])
            ax.set_xlabel("Pickaxe", size=12)

            plt.ylim([0, 100])
            ax.set_ylabel("Average completion time (s)")

            plt.title(f"Gathering scenario in {world_name} with {agents} agents")

            save_figure(f"pickaxe_completion_times_{world_id}_{agents}.png")
            plt.show()


if __name__ == "__main__":
    plot_pickaxe_completion_times()
