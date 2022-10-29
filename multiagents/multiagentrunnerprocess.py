import multiprocessing as mp

from malmoutils.minecraft import run_minecraft
from multiagents.multiagentrunner import MultiAgentRunner


class MultiAgentRunnerProcess(mp.Process):

    def __init__(self, agent_names, goals):
        super(MultiAgentRunnerProcess, self).__init__()
        self.n_clients = len(agent_names)
        self.multi_agent_runner = MultiAgentRunner(agent_names, goals)
        self.pipe = mp.Pipe()

    def run(self):
        run_minecraft(n_clients=self.n_clients)
        self.multi_agent_runner.run_mission_async(on_position=lambda position: self.on_position(position))

    def on_position(self, position):
        self.pipe[1].send(position)
