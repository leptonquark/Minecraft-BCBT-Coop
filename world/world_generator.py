from dataclasses import dataclass

import numpy as np

DEFAULT_SEED = "4000020"
FLAT_WORLD_NO_DECORATION_GENERATOR_STRING = "3;1*minecraft:bedrock,7*minecraft:dirt,1*minecraft:grass;35"
FLAT_WORLD_DECORATION_GENERATOR_STRING = "3;1*minecraft:bedrock,7*minecraft:dirt,1*minecraft:grass;35;decoration"


class WorldGenerator:
    def __init__(self, seed=DEFAULT_SEED):
        self.seed = seed
        self.cuboids = []


class DefaultWorldGenerator(WorldGenerator):
    def __init__(self, seed=DEFAULT_SEED):
        super().__init__(seed)


class FlatWorldGenerator(WorldGenerator):
    def __init__(self, with_trees=True, seed=DEFAULT_SEED):
        super().__init__(seed)
        if with_trees:
            self.generator_string = FLAT_WORLD_DECORATION_GENERATOR_STRING
        else:
            self.generator_string = FLAT_WORLD_NO_DECORATION_GENERATOR_STRING


class CustomWorldGenerator(FlatWorldGenerator):
    def __init__(self, cuboids=None, seed=DEFAULT_SEED):
        super().__init__(False, seed=seed)
        if cuboids is None:
            cuboids = []
        self.cuboids = cuboids


@dataclass
class Cuboid:
    type: str
    range: np.array
