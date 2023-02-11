import numpy as np

from mobs.entity import Entity
from utils.vectors import flat_center


class PickUp(Entity):

    def __init__(self, name, x, y, z):
        super(PickUp, self).__init__(name, x, y, z)

    def get_centralized_position(self):
        centralized_vector = np.round(self.position - flat_center) + flat_center
        centralized_vector[1] = self.position[1]
        return centralized_vector
