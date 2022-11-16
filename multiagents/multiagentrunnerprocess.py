import multiprocessing as mp

from multiagents.multiagentprocess import MultiAgentProcess
from world.missiondata import MissionData

AGENT_DATA = "agent_data"
BLACKBOARD = "blackboard"


class MultiAgentRunnerProcess(mp.Process):

    def __init__(self, running, agent_names, goals):
        super(MultiAgentRunnerProcess, self).__init__()
        self.running = running
        self.n_clients = len(agent_names)
        self.pipe = mp.Pipe()
        self.goals = goals
        self.agent_names = agent_names

    def run(self):
        manager = mp.Manager()
        blackboard = manager.dict()
        mission_data = MissionData(self.goals, self.agent_names)
        processes = [
            MultiAgentProcess(self.running, mission_data, self.goals, blackboard, i)
            for i in range(len(self.agent_names))
        ]
        for process in processes:
            process.start()
        pipes = [process.pipe for process in processes]

        while any(process.is_alive() for process in processes):
            for i, pipe in enumerate(pipes):
                if pipe[0].poll():
                    pipe_data = pipe[0].recv()
                    agent_data = (i, pipe_data)
                    data = {
                        AGENT_DATA: agent_data,
                        BLACKBOARD: blackboard.copy()
                    }
                    self.pipe[1].send(data)
