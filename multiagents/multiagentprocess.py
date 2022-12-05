import multiprocessing as mp
import time
from dataclasses import dataclass
from typing import List, Optional

from bt.back_chain_tree import BackChainTree
from goals.blueprint.blueprintvalidator import get_blueprint_validators_from_goals
from malmoutils.agent import MinerAgent
from malmoutils.world_state import check_timeout
from world.observation import Observation

MAX_TIME = None


class MultiAgentProcess(mp.Process):
    def __init__(self, running, mission_data, blackboard, role):
        super().__init__()
        self.running = running
        self.mission_data = mission_data
        self.blackboard = blackboard
        self.role = role
        goals = self.mission_data.goals
        self.blueprint_validators = get_blueprint_validators_from_goals(goals, role)
        self.pipe = mp.Pipe()

    def run(self):
        agent_name = self.mission_data.agent_names[self.role]
        agent = MinerAgent(self.blackboard, self.role, agent_name)

        agent.start_multi_agent_mission(self.mission_data)
        agent.wait_for_mission()

        agent.activate_night_vision()

        tree = BackChainTree(agent, self.mission_data.goals, self.mission_data.collaborative)

        last_delta = time.time()
        start_time = time.time()

        world_state = agent.get_next_world_state()
        observation = None
        while self.is_running(observation, world_state, tree, start_time):
            observation = Observation(world_state.observations, self.mission_data)
            agent.set_observation(observation)
            self.send_info(observation, None)
            tree.tick()
            last_delta = check_timeout(agent, world_state, last_delta)
            world_state = agent.get_next_world_state()
        completion_time = time.time() - start_time

        print(f"Mission is running: {world_state.is_mission_running}")
        print(f"All goals achieved: {tree.all_goals_achieved()}")
        print(f"Total time: {completion_time} \n")
        self.send_info(observation, completion_time)

    def is_running(self, observation, world_state, tree, start_time):
        if self.running and not self.running.is_set():
            print("Process was terminated")
            return False
        if world_state is None or not world_state.is_mission_running:
            print("Mission was cancelled")
            return False
        if tree.all_goals_achieved():
            print("All goals were achieved")
            return False
        if MAX_TIME and time.time() - start_time > MAX_TIME:
            print("Mission timed out")
            return False
        if observation is not None and observation.life is not None and observation.life <= 0:
            print("Agent is deceased")
            return False
        return True

    def send_info(self, observation, completion_time):
        if observation:
            self.pipe[1].send(self.get_data(observation, completion_time))

    def get_data(self, observation, completion_time):
        player_position = observation.abs_pos
        blueprint_result = [validator.validate(observation) for validator in self.blueprint_validators]
        return MultiAgentState(self.role, completion_time, player_position, blueprint_result)


@dataclass
class MultiAgentState:
    role: int
    completion_time: Optional[float]
    position: List[float]
    blueprint_results: List[List[bool]]
