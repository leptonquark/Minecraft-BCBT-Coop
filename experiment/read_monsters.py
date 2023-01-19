from enum import Enum

from matplotlib import pyplot as plt

from experiment.read import read_csv


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


def failures(x):
    return x[x == ExperimentResult.FAILURE].count()


def timeouts(x):
    return x[x == ExperimentResult.TIMEOUT].count()


def successes(x):
    return x[x == ExperimentResult.SUCCESS].count()


def plot_completion_chances():
    # Read data from one file
    file_default = "output_fwz.csv"
    file_help = "output_fwzh.csv"
    files = [file_default, file_help]

    stats = read_csv(file_default)

    stats["result"] = stats.apply(lambda x: get_experiment_result(x.time), axis=1)
    accumulated_results = stats.agg({"result": ["count", failures, timeouts, successes]}).T
    grouped_results = stats.groupby(["agents", "collaborative"])["result"].agg([failures, timeouts, successes])

    fig, ax = plt.subplots()
    colors = ["g", "r", "b"]
    accumulated_results.plot(kind="bar", ax=ax, y=["successes", "failures", "timeouts"], color=colors, stacked=True)
    plt.show()
    fig, ax = plt.subplots()
    grouped_results.plot(kind="bar", ax=ax, y=["successes", "failures", "timeouts"], color=["g", "r", "b"],
                         stacked=True, rot=0)
    plt.show()

    # Compare completion chance for different files. Separate by timeout, failure and success.

    # First show it for one file, then show it for two files.
    # Separate by each type of cooperativity and amount of agents. One graph for each amount of agents.
    # Use cumulative bar graph?

    # Maybe show one which doesn't care for which model is used also.
    # And one which combines all the data.

    # Probably also show the average completion time for each of these.


if __name__ == '__main__':
    plot_completion_chances()
