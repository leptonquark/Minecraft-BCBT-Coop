import multiprocessing as mp
import time

from bt.back_chain_tree import BackChainTree
from goals.blueprint.blueprint import Blueprint
from goals.blueprint.blueprintvalidator import BlueprintValidator
from malmoutils.agent import MinerAgent
from malmoutils.world_state import check_timeout
from world.observation import Observation


class MultiAgentProcess(mp.Process):

    def __init__(self, running, mission_data, goals, blackboard, role):
        super(MultiAgentProcess, self).__init__()
        self.running = running
        self.mission_data = mission_data
        self.goals = goals
        self.blackboard = blackboard
        self.role = role
        self.pipe = mp.Pipe()
        self.blueprint_validator = None
        if role == 0 and type(self.goals) is Blueprint:
            self.blueprint_validator = BlueprintValidator(self.goals)

    def run(self):
        agent_name = self.mission_data.agent_names[self.role]
        agent = MinerAgent(self.blackboard, agent_name)

        agent.start_multi_agent_mission(self.mission_data, self.role)
        agent.wait_for_mission()

        if self.mission_data.night_vision:
            agent.activate_night_vision()

        tree = BackChainTree(agent, self.goals)

        last_delta = time.time()
        start = time.time()

        world_state = agent.get_next_world_state()
        while self.is_running(world_state, tree):
            world_state = agent.get_next_world_state()
            observation = Observation(world_state.observations, self.mission_data)
            agent.set_observation(observation)
            self.send_info(observation)
            tree.tick()
            last_delta = check_timeout(agent, world_state, last_delta)
        print(f"Mission is running: {world_state.is_mission_running}")
        print(f"All goals achieved: {tree.all_goals_achieved()}")
        print(f"Total time: {time.time() - start} \n")

    def is_running(self, world_state, tree):
        if self.running and not self.running.is_set():
            print("Process was terminated")
            return False
        if world_state is None or not world_state.is_mission_running:
            print("Mission was cancelled")
            return False
        if tree.all_goals_achieved():
            print("All goals were achieved")
            return False
        return True

    def send_info(self, observation):
        self.pipe[1].send(self.get_data(observation))

    def get_data(self, observation):
        player_position = observation.abs_pos
        if self.blueprint_validator:
            blueprint_result = self.blueprint_validator.validate(observation)
            return MultiAgentState(self.role, player_position, blueprint_result)
        else:
            return MultiAgentState(self.role, player_position)


class MultiAgentState:
    def __init__(self, role, player_position, blueprint_result=None):
        self.role = role
        self.position = player_position
        self.blueprint_result = blueprint_result
