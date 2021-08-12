import time
from enum import Enum

import gym
import numpy as np

from items import items
from world.observation import game_objects, Observation
from world.world import World


class BaseAction(Enum):
    StartAttack = 0
    StopAttack = 1
    MoveForward = 2
    StopMove = 3
    TurnLeft = 4
    TurnRight = 5
    StopTurn = 6


class MineEnvironment(gym.Env):
    metadata = {'render.modes': ['human']}

    def step(self, action):
        self.run_action(BaseAction(action))

        world_state = self.agent.get_next_world_state()
        observation = Observation(world_state.observations, self.world.mission_data)

        reward = calculate_rewards(observation)
        obs_vector = observation.to_obs_vector()

        done = is_done(world_state)

        info = {}

        return obs_vector, reward, done, info

    def run_action(self, action):
        if action == BaseAction.StartAttack:
            self.agent.attack(True)
        elif action == BaseAction.StopAttack:
            self.agent.attack(False)
        elif action == BaseAction.MoveForward:
            self.agent.move(0.3)
        elif action == BaseAction.StopMove:
            self.agent.move(0)
        elif action == BaseAction.TurnLeft:
            self.agent.turn(0.3)
        elif action == BaseAction.TurnRight:
            self.agent.turn(-0.3)
        elif action == BaseAction.StopTurn:
            self.agent.turn(0)

    def close(self):
        print("Quit")
        self.agent.quit()

    def reset(self):
        observation = Observation(self.agent.get_next_world_state().observations, self.world.mission_data)
        print("Reset")
        self.agent.quit()
        time.sleep(2)
        self.world = World(self.agent, None)
        self.world.start_world()

        return observation.to_obs_vector()

    def render(self, mode='human', close=False):
        """ Minecraft is started separately. """
        raise NotImplementedError()

    def __init__(self, agent):
        super(MineEnvironment, self).__init__()

        self.agent = agent
        self.world = World(self.agent, None)
        self.world.start_world()

        self.observation_space = self.get_observation_space()
        self.action_space = get_action_space()

    def get_observation_space(self):
        grid_size = self.world.mission_data.grid_local.get_list_size()

        low = float(-1) * np.ones(grid_size, dtype=np.float32)
        high = float(len(game_objects) - 1) * np.ones(grid_size, dtype=np.float32)
        return gym.spaces.Box(low, high)


def is_done(world_state):
    return not world_state.is_mission_running


def calculate_rewards(observation):
    if observation.inventory is None:
        return 0
    else:
        return observation.inventory.get_item_amount(items.DIRT)


def get_action_space():
    return gym.spaces.Discrete(len(BaseAction))
