import multiprocessing as mp
import time

from bt.back_chain_tree import BackChainTree
from goals.blueprint.blueprint import Blueprint
from goals.blueprint.blueprintvalidator import BlueprintValidator
from malmoutils.agent import MinerAgent
from malmoutils.world_state import check_timeout
from world.observation import Observation

PLAYER_POSITION = "player_position"
BLUEPRINT_RESULTS = "blueprint_results"

class MultiAgentProcess(mp.Process):

    def __init__(self, mission_data, goals, blackboard, role):
        super(MultiAgentProcess, self).__init__()
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
        while world_state is not None and world_state.is_mission_running and not tree.all_goals_achieved():
            world_state = agent.get_next_world_state()
            observation = Observation(world_state.observations, self.mission_data)
            agent.set_observation(observation)
            self.send_info(observation)
            tree.tick()
            last_delta = check_timeout(agent, world_state, last_delta)
        print(f"Mission is running: {world_state.is_mission_running}")
        print(f"All goals achieved: {tree.all_goals_achieved()}")
        print(f"Total time: {time.time() - start} \n")

    def send_info(self, observation):
        data = {PLAYER_POSITION: observation.abs_pos}
        if self.blueprint_validator:
            blueprint_result = self.blueprint_validator.validate(observation)
            data[BLUEPRINT_RESULTS] = blueprint_result
        self.pipe[1].send(data)
