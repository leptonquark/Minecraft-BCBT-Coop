import matplotlib.pyplot as plt

from experiment.read import read_csv, plot_variable_values, COOPERATIVITY_COLORS, get_time_stats
from utils.plot import save_figure

X_LABEL_SIZE = 12

FIGURE_NAME_DELTA_COMPLETION_TIME_FRACTIONS = "delta_ct_fractions"

FIGURE_NAME_DELTA_COMPLETION_TIMES = "delta_completion_times"

DELTA_X_LABEL = "Distance between fence posts $\Delta$ (blocks)"

COMPLETION_TIME_Y_LABEL = "Average completion time (s)"
COMPLETION_TIME_FRACTION_Y_LABEL = "Fraction of average completion time of baseline"

COMPLETION_TIME_Y_RANGE = [0, 100]
COMPLETION_TIME_FRACTION_Y_RANGE = [0, 1]

BAR_WIDTH = 0.5


def plot_delta(agents):
    world_id = "fwg"
    world_name = "the flat world"
    file_name = "output_fwg_delta.csv"

    world_data = read_csv(file_name)

    agent_data = world_data[world_data.agents == agents]

    stats = get_time_stats(agent_data, ['delta', 'collaborative'])
    stats = stats.groupby("delta").apply(add_time_fractions)
    deltas = stats.delta.unique()

    plot_delta_completion_times(agents, deltas, world_id, stats, world_name)
    plot_delta_completion_time_fractions(agents, deltas, world_id, stats, world_name)


def plot_delta_completion_times(agents, deltas, world_id, stats, world_name):
    fig, ax = plt.subplots()
    plot_variable_values(ax, stats, deltas, "delta")
    ax.set_ylim(COMPLETION_TIME_Y_RANGE)
    set_labels(agents, ax, world_name, COMPLETION_TIME_Y_LABEL)
    save_delta_figure(FIGURE_NAME_DELTA_COMPLETION_TIMES, world_id, agents)


def set_labels(agents, ax, world_name, y_label):
    ax.set_xlabel(DELTA_X_LABEL, size=X_LABEL_SIZE)
    ax.set_ylabel(y_label)
    set_title(ax, agents, world_name)


def plot_delta_completion_time_fractions(agents, deltas, world_id, stats, world_name):
    fig, ax = plt.subplots()
    for cooperativity, color in COOPERATIVITY_COLORS.items():
        if cooperativity == "True" or cooperativity == "Both":
            data = stats[stats.collaborative == cooperativity]
            data = data.set_index("delta")
            deltas_collab = deltas - BAR_WIDTH / 2 if cooperativity == "True" else deltas + BAR_WIDTH / 2
            ax.bar(deltas_collab, data.time_mean_diff, yerr=data.time_std_diff, color=color, capsize=2, edgecolor="k",
                   width=BAR_WIDTH)
            legend_values = ["Collaborative", "Proposed Method"]
            plt.legend(legend_values, title="Cooperativity", title_fontproperties={"weight": "bold"})
    ax.set_ylim(COMPLETION_TIME_FRACTION_Y_LABEL)
    set_labels(agents, ax, world_name, COMPLETION_TIME_FRACTION_Y_LABEL)
    save_delta_figure(FIGURE_NAME_DELTA_COMPLETION_TIME_FRACTIONS, world_id, agents)


def set_title(ax, agents, world_name):
    ax.set_title(f"Fence post placement in {world_name} with {agents} agents")


def save_delta_figure(data_type, world_id, agents):
    save_figure(f"{data_type}_{world_id}_{agents}.png")
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
    plot_delta(3)
