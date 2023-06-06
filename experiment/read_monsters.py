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


def get_experiment_result(time, alive_agents):
    if time == -1 or alive_agents == 0:
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
        labels += ["Isolated", f"\n {agent} agents", "Observant"]
    return labels


def plot_completion_chances():
    experiment_no_help = {"files": ["output_fwz_4.csv", "output_fwz_5.csv"], "consider_other_agents": False}
    experiment_help = {"files": ["output_fwzh_4.csv", "output_fwzh_5.csv"], "consider_other_agents": True}
    experiments = [experiment_no_help, experiment_help]

    data = pd.DataFrame()
    for experiment in experiments:
        files = experiment["files"]
        dfs = [read_csv(file).astype({"collaborative": str}) for file in files]
        df = pd.concat(dfs)
        df["consider_other_agents"] = experiment["consider_other_agents"]
        data = data.append(df)

    data["result"] = data.apply(lambda row: get_experiment_result(row.time, row.alive_agents), axis=1)
    accumulated_results = data.groupby(["consider_other_agents", "agents"])["result"].agg(
        [failure_rate, timeout_rate, success_rate])
    accumulated_results = accumulated_results.reset_index()

    fig, ax = plt.subplots()
    colors = ["g", "r", "b"]
    labels = ["Success", "Failure"]
    y = ["success_rate", "failure_rate"]

    for result in accumulated_results.groupby("consider_other_agents"):
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

    times_pivot = filtered_data.pivot_table(index='agents', columns='consider_other_agents', values='time',
                                            aggfunc=['mean', 'std'])

    fig, ax = plt.subplots()
    colors = ["orange", "deepskyblue"]
    times_pivot.plot(kind="bar", y="mean", width=WIDTH * 1.5, ax=ax, yerr="std", capsize=CAPSIZE, color=colors,
                     edgecolor='k', rot=1)
    ax.set_title("Fence placement in flat world with zombie")

    ax.set_ylabel("Average completion time (s)")
    ax.set_ylim([0, 300])

    ax.set_xlabel("")
    ax.set_xticks(get_ticks(n_agent_amounts, WIDTH * 0.75))
    ax.set_xticklabels(get_labels(accumulated_results.agents.unique()))
    ax.tick_params(axis='x', which='both', length=0)

    ax.legend(["Isolated", "Observant"], loc="upper right")

    save_figure("times_monster.png")
    plt.show()


if __name__ == '__main__':
    plot_completion_chances()
