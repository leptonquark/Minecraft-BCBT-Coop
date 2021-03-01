import random
import time
import json
import numpy as np
from enum import Enum
from observation import Observation, not_stuck
from tree import BehaviourTree

MAX_DELAY = 60

class Player():

    def __init__(self, world, agent_host):
        self.world = world
        self.agent_host = agent_host

        self.grid_size = world.mission_data.get_grid_size()
        self.name = world.mission_data.name

        self.tree = BehaviourTree(agent_host)


    def run_mission(self):
        world_state = self.agent_host.getWorldState()

        self.last_delta = time.time()

        time.sleep(1)


        # main loop:
        while world_state.is_mission_running:

            #SLEEP
            time.sleep(0.25)

            #SEE 
            world_state = self.agent_host.getWorldState()
            observation = Observation(world_state.observations, self.grid_size)
            self.agent_host.set_observation(observation)
            # observation.print()

            currentDirection = observation.getCurrentDirection()                        
            print("Current Direction", currentDirection)

            self.tree.root.tick_once()


            #DO
            #If has material to craft, craft. Otherwise look for log

            self.checkTimeout(self.world, world_state)



    def checkTimeout(self, world, world_state):
        if (world_state.number_of_video_frames_since_last_state > 0 or
        world_state.number_of_observations_since_last_state > 0 or
        world_state.number_of_rewards_since_last_state > 0):
            self.last_delta = time.time()
        else:
            if time.time() - self.last_delta > MAX_DELAY:
                print("Max delay exceeded for world state change")
                world.restart_minecraft(world_state, "world state change")