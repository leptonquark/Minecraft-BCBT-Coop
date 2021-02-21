import random
import time
import json
from enum import Enum
import numpy as np
from observation import Observation, not_stuck
from utils import Direction, directionAngle, directionVector, up_vector, down_vector



MAX_DELAY = 60
YAW_TOLERANCE = 5
PITCH_TOLERANCE = 5
CIRCLE_DEGREES = 360
DELTA_ANGLES = 45
LOS_TOLERANCE = 0.5
MOVE_TRESHOLD = 5


up_vector = np.array([0, 1, 0])
down_vector = np.array([0, -1, 0])



class Player():

    def __init__(self, world, agent_host):
        self.world = world
        self.agent_host = agent_host

        self.grid_size = world.mission_data.get_grid_size()
        self.name = world.mission_data.name

    def run_mission(self):
        agent_host = self.agent_host
        world_state = agent_host.getWorldState()

        self.last_delta = time.time()

        # main loop:
        while world_state.is_mission_running:

            #SLEEP
            time.sleep(0.5)

            #SEE 
            world_state = agent_host.getWorldState()
            observation = Observation(world_state.observations, self.grid_size)

            #DO
            #If has material to craft, craft. Otherwise look for log
            if(observation.inventory.hasItem("log")):
                agent_host.sendCommand("craft planks")
            if(not observation.inventory.hasItem("crafting_table", 1)):
                if observation.inventory.hasItem("planks", 4):
                    agent_host.sendCommand("craft crafting_table")
            else:
                if(not observation.inventory.hasItem("stick", 2) and observation.inventory.hasItem("planks", 2)):
                    agent_host.sendCommand("craft stick")
                if(not observation.inventory.hasItem("wooden_pickaxe", 2) and observation.inventory.hasItem("stick", 2) and observation.inventory.hasItem("planks", 2)):
                    agent_host.sendCommand("craft wooden_pickaxe")
            
            if observation.grid is not None:
                logpos = np.argwhere((observation.grid == "log") | (observation.grid == "log2"))
                if len(logpos) > 0:

                    logdistances = logpos - observation.pos
                    logdistances = np.sum(np.abs(logdistances),axis=1)
                    min_dist_arg = np.argmin(logdistances)
                    move = logpos[min_dist_arg] - observation.pos
                    print(move)

                    log_horizontal_distance = self.getHorizontalDistance(move)
                    log_vertical_distance = move[1]
                    print("Log vertical distance", log_vertical_distance)

                    wantedDirection = Direction.North
                    if(np.abs(move[2]) >= np.abs(move[0])):
                        if(move[2] > 0):
                            wantedDirection = Direction.North
                        else:
                            wantedDirection = Direction.South
                    else:
                        if(move[0] > 0):
                            wantedDirection = Direction.West
                        else:
                            wantedDirection = Direction.East

                    currentDirection = observation.getCurrentDirection()                        
                    print("Current Direction", currentDirection)
                    print("Wanted Direction", wantedDirection)
                    print(move)

                    wantedPitch = self.getWantedPitch(log_horizontal_distance, -1+log_vertical_distance)
                    print("Current Pitch", observation.pitch)
                    print("Wanted Pitch", wantedPitch)


            if observation.isStuck():
                agent_host.sendCommand("jump 1")
            else:
                agent_host.sendCommand("jump 0")
                if wantedDirection is not None:
                    turn_direction = self.getTurnDirection(observation.yaw, wantedDirection)
                agent_host.sendCommand( "turn " + str(turn_direction))

                if turn_direction == 0:
                    if log_horizontal_distance > 1:
                        if(not observation.upper_surroundings[currentDirection] in not_stuck):
                            wantedPitch = self.getWantedPitch(1, 0)
                            agent_host.sendCommand( "move 0")
                            pitch_req = self.getPitchChange(observation.pitch, wantedPitch)
                            agent_host.sendCommand("pitch " + str(pitch_req))
                            if(pitch_req == 0):
                                agent_host.sendCommand( "attack 1")
                            else:
                                agent_host.sendCommand( "attack 0")
                        elif(not observation.lower_surroundings[currentDirection] in not_stuck):
                            wantedPitch = self.getWantedPitch(1, -1)
                            agent_host.sendCommand( "move 0")
                            pitch_req = self.getPitchChange(observation.pitch, wantedPitch)
                            agent_host.sendCommand("pitch " + str(pitch_req))
                            if(pitch_req == 0):
                                agent_host.sendCommand( "attack 1")
                            else:
                                agent_host.sendCommand( "attack 0")                          
                        else:                            
                            move_speed = self.getMoveSpeed(log_horizontal_distance)
                            pitch_req = self.getPitchChange(observation.pitch, 0)
                            agent_host.sendCommand("pitch " + str(pitch_req))
                            agent_host.sendCommand( "move " + str(move_speed))
                            agent_host.sendCommand( "attack 0")
                    else:
                        agent_host.sendCommand( "move 0")
                        pitch_req = self.getPitchChange(observation.pitch, wantedPitch)
                        agent_host.sendCommand("pitch " + str(pitch_req))
                        if(pitch_req == 0):
                            agent_host.sendCommand( "attack 1")
                        else:
                            agent_host.sendCommand( "attack 0")
                else:
                    agent_host.sendCommand( "attack 0")
                    agent_host.sendCommand( "move 0")            
            
            self.checkTimeout(self.world, world_state)

        print("Mission has stopped.")


    def checkTimeout(self, world, world_state):
        if (world_state.number_of_video_frames_since_last_state > 0 or
        world_state.number_of_observations_since_last_state > 0 or
        world_state.number_of_rewards_since_last_state > 0):
            self.last_delta = time.time()
        else:
            if time.time() - self.last_delta > MAX_DELAY:
                print("Max delay exceeded for world state change")
                world.restart_minecraft(world_state, "world state change")


    def getWantedAngle(self, direction):
        return directionAngle[direction]

    def getTurnDirection(self, yaw, wantedDirection):
        diff = self.getWantedAngle(wantedDirection) - yaw
        if diff <= 0:
            diff += 360

        if diff <= YAW_TOLERANCE or diff >= CIRCLE_DEGREES - YAW_TOLERANCE: 
            return 0
        else:
            print("diff", diff)
            half_circle = CIRCLE_DEGREES/2
            if diff <= half_circle:
                return diff/half_circle
            else:
                return (diff-CIRCLE_DEGREES)/half_circle

    def getWantedPitch(self, distDirection, distY):
        half_circle = CIRCLE_DEGREES/2

        return -np.arctan(distY/distDirection) * half_circle/np.pi
        

    def getPitchChange(self, pitch, wantedPitch):
        quarter_circle = CIRCLE_DEGREES/4
        diff = pitch - wantedPitch
        print(diff)
        if np.abs(diff) <= PITCH_TOLERANCE:
            return 0
        else:
            return -diff/quarter_circle

    def getHorizontalDistance(self, distance):
        return np.abs(distance[0]) + np.abs(distance[2])

    def getMoveSpeed(self, horizontal_distance):
        if(horizontal_distance >= MOVE_TRESHOLD):
            return 1
        elif(horizontal_distance <= 1):
            return 0
        else:
            return (horizontal_distance-1)/(MOVE_TRESHOLD-1)
            
