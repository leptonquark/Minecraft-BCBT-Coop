import multiprocessing as mp
from dataclasses import dataclass
from typing import List, Dict, Optional

from multiagents.multiagentprocess import MultiAgentProcess, MultiAgentRunningState


class MultiAgentRunnerProcess(mp.Process):

    def __init__(self, mission_data, running_event=None):
        super().__init__()
        if running_event is None:
            self.running_event = mp.Event()
            self.running_event.set()
        else:
            self.running_event = running_event
        self.pipe = mp.Pipe(False)
        self.mission_data = mission_data

        self.agent_positions = [None] * mission_data.n_agents
        self.completion_times: List[Optional[float]] = [None] * mission_data.n_agents
        self.blueprint_results = []
        self.running_state = MultiAgentRunningState.RUNNING

    def run(self):
        manager = mp.Manager()
        blackboard = manager.dict()
        processes = [
            MultiAgentProcess(self.running_event, self.mission_data, blackboard, role)
            for role in range(self.mission_data.n_agents)
        ]
        for process in processes:
            process.start()

        receivers = [process.pipe[0] for process in processes]

        while any(process.is_alive() for process in processes):
            for receiver in mp.connection.wait(receivers):
                agent_data = receiver.recv()
                self.cache_agent_data(agent_data)
                state = self.get_state(blackboard)
                print(state)
                if self.running_state is MultiAgentRunningState.DECEASED:
                    self.running_event.clear()
                self.pipe[1].send(state)
        print("All MultiAgentProcesses has stopped")

    def cache_agent_data(self, agent_data):
        self.agent_positions[agent_data.role] = agent_data.position
        if agent_data.blueprint_results:
            self.blueprint_results = agent_data.blueprint_results
        self.completion_times[agent_data.role] = agent_data.completion_time
        if agent_data.running_state is not MultiAgentRunningState.RUNNING:
            self.running_state = agent_data.running_state

    def get_state(self, blackboard):
        bb = blackboard.copy()
        completion_time = -1  # self.get_completion_time()
        return MultiAgentRunnerState(self.agent_positions, self.blueprint_results, bb, completion_time)

    def get_completion_time(self):
        if self.running_state in [MultiAgentRunningState.TIMEOUT, MultiAgentRunningState.COMPLETED]:
            return max(self.completion_times)
        elif self.running_state is MultiAgentRunningState.RUNNING:
            return None
        else:
            return float(-1)


@dataclass
class MultiAgentRunnerState:
    agent_positions: List[Optional[List[float]]]
    blueprint_results: List[List[bool]]
    blackboard: Dict[str, str]
    completion_time: Optional[float]
