import multiprocessing as mp
import time

from bt.back_chain_tree import BackChainTree
from goals.blueprint.blueprintvalidator import get_blueprint_validators_from_goals
from malmoutils.agent import MinerAgent
from malmoutils.world_state import check_timeout
from multiagents.multiagentstate import MultiAgentState, MultiAgentRunningState
from world.observation import Observation

MAX_TIME = 300


class MultiAgentProcess(mp.Process):
    def __init__(self, running, mission_data, blackboard, queue, role):
        super().__init__()
        self.running = running
        self.mission_data = mission_data
        self.blackboard = blackboard
        self.role = role
        goals = self.mission_data.goals
        self.blueprint_validators = get_blueprint_validators_from_goals(goals, role)
        self.queue = queue

    def run(self):
        agent = MinerAgent(self.mission_data, self.blackboard, self.role)

        agent.start_mission()
        agent.wait_for_mission()
        agent.activate_night_vision()

        tree = BackChainTree(agent, self.mission_data.goals, self.mission_data.cooperativity)

        last_delta = time.time()
        start_time = time.time()

        world_state = agent.get_next_world_state()
        observation = None
        state = MultiAgentRunningState.RUNNING
        while state is MultiAgentRunningState.RUNNING:
            observation = Observation(world_state.observations, self.mission_data)
            agent.set_observation(observation)
            self.send_info(observation, state, None)
            tree.tick()
            last_delta = check_timeout(agent, world_state, last_delta)
            world_state = agent.get_next_world_state()
            state = self.get_running_state(observation, world_state, tree, start_time)
        completion_time = time.time() - start_time
        success = tree.all_goals_achieved()

        print(f"Mission is running: {world_state.is_mission_running}")
        print(f"All goals achieved: {success}")
        print("Mission running state: ", state)
        print(f"Total time: {completion_time} \n")
        self.send_info(observation, state, completion_time)

    def get_running_state(self, observation, world_state, tree, start_time):
        if self.running and not self.running.is_set():
            print("Process was terminated")
            return MultiAgentRunningState.TERMINATED
        elif world_state is None or not world_state.is_mission_running:
            print("Mission was cancelled")
            return MultiAgentRunningState.CANCELLED
        elif tree.all_goals_achieved():
            print("All goals were achieved")
            return MultiAgentRunningState.SUCCESS
        elif MAX_TIME and time.time() - start_time > MAX_TIME:
            print("Mission timed out")
            return MultiAgentRunningState.TIMEOUT
        elif observation is not None and observation.life is not None and observation.life <= 0:
            print("Agent is deceased")
            return MultiAgentRunningState.DECEASED
        else:
            return MultiAgentRunningState.RUNNING

    def send_info(self, observation, state, completion_time):
        if observation:
            self.queue.put(self.get_data(observation, state, completion_time))

    def get_data(self, observation, running_state, completion_time):
        player_position = observation.abs_pos
        blueprint_result = [validator.validate(observation) for validator in self.blueprint_validators]
        return MultiAgentState(self.role, running_state, completion_time, player_position, blueprint_result)

