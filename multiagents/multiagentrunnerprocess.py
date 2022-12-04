import multiprocessing as mp
from dataclasses import dataclass
from typing import List, Dict, Optional

from multiagents.multiagentprocess import MultiAgentProcess


class MultiAgentRunnerProcess(mp.Process):

    def __init__(self, running, mission_data):
        super().__init__()
        self.running = running
        self.pipe = mp.Pipe()
        self.mission_data = mission_data

        self.agent_positions = [None] * mission_data.n_agents
        self.completion_times: List[Optional[float]] = [None] * mission_data.n_agents
        self.blueprint_results = []

    def run(self):
        manager = mp.Manager()
        blackboard = manager.dict()
        processes = [
            MultiAgentProcess(self.running, self.mission_data, blackboard, role)
            for role in range(self.mission_data.n_agents)
        ]
        for process in processes:
            process.start()

        pipes = [process.pipe for process in processes]

        while any(process.is_alive() for process in processes):
            for i, pipe in enumerate(pipes):
                if pipe[0].poll():
                    agent_data = pipe[0].recv()
                    self.cache_agent_data(agent_data, i)
                    self.pipe[1].send(self.get_state(blackboard))
        print("All MultiAgentProcesses has stopped")

    def cache_agent_data(self, agent_data, i):
        self.agent_positions[i] = agent_data.position
        if agent_data.blueprint_results:
            self.blueprint_results = agent_data.blueprint_results
        self.completion_times[i] = agent_data.completion_time

    def get_state(self, blackboard):
        if all(self.completion_times):
            completion_time = max(self.completion_times)
        else:
            completion_time = None
        data = MultiAgentRunnerState(self.agent_positions, self.blueprint_results, blackboard.copy(),
                                     completion_time)
        return data


@dataclass
class MultiAgentRunnerState:
    agent_positions: List[Optional[List[float]]]
    blueprint_results: List[List[bool]]
    blackboard: Dict[str, str]
    completion_time: Optional[float]

