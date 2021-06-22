import numpy as np

from world import xmlconstants
from xml.etree import ElementTree as Et


class GridSpecification:
    def __init__(self, name, grid_range, is_global):
        self.name = name
        self.grid_range = grid_range
        self.is_global = is_global

    def initialize_xml(self, observation_grid):
        grid = Et.SubElement(observation_grid, xmlconstants.ELEMENT_GRID)
        grid.set(xmlconstants.ATTRIBUTE_GRID_NAME, self.name)
        grid.set(xmlconstants.ATTRIBUTE_GRID_GLOBAL, xmlconstants.TRUE if self.is_global else xmlconstants.FALSE)
        grid_min = Et.SubElement(grid, xmlconstants.ELEMENT_GRID_MIN)
        grid_min.set(xmlconstants.ATTRIBUTE_GRID_X, str(self.grid_range[0, 0]))
        grid_min.set(xmlconstants.ATTRIBUTE_GRID_Y, str(self.grid_range[1, 0]))
        grid_min.set(xmlconstants.ATTRIBUTE_GRID_Z, str(self.grid_range[2, 0]))
        grid_max = Et.SubElement(grid, xmlconstants.ELEMENT_GRID_MAX)
        grid_max.set(xmlconstants.ATTRIBUTE_GRID_X, str(self.grid_range[0, 1]))
        grid_max.set(xmlconstants.ATTRIBUTE_GRID_Y, str(self.grid_range[1, 1]))
        grid_max.set(xmlconstants.ATTRIBUTE_GRID_Z, str(self.grid_range[2, 1]))

    def get_grid_size(self):
        return [axis[1] - axis[0] + 1 for axis in self.grid_range]

    def contains_position(self, position):
        return np.all(position >= self.grid_range[:, 0]) and np.all(position <= self.grid_range[:, 1])
