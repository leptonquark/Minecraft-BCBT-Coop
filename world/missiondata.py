import numpy as np
import xml.etree.ElementTree as Et
import xml.dom.minidom as dom

from goals.blueprint import Blueprint
from world import xmlconstants
from world.grid import GridSpecification

FOREST_SEED = "-5603130799377933031"
DESERT_SEED = "400009"


class MissionData:

    def __init__(self, goals):
        self.name = "SteveBot"
        self.summary = "Behaviour Tree Malmo"

        self.seed = DESERT_SEED
        self.ms_per_tick = 50  # Default: 50
        self.mode = "Survival"

        self.commands = [
            xmlconstants.COMMANDS_CONTINUOUS,
            xmlconstants.COMMANDS_DISCRETE,  # Needs to be specified after COMMANDS_CONTINUOUS
            xmlconstants.COMMANDS_INVENTORY,
            xmlconstants.COMMANDS_CRAFT,
            xmlconstants.COMMANDS_QUIT,
            xmlconstants.COMMANDS_CHAT
        ]
        self.simple_observations = [
            xmlconstants.OBSERVATION_LOS,
            xmlconstants.OBSERVATION_STATS,
            xmlconstants.OBSERVATION_INVENTORY
        ]

        self.start_position = (247.5, 68, 232.5)
        self.start_pitch = 18

        self.start_time = 6000
        self.allow_passage_of_time = False

        self.night_vision = True

        self.entities_name = "entities"
        self.entities_range = (40, 40, 40)

        self.grid_local = GridSpecification("me", np.array([[-20, 20], [-20, 20], [-20, 20]]), False)

        self.grids_global = []
        if isinstance(goals, Blueprint):
            self.grids_global.append(goals.get_required_grid("global"))

    def get_xml(self):
        mission = Et.Element(xmlconstants.ELEMENT_MISSION)
        mission.set(xmlconstants.ATTRIBUTE_XMLNS, xmlconstants.XMLNS_MALMO)
        mission.set(xmlconstants.ATTRIBUTE_XSI, xmlconstants.XSI_WWW)

        self.initialize_about(mission)
        self.initialize_mod_settings(mission)
        self.initialize_server_section(mission)
        self.initialize_agent_section(mission)

        return et_to_xml(mission)

    def initialize_about(self, mission):
        about = Et.SubElement(mission, xmlconstants.ELEMENT_ABOUT)
        summary = Et.SubElement(about, xmlconstants.ELEMENT_SUMMARY)
        summary.text = self.summary

    def initialize_mod_settings(self, mission):
        mod_settings = Et.SubElement(mission, xmlconstants.ELEMENT_MOD_SETTINGS)
        ms_per_tick = Et.SubElement(mod_settings, xmlconstants.ELEMENT_MS_PER_TICK)
        ms_per_tick.text = str(self.ms_per_tick)

    def initialize_server_section(self, mission):
        server_section = Et.SubElement(mission, xmlconstants.ELEMENT_SERVER_SECTION)
        self.initialize_initial_conditions(server_section)
        self.initialize_server_handlers(server_section)

    def initialize_initial_conditions(self, server_section):
        server_initial_conditions = Et.SubElement(server_section, xmlconstants.ELEMENT_INITIAL_CONDITIONS)
        time = Et.SubElement(server_initial_conditions, xmlconstants.ELEMENT_TIME)
        start_time = Et.SubElement(time, xmlconstants.ELEMENT_START_TIME)
        start_time.text = str(self.start_time)
        allow_passage_of_time = Et.SubElement(time, xmlconstants.ELEMENT_ALLOW_PASSAGE_OF_TIME)
        allow_passage_of_time.text = xmlconstants.TRUE if self.allow_passage_of_time else xmlconstants.FALSE

    def initialize_server_handlers(self, server_section):
        server_handlers = Et.SubElement(server_section, xmlconstants.ELEMENT_SERVER_HANDLERS)
        default_world_generator = Et.SubElement(server_handlers, xmlconstants.ELEMENT_WORLD_GENERATOR)
        default_world_generator.set(xmlconstants.ATTRIBUTE_SEED, self.seed)

    def initialize_agent_section(self, mission):
        agent_section = Et.SubElement(mission, xmlconstants.ELEMENT_AGENT_SECTION)
        agent_section.set(xmlconstants.ATTRIBUTE_GAME_MODE, self.mode)

        self.initialize_agent_name(agent_section)
        self.initialize_agent_start(agent_section)
        self.initialize_agent_handlers(agent_section)

    def initialize_agent_name(self, agent_section):
        name = Et.SubElement(agent_section, xmlconstants.ELEMENT_AGENT_NAME)
        name.text = self.name

    def initialize_agent_start(self, agent_section):
        agent_start = Et.SubElement(agent_section, xmlconstants.ELEMENT_AGENT_START_SPECIFICATIONS)
        placement = Et.SubElement(agent_start, xmlconstants.AGENT_START_POSITION)
        placement.set(xmlconstants.AGENT_START_POSITION_X, str(self.start_position[0]))
        placement.set(xmlconstants.AGENT_START_POSITION_Y, str(self.start_position[1]))
        placement.set(xmlconstants.AGENT_START_POSITION_Z, str(self.start_position[2]))
        placement.set(xmlconstants.AGENT_START_PITCH, str(self.start_pitch))

    def initialize_agent_handlers(self, agent_section):
        agent_handlers = Et.SubElement(agent_section, xmlconstants.ELEMENT_AGENT_HANDLERS)
        self.initialize_commands(agent_handlers)
        self.initialize_simple_observations(agent_handlers)
        self.initialize_entities_observations(agent_handlers)
        self.initialize_grid_observations(agent_handlers)

    def initialize_commands(self, agent_handlers):
        for command in self.commands:
            Et.SubElement(agent_handlers, command)

    def initialize_simple_observations(self, agent_handlers):
        for observation in self.simple_observations:
            Et.SubElement(agent_handlers, observation)

    def initialize_entities_observations(self, agent_handlers):
        observation_entities = Et.SubElement(agent_handlers, xmlconstants.OBSERVATION_ENTITIES)
        range_entities = Et.SubElement(observation_entities, xmlconstants.ENTITIES_RANGE)
        range_entities.set(xmlconstants.ENTITIES_NAME, self.entities_name)
        range_entities.set(xmlconstants.ENTITIES_RANGE_X, str(self.entities_range[0]))
        range_entities.set(xmlconstants.ENTITIES_RANGE_Y, str(self.entities_range[1]))
        range_entities.set(xmlconstants.ENTITIES_RANGE_Z, str(self.entities_range[2]))

    def initialize_grid_observations(self, agent_handlers):
        observation_grid = Et.SubElement(agent_handlers, xmlconstants.OBSERVATION_GRID)
        self.grid_local.initialize_xml(observation_grid)
        for grid_global in self.grids_global:
            grid_global.initialize_xml(observation_grid)


def et_to_xml(root):
    rough_string = Et.tostring(root, 'utf-8')
    reparsed = dom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

