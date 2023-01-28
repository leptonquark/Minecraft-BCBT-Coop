from enum import Enum

import pandas as pd
from matplotlib import pyplot as plt

from experiment.read import read_csv
from utils.plot import save_figure

CAPSIZE = 10
WIDTH = 0.4


class ExperimentResult(Enum):
    SUCCESS = 0
    FAILURE = 1
    TIMEOUT = 2


def get_experiment_result(time):
    if time == -1:
        return ExperimentResult.FAILURE
    elif time >= 300:
        return ExperimentResult.TIMEOUT
    else:
        return ExperimentResult.SUCCESS


def failure_rate(x):
    return x[x == ExperimentResult.FAILURE].count() / x.count()


def timeout_rate(x):
    return x[x == ExperimentResult.TIMEOUT].count() / x.count()


def success_rate(x):
    return x[x == ExperimentResult.SUCCESS].count() / x.count()


def get_ticks(agents, width=WIDTH):
    return [agent + i * width / 2 for agent in range(agents) for i in range(-1, 2)]


def get_labels(agents):
    labels = []
    for agent in agents:
        labels += [f"Isolated", f"\n {agent} agents", f"Observant"]
    return labels


def plot_completion_chances():
    experiment_no_help = {"file": "output_fwz_1.csv", "helpful": False}
    experiment_help = {"file": "output_fwzh_1.csv", "helpful": True}
    experiments = [experiment_no_help, experiment_help]

    data = pd.DataFrame()
    for experiment in experiments:
        df = read_csv(experiment["file"])
        df["helpful"] = experiment["helpful"]
        data = data.append(df)

    data["result"] = data["time"].apply(get_experiment_result)
    accumulated_results = data.groupby(["helpful", "agents"])["result"].agg([failure_rate, timeout_rate, success_rate])
    accumulated_results = accumulated_results.reset_index()

    fig, ax = plt.subplots()
    colors = ["g", "r", "b"]
    labels = ["Success", "Failure"]
    y = ["success_rate", "failure_rate"]

    for result in accumulated_results.groupby("helpful"):
        width = WIDTH if result[0] else -WIDTH
        result[1].plot(
            kind="bar",
            position=0,
            width=width,
            edgecolor='black',
            ax=ax,
            label=labels,
            y=y,
            color=colors,
            stacked=True,
            rot=1
        )
    for i, container in enumerate(ax.containers):
        if i % 2 == 0:
            percentage_labels = [f"{100 * value:.0f}%" for value in container.datavalues]
        else:
            percentage_labels = [""] * len(container.datavalues)
        ax.bar_label(container, labels=percentage_labels, label_type='edge')

    n_agent_amounts = len(accumulated_results.agents.unique())
    ax.set_xlim([-2 * WIDTH, (n_agent_amounts - 1) + 2 * WIDTH])
    ax.set_title("Fence placement in flat world with zombie")

    ax.set_xticks(get_ticks(n_agent_amounts))
    ax.set_xticklabels(get_labels(accumulated_results.agents.unique()))
    ax.tick_params(axis='x', which='both', length=0)

    ax.set_ylabel("Probability of result")

    plt.legend(labels=labels, loc="upper right")
    save_figure("success_monster.png")

    plt.show()

    filtered_data = data[data["result"] == ExperimentResult.SUCCESS]

    times = filtered_data.groupby(['agents', 'helpful'])["time"].agg(["mean", "std"])
    times.columns = ["time_mean", "time_std"]
    times = times.reset_index()
    times = times.set_index(["agents"])
    times_pivot = filtered_data.pivot_table(index='agents', columns='helpful', values='time', aggfunc=['mean', 'std'])

    print(times_pivot)

    fig, ax = plt.subplots()
    colors = ["orange", "deepskyblue"]
    times_pivot.plot(kind="bar", y="mean", width=WIDTH * 1.5, ax=ax, yerr="std", capsize=CAPSIZE, color=colors,
                     edgecolor='k', rot=1)
    ax.set_title("Fence placement in flat world with zombie")

    ax.set_ylabel("Average completion time (s)")
    ax.set_ylim([0, 200])

    ax.set_xlabel("")
    ax.set_xticks(get_ticks(n_agent_amounts, WIDTH * 0.75))
    ax.set_xticklabels(get_labels(accumulated_results.agents.unique()))
    ax.tick_params(axis='x', which='both', length=0)

    ax.legend(["Isolated", "Observant"], loc="upper right")

    save_figure("times_monster.png")
    plt.show()
    print(times)



if __name__ == '__main__':
    plot_completion_chances()
