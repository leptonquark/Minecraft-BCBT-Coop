# Start a MultiAgentProcess with various amount of agents
# Store the time?
# Store the path (stretch)
# Being able to choose whether to use cooperative or individualistic agents
import multiprocessing as mp
import time

from goals.blueprint.blueprint import Blueprint, BlueprintType
from multiagents.multiagentrunnerprocess import MultiAgentRunnerProcess
from utils.names import get_names

if __name__ == '__main__':

    for i in range(10):
        start_time = time.time()
        amount = 2
        agent_names = get_names(amount)
        print(f"Starting Minecraft with {amount} clients...")
        goals = Blueprint.get_blueprint(BlueprintType.PointGrid, [132, 71, 9])
        running_event = mp.Event()
        running_event.set()
        process = MultiAgentRunnerProcess(running_event, agent_names, goals)
        process.start()
        value = None
        while process.is_alive():
            if process.pipe[0].poll():
                value = process.pipe[0].recv()
        length = value.completion_time if value else -1
        print(f"Total time: {length}")
