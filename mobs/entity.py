import numpy as np


class Entity:

    def __init__(self, name, x, y, z, hand_item=None):
        self.type = name
        self.position = np.array([x, y, z])
        self.hand_item = hand_item

    def __str__(self):
        return f"Entity: {self.type} at position {self.position[0]}, {self.position[1]}, {self.position[2]}"

    def __repr__(self):
        return str(self)
