import json

import numpy as np

from items import items
from items.inventory import Inventory
from items.pickup import PickUp
from mobs import animals
from mobs.animals import Animal
from utils.vectors import CIRCLE_DEGREES, degrees_to_radians, up_vector

SAME_SPOT_Y_THRESHOLD = 2
EPSILON_ARRIVED_AT_POSITION = 0.09

# Always append at the end of this list
game_objects = [
    items.AIR,
    items.PLANT,
    items.TALL_GRASS,
    items.FLOWER_YELLOW,
    items.FLOWER_RED,
    items.DIRT,
    items.SAND,
    items.GRAVEL,
    items.GRASS,
    items.LOG,
    items.LOG_2,
    items.COAL,
    items.STONE,
    items.COBBLESTONE,
    items.COAL_ORE,
    items.REDSTONE_ORE,
    items.LAPIS_ORE,
    items.IRON_ORE,
    items.GOLD_ORE,
    items.DIAMOND_ORE,
    items.DIAMOND,
    items.STICKS,
    items.WOODEN_FENCE,
    items.CRAFTING_TABLE,
    items.FURNACE,
    items.LEAVES,
    items.LEAVES_2,
    items.WATER,
    items.CLAY,
    items.SANDSTONE,
    items.MOSSY_COBBLESTONE,
    items.MOB_SPAWNER,
    items.CHEST,
    items.BROWN_MUSHROOM,
    items.DEAD_BUSH,
    items.FLOWING_WATER,
    items.LAVA,
    items.FLOWING_LAVA,
    items.FIRE,
    items.RED_MUSHROOM,
    items.CACTUS,
    items.REEDS,
    items.BEDROCK,
    items.OBSIDIAN,
    items.PLANKS,
    items.STICKS
]


def grid_observation_from_list(grid_observation_list, grid_size):
    grid = np.array(grid_observation_list).reshape((grid_size[1], grid_size[2], grid_size[0]))
    grid = np.transpose(grid, (2, 0, 1))
    return grid


def get_absolute_position(info):
    if Observation.X in info and Observation.Y in info and Observation.Z in info:
        return np.array([info[Observation.X], info[Observation.Y], info[Observation.Z]])
    return None


def get_yaw(info):
    if Observation.YAW in info:
        yaw = info[Observation.YAW]
        if yaw <= 0:
            yaw += CIRCLE_DEGREES
        return yaw
    return None


def get_pitch(info):
    return info.get(Observation.PITCH)


def get_line_of_sight_position(info):
    los = info.get(Observation.LOS)
    if los is None:
        return None
    if Observation.LOS_X in los and Observation.LOS_Y in los and Observation.LOS_Z in los:
        return np.array([los[Observation.LOS_X], los[Observation.LOS_Y], los[Observation.LOS_Z]])
    else:
        return None


def get_line_of_sight_type(info):
    los = info.get(Observation.LOS)
    if los is None:
        return None
    return los.get(Observation.LOS_TYPE)


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

        self.pos_local_grid = None

        self.abs_pos = None
        self.pitch = None
        self.yaw = None

        self.grid_local = None
        self.grids_global = {}
        self.inventory = None
        self.los_pos = None
        self.los_type = None

        self.animals = None
        self.pickups = None

        if observations is None or len(observations) == 0:
            print("Observations is null or empty")
            return

        info_json = observations[-1].text
        if info_json is None:
            print("Info is null")
            return

        self.info = json.loads(info_json)
        self.inventory = Inventory(self.info)

        self.pos_local_grid = np.array([int(axis / 2) for axis in self.grid_size_local])

        self.abs_pos = get_absolute_position(self.info)
        self.yaw = get_yaw(self.info)
        self.pitch = get_pitch(self.info)

        self.los_pos = get_line_of_sight_position(self.info)
        self.los_type = get_line_of_sight_type(self.info)

        self.grid_local = self.get_grid_local(self.info)

        self.setup_entities(self.info)

        self.to_obs_vector()

    def get_grid_local(self, info):
        if Observation.GRID_LOCAL in info:
            grid_local_spec = self.mission_data.grid_local
            return grid_observation_from_list(info[grid_local_spec.name], self.grid_size_local)
        return None

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

    def to_obs_vector(self):
        grid_vector = self.get_grid_obs_vector()
        los_type_vector = np.array([get_game_object_ordinal(self.los_type)])
        direction_vector = self.get_direction_vector()
        inventory_vector = self.get_inventory_vector()

        obs_vector = np.hstack((
            grid_vector,
            self.abs_pos,
            self.los_pos,
            los_type_vector,
            direction_vector,
            inventory_vector
        ))

        return obs_vector

    def get_grid_obs_vector(self):
        grid_local_spec = self.mission_data.grid_local
        if grid_local_spec.name in self.info:
            return np.array([get_game_object_ordinal(block) for block in self.info[grid_local_spec.name]])
        else:
            return np.array([])

    def get_direction_vector(self):
        if self.yaw is None or self.pitch is None:
            return np.array([])

        yaw_radians = degrees_to_radians(self.yaw)
        pitch_radians = degrees_to_radians(self.pitch)

        direction_vector = np.array([
            -np.sin(yaw_radians) * np.cos(pitch_radians),
            -np.sin(pitch_radians),
            np.cos(yaw_radians) * np.cos(pitch_radians),
        ])
        return direction_vector

    def get_inventory_vector(self):
        inventory_list = []
        for inventory_slot in self.inventory:
            inventory_list += [inventory_slot.amount, get_game_object_ordinal(inventory_slot.item)]
        return np.array(inventory_list)


def get_game_object_ordinal(game_object):
    if game_object is None:
        return -1
    if game_object not in game_objects:
        print(f"Object {game_object} has not been added to the game objects list")
        return -1
    else:
        return game_objects.index(game_object)
