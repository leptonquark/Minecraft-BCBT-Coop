import multiprocessing as mp
from dataclasses import dataclass
from typing import List, Dict, Optional

from multiagents.multiagentprocess import MultiAgentProcess, MultiAgentRunningState

ALL_DONE_STATES = [MultiAgentRunningState.TIMEOUT, MultiAgentRunningState.COMPLETED, MultiAgentRunningState.DECEASED]
ANY_DONE_STATES = [MultiAgentRunningState.CANCELLED, MultiAgentRunningState.TERMINATED]


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
        self.agent_alive = [True] * mission_data.n_agents
        self.completion_times: List[Optional[float]] = [None] * mission_data.n_agents
        self.blueprint_results = []
        self.agent_running_states = [MultiAgentRunningState.RUNNING] * mission_data.n_agents
        self.running_state = MultiAgentRunningState.RUNNING

    def run(self):
        manager = mp.Manager()
        blackboard = manager.dict()
        queue = manager.Queue()

        processes = [
            MultiAgentProcess(self.running_event, self.mission_data, blackboard, queue, role)
            for role in range(self.mission_data.n_agents)
        ]
        for process in processes:
            process.start()

        while any(process.is_alive() for process in processes):
            agent_data = queue.get(1000)
            self.cache_agent_data(agent_data)
            state = self.get_state(blackboard)
            self.pipe[1].send(state)
            if self.running_state is not MultiAgentRunningState.RUNNING:
                self.running_event.clear()
                for process in processes:
                    process.join()
                break

        print("All MultiAgentProcesses has stopped")

    def cache_agent_data(self, agent_data):
        self.agent_positions[agent_data.role] = agent_data.position
        if agent_data.blueprint_results:
            self.blueprint_results = agent_data.blueprint_results
        self.completion_times[agent_data.role] = agent_data.completion_time
        self.agent_running_states[agent_data.role] = agent_data.running_state

        all_done_state = all(state in ALL_DONE_STATES for state in self.agent_running_states)
        any_done_state = any(state in ANY_DONE_STATES for state in self.agent_running_states)
        if all_done_state or any_done_state:
            self.running_state = agent_data.running_state
        if self.agent_alive[agent_data.role] and agent_data.running_state is MultiAgentRunningState.DECEASED:
            self.agent_alive[agent_data.role] = False

    def get_state(self, blackboard):
        bb = blackboard.copy()
        completion_time = self.get_completion_time()
        alive_agents = sum(self.agent_alive)
        return MultiAgentRunnerState(self.agent_positions, self.blueprint_results, bb, completion_time, alive_agents)

    def get_completion_time(self):
        if self.running_state in ALL_DONE_STATES:
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
    alive_agents: int
