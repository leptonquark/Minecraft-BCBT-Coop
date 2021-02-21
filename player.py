import random
import time
import json
from enum import Enum
import numpy as np


class Direction(Enum):
    Zero = 0
    North = 1
    West = 2
    South = 3
    East = 4

class LookHeight(Enum):
    Bottom = 0
    Upper = 1
    StraightDown = 2
    StraightUp = 3

MAX_DELAY = 60
YAW_TOLERANCE = 5
CIRCLE_DEGREES = 360
DELTA_ANGLES = 45
LOS_TOLERANCE = 0.5
MAX_PITCH = 0.2

directionAngle = {
    Direction.North : 0,
    Direction.East : 90,
    Direction.South : 180,
    Direction.West : 270
}

directionVector = {
    Direction.Zero : np.array([0, 0, 0]),
    Direction.North : np.array([0, 0, 1]),
    Direction.East : np.array([-1, 0, 0]),
    Direction.South : np.array([0, 0, -1]),
    Direction.West : np.array([1, 0, 0])
}

up_vector = np.array([0, 1, 0])
down_vector = np.array([0, -1, 0])

not_stuck = ["air", "double_plant", "tallgrass"]


class Player():

    def __init__(self, world, agent_host):
        self.world = world
        self.agent_host = agent_host

        self.grid_size = world.mission_data.get_grid_size()
        self.name = world.mission_data.name

    def run_mission(self):
        agent_host = self.agent_host
        world_state = agent_host.getWorldState()


        # main loop:
        while world_state.is_mission_running:

            #SLEEP
            time.sleep(0.5)

            #SEE (AND DO (FOR NOW)) 
            world_state = agent_host.getWorldState()
            info = world_state.observations[-1].text
            
            if info:
                infoDict = json.loads(info)

                for key in infoDict:
                    if key != "me":
                        print(key, infoDict[key])
                los_abs_pos = None


                abs_pos = None
                if "XPos" in infoDict and "YPos" in infoDict and "ZPos" in infoDict:
                    abs_pos = np.array([infoDict["XPos"], infoDict["YPos"], infoDict["ZPos"]])

                if "LineOfSight" in infoDict:
                    los = infoDict["LineOfSight"]
                    print("los", los)
                    los_abs_pos = np.array([los["x"], los["y"], los["z"]]) 
                    los_pos = los_abs_pos - abs_pos
                print("LOS", los_pos)


                yaw = 0
                if "Yaw" in infoDict:
                    yaw = infoDict["Yaw"]
                    if yaw <= 0:
                        yaw += CIRCLE_DEGREES

                pitch = 0
                if "Pitch" in infoDict:
                    pitch = infoDict["Pitch"]



                if "me" in infoDict:
                    grid = self.gridObservationFromList(infoDict["me"])
                    pos = np.array([int(axis/2) for axis in self.grid_size])

                    upper_surroundings = {direction : grid[tuple(pos + directionVector[direction] + up_vector)] for direction in Direction }
                    print("Upper Surroundings", upper_surroundings)
                    lower_surroundings = {direction : grid[tuple(pos + directionVector[direction])] for direction in Direction }
                    print("Lower Surroundings", lower_surroundings)
                
                if grid is not None:
                    logpos = np.argwhere((grid == "log") | (grid == "log2"))
                    if len(logpos) > 0:

                        logdistances = logpos - pos
                        logdistances = np.sum(np.abs(logdistances),axis=1)
                        min_dist_arg = np.argmin(logdistances)
                        move = logpos[min_dist_arg] - pos
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

                        currentDirection = self.getCurrentDirection(yaw)                        
                        print("Current Direction", currentDirection)
                        print("Wanted Direction", wantedDirection)
                        print(move)

                        if grid[tuple(pos)] not in not_stuck:
                            agent_host.sendCommand("jump 1")
                        else:
                            agent_host.sendCommand("jump 0")
                            turn_direction = self.getTurnDirection(yaw, wantedDirection)
                            agent_host.sendCommand( "turn " + str(turn_direction))




                            if turn_direction == 0:
                                if log_horizontal_distance > 1:
                                    agent_host.sendCommand( "attack 0")
                                    agent_host.sendCommand( "move 1")
                                else:
                                    agent_host.sendCommand( "move 0")

                                los_goal = log_vertical_distance + 0.5
                                if los_goal != None:
                                    pitch_req = self.getPitchChange(los_pos[1], los_goal)
                                    print("Pitch req", pitch_req)
                                    agent_host.sendCommand("pitch " + str(pitch_req))
                                    if(pitch_req == 0):
                                        agent_host.sendCommand( "attack 1")
                                    else:
                                        agent_host.sendCommand( "attack 0")
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
            last_delta = time.time()
        else:
            if time.time() - last_delta > MAX_DELAY:
                print("Max delay exceeded for world state change")
                world.restart_minecraft(world_state, "world state change")

    def gridObservationFromList(self, gridobs):
        grid = np.array(gridobs).reshape(self.grid_size[1], self.grid_size[2], self.grid_size[0])
        grid = np.transpose(grid, (2, 0, 1))
        return grid

    def getWantedAngle(self, direction):
        return directionAngle[direction]

    def getTurnDirection(self, yaw, wantedDirection):
        diff = self.getWantedAngle(wantedDirection) - yaw
        if diff <= 0:
            diff += 360

        if diff <= YAW_TOLERANCE or diff >= CIRCLE_DEGREES - YAW_TOLERANCE: 
            return 0
        else:
            half_circle = CIRCLE_DEGREES/2
            if diff <= half_circle:
                return diff/half_circle
            else:
                return -diff/half_circle


    def getCurrentDirection(self, yaw):
        for key in directionAngle:
            checkAngle = directionAngle[key]
            diff = checkAngle - yaw
            if diff <= 0:
                diff += 360

            if diff <= DELTA_ANGLES or diff >= CIRCLE_DEGREES - DELTA_ANGLES: 
                return key
        return Direction.North

    def getPitchChange(self, losY, targetY):
        if np.abs(losY - targetY) <= LOS_TOLERANCE:
            return 0
        else:
            if losY >= targetY:
                return MAX_PITCH 
            else:
                return -MAX_PITCH

    def getHorizontalDistance(self, distance):
        return np.abs(distance[0]) + np.abs(distance[2])



