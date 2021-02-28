import json
import numpy as np
from enum import Enum
from inventory import Inventory
from utils import Direction, directionAngle, directionVector, up_vector, down_vector


MAX_DELAY = 60
YAW_TOLERANCE = 5
CIRCLE_DEGREES = 360
DELTA_ANGLES = 45
LOS_TOLERANCE = 0.5
MAX_PITCH = 0.2



not_stuck = ["air", "double_plant", "tallgrass", "yellow_flower"]


class Observation():


    def __init__(self, observations, grid_size):
        self.grid_size = grid_size

        if observations is None or len(observations) == 0:
            print("Observations is null or empty")
            return
 
        infoJSON = observations[-1].text
        if infoJSON is None:
            print("Info is null")
            return


        info = json.loads(infoJSON)
        self.info = info

        self.inventory = Inventory(info)
        print(self.inventory)

        los_abs_pos = None


        abs_pos = None
        if "XPos" in info and "YPos" in info and "ZPos" in info:
            abs_pos = np.array([info["XPos"], info["YPos"], info["ZPos"]])

        self.los_pos = None
        if "LineOfSight" in info:
            los = info["LineOfSight"]
            print("los", los)
            los_abs_pos = np.array([los["x"], los["y"], los["z"]]) 
            self.los_pos = los_abs_pos - abs_pos
        print("LOS", self.los_pos)


        yaw = 0
        if "Yaw" in info:
            yaw = info["Yaw"]
            if yaw <= 0:
                yaw += CIRCLE_DEGREES
        self.yaw = yaw

        pitch = 0
        if "Pitch" in info:
            pitch = info["Pitch"]
        self.pitch = pitch


        if "me" in info:
            self.grid = self.gridObservationFromList(info["me"])
            self.pos = np.array([int(axis/2) for axis in self.grid_size])

            self.upper_surroundings = {direction : self.grid[tuple(self.pos + directionVector[direction] + up_vector)] for direction in Direction }
            print("Upper Surroundings", self.upper_surroundings)
            self.lower_surroundings = {direction : self.grid[tuple(self.pos + directionVector[direction])] for direction in Direction }
            print("Lower Surroundings", self.lower_surroundings)



    def gridObservationFromList(self, gridobs):
        grid = np.array(gridobs).reshape(self.grid_size[1], self.grid_size[2], self.grid_size[0])
        grid = np.transpose(grid, (2, 0, 1))
        return grid



    def getCurrentDirection(self):
        for key in directionAngle:
            checkAngle = directionAngle[key]
            diff = checkAngle - self.yaw
            if diff <= 0:
                diff += 360

            if diff <= DELTA_ANGLES or diff >= CIRCLE_DEGREES - DELTA_ANGLES: 
                return key
        return Direction.North

    def getClosest(self, materials):
        if self.grid is not None:
            hits = (self.grid == materials[0])
            if len(materials) > 1:
                for i in range(1, len(materials)):
                    hits = (hits | (self.grid == materials[i]))
            matpos = np.argwhere(hits)
            if len(matpos) > 0:
                logdistances = matpos - self.pos
                logdistances = np.sum(np.abs(logdistances),axis=1)
                min_dist_arg = np.argmin(logdistances)
                move = matpos[min_dist_arg] - self.pos

                return move

        return None


    def isStuck(self):
        return self.lower_surroundings[Direction.Zero] not in not_stuck

    def print(self):
        for key in self.info:
            if key != "me":
                print(key, self.info[key])
