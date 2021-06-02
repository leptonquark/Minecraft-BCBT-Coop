import numpy as np

from utils.vectors import flat_center_vector


class PickUp:

    def __init__(self, name, x, y, z):
        self.name = name
        self.position = np.array([x, y, z])

    def get_centralized_position(self):
        centralized_vector = np.round(self.position - flat_center_vector) + flat_center_vector
        centralized_vector[1] = self.position[1]
        return centralized_vector

    def __str__(self):
        return f"Pickup: {self.name} at position {self.position[0]}, {self.position[1]}, {self.position[2]}"

    def __repr__(self):
        return str(self)
