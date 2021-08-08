import json

import numpy as np

from items import items
from items.inventory import Inventory
from items.pickup import PickUp
from mobs import animals
from mobs.animals import Animal
from utils.vectors import CIRCLE_DEGREES

SAME_SPOT_Y_THRESHOLD = 2
EPSILON_ARRIVED_AT_POSITION = 0.09


class Observation:
    GRID_LOCAL = "me"

    X = "XPos"
    Y = "YPos"
    Z = "ZPos"

    LOS = "LineOfSight"
    LOS_TYPE = "type"
    LOS_X = "x"
    LOS_Y = "y"
    LOS_Z = "z"

    YAW = "Yaw"
    PITCH = "Pitch"

    ENTITIES = "entities"
    ENTITY_NAME = "name"
    ENTITY_X = "x"
    ENTITY_Y = "y"
    ENTITY_Z = "z"
    ENTITY_LIFE = "life"

    def __init__(self, observations, mission_data):
        self.mission_data = mission_data

        self.grid_size_local = mission_data.grid_local.get_grid_size()

        self.abs_pos = None
        self.pickups = None
        self.pitch = None
        self.yaw = None

        self.grid_local = None
        self.grids_global = {}
        self.inventory = None
        self.los_abs_pos = None
        self.los_type = None

        self.lower_surroundings = None
        self.upper_surroundings = None
        self.upper_upper_surroundings = None

        self.pos_local_grid = None
        self.animals = None

        if observations is None or len(observations) == 0:
            print("Observations is null or empty")
            return

        info_json = observations[-1].text
        if info_json is None:
            print("Info is null")
            return

        self.info = json.loads(info_json)
        self.inventory = Inventory(self.info)

        self.setup_absolute_position(self.info)
        self.setup_yaw(self.info)
        self.setup_pitch(self.info)
        self.setup_line_of_sight(self.info)
        self.setup_local_grid(self.info)
        self.setup_entities(self.info)

    def get_grid_local(self):
        if self.grid_local is not None:
            return self.grid_local
        grid_local_spec = self.mission_data.grid_local
        grid_local = grid_observation_from_list(self.info[grid_local_spec.name], grid_local_spec.get_grid_size())
        self.grid_local = grid_local

    def setup_absolute_position(self, info):
        if Observation.X in info and Observation.Y in info and Observation.Z in info:
            self.abs_pos = np.array([info[Observation.X], info[Observation.Y], info[Observation.Z]])

    def setup_line_of_sight(self, info):
        if Observation.LOS in info:
            los = info[Observation.LOS]
            if Observation.LOS_X in los and Observation.LOS_Y in los and Observation.LOS_Z in los:
                self.los_abs_pos = np.array([los[Observation.LOS_X], los[Observation.LOS_Y], los[Observation.LOS_Z]])
            if Observation.LOS_TYPE in los:
                self.los_type = los[Observation.LOS_TYPE]

    def setup_yaw(self, info):
        if Observation.YAW in info:
            self.yaw = info[Observation.YAW]
            if self.yaw <= 0:
                self.yaw += CIRCLE_DEGREES

    def setup_pitch(self, info):
        if Observation.PITCH in info:
            self.pitch = info[Observation.PITCH]

    def setup_local_grid(self, info):
        if Observation.GRID_LOCAL in info:
            grid_local_spec = self.mission_data.grid_local
            self.grid_local = grid_observation_from_list(info[grid_local_spec.name], self.grid_size_local)
            self.pos_local_grid = np.array([int(axis / 2) for axis in self.grid_size_local])

    def setup_entities(self, info):
        if Observation.ENTITIES in info:
            self.pickups = []
            self.animals = []
            for entity in info[Observation.ENTITIES]:
                entity_name = entity.get(Observation.ENTITY_NAME, None)
                entity_x = entity.get(Observation.ENTITY_X, None)
                entity_y = entity.get(Observation.ENTITY_Y, None)
                entity_z = entity.get(Observation.ENTITY_Z, None)
                if entity_name and entity_x is not None and entity_y is not None and entity_z is not None:
                    if entity_name in items.pickups:
                        self.pickups.append(PickUp(entity_name, entity_x, entity_y, entity_z))
                    elif entity_name in animals.species:
                        animal_life = entity.get(Observation.ENTITY_LIFE, None)
                        self.animals.append(Animal(entity_name, entity_x, entity_y, entity_z, animal_life))

    def get_grid_global(self, grid_spec):
        if grid_spec.name in self.grids_global:
            return self.grids_global[grid_spec.name]

        grid = grid_observation_from_list(self.info[grid_spec.name], grid_spec.get_grid_size())
        self.grids_global[grid_spec.name] = grid
        return grid

    def print(self):
        for key in self.info:
            if key != Observation.GRID_LOCAL:
                print(key, self.info[key])


def grid_observation_from_list(grid_observation_list, grid_size):
    grid = np.array(grid_observation_list).reshape((grid_size[1], grid_size[2], grid_size[0]))
    grid = np.transpose(grid, (2, 0, 1))
    return grid
