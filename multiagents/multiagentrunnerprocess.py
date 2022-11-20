import multiprocessing as mp
from dataclasses import dataclass
from typing import List, Dict, Optional

from multiagents.multiagentprocess import MultiAgentProcess
from world.missiondata import MissionData


class MultiAgentRunnerProcess(mp.Process):

    def __init__(self, running, agent_names, goals):
        super(MultiAgentRunnerProcess, self).__init__()
        self.running = running
        self.pipe = mp.Pipe()
        self.goals = goals
        self.agent_names = agent_names

        self.agent_positions = [None] * len(agent_names)
        self.blueprint_result = None

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
                    agent_data = pipe[0].recv()
                    self.agent_positions[i] = agent_data.position
                    if agent_data.blueprint_result:
                        self.blueprint_result = agent_data.blueprint_result
                    data = MultiAgentRunnerState(self.agent_positions, self.blueprint_result, blackboard.copy())
                    self.pipe[1].send(data)
        print("All MultiAgentProcesses has stopped")


@dataclass
class MultiAgentRunnerState:
    agent_positions: List[Optional[List[float]]]
    blueprint_result: Optional[List[bool]]
    blackboard: Dict[str, str]
