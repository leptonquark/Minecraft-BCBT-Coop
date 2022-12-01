import numpy as np


class Entity:

    def __init__(self, name, x, y, z):
        self.specie = name
        self.position = np.array([x, y, z])
