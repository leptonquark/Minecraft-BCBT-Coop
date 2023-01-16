from xml.etree import ElementTree as Et

import numpy as np

from world import xmlconstants


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
        grid_max = Et.SubElement(grid, xmlconstants.ELEMENT_GRID_MAX)
        for i, attribute in enumerate(xmlconstants.ATTRIBUTE_GRID_XYZ):
            grid_min.set(attribute, str(self.grid_range[i, 0]))
            grid_max.set(attribute, str(self.grid_range[i, 1]))

    def get_grid_size(self):
        return [axis[1] - axis[0] + 1 for axis in self.grid_range]

    def contains_position(self, position):
        return np.all(position >= self.grid_range[:, 0]) and np.all(position <= self.grid_range[:, 1])

    def get_grid_position(self, position):
        return tuple(position - self.grid_range[:, 0])
