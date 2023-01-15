import uuid
import xml.etree.ElementTree as Et

import numpy as np

from goals.blueprint.blueprint import Blueprint
from utils.names import get_agent_names
from utils.string import prettify_xml
from world import xmlconstants
from world.grid import GridSpecification
from world.worldgenerator import FlatWorldGenerator


def setup_experiment_id():
    experiment_id = str(uuid.uuid1())
    print(f"experiment id {experiment_id}")
    return experiment_id


class MissionData:

    def __init__(self, config, cooperativity, reset, n_agents=1):
        self.agent_names = get_agent_names(n_agents)
        self.cooperativity = cooperativity
        self.goals = config.goals

        self.experiment_id = setup_experiment_id()

        self.summary = "Behaviour Tree Malmo"

        self.n_agents = n_agents

        self.world_generator = config.world_generator

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

        self.force_reset = reset

        self.start_positions = config.start_positions if self.force_reset else None

        self.start_pitch = 18

        self.daytime = len(config.start_entities) == 0
        self.start_time = 6000 if self.daytime else 18000
        self.allow_passage_of_time = False

        self.obs_entities_name = "entities"
        self.obs_entities_range = (80, 5, 80)

        self.grid_local = GridSpecification("me", np.array([[-40, 40], [-2, 4], [-40, 40]]), False)

        self.grids_global = [goal.get_required_grid("global") for goal in self.goals if isinstance(goal, Blueprint)]
        self.start_inventory = config.start_inventory
        self.start_entities = config.start_entities

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
        self.initialize_world_generator(server_handlers)
        if self.start_entities or self.world_generator.cuboids:
            self.initialize_drawing_decorator(server_handlers)

    def initialize_world_generator(self, server_handlers):
        if isinstance(self.world_generator, FlatWorldGenerator):
            world_generator = Et.SubElement(server_handlers, xmlconstants.ELEMENT_FLAT_WORLD_GENERATOR)
            generator_string = self.world_generator.generator_string
            world_generator.set(xmlconstants.ATTRIBUTE_FLAT_WORLD_GENERATOR_STRING, generator_string)
        else:
            world_generator = Et.SubElement(server_handlers, xmlconstants.ELEMENT_DEFAULT_WORLD_GENERATOR)
        world_generator.set(xmlconstants.ATTRIBUTE_SEED, self.world_generator.seed)
        xml_force_reset = xmlconstants.TRUE if self.force_reset else xmlconstants.FALSE
        world_generator.set(xmlconstants.ATTRIBUTE_FORCE_WORLD_RESET, xml_force_reset)

    def initialize_drawing_decorator(self, server_handlers):
        drawing_decorator = Et.SubElement(server_handlers, xmlconstants.ELEMENT_DRAWING_DECORATOR)
        self.initialize_entities(drawing_decorator)
        self.initialize_cuboids(drawing_decorator)

    def initialize_entities(self, drawing_decorator):
        for entity in self.start_entities:
            draw_entity = Et.SubElement(drawing_decorator, xmlconstants.ELEMENT_DRAW_ENTITY)
            draw_entity.set(xmlconstants.ATTRIBUTE_ENTITY_TYPE, entity.type)
            draw_entity.set(xmlconstants.ATTRIBUTE_ENTITY_X, str(entity.position[0]))
            draw_entity.set(xmlconstants.ATTRIBUTE_ENTITY_Y, str(entity.position[1]))
            draw_entity.set(xmlconstants.ATTRIBUTE_ENTITY_Z, str(entity.position[2]))

    def initialize_cuboids(self, drawing_decorator):
        for cuboid in self.world_generator.cuboids:
            draw_cuboid = Et.SubElement(drawing_decorator, xmlconstants.ELEMENT_DRAW_CUBOID)
            draw_cuboid.set(xmlconstants.ATTRIBUTE_CUBOID_X1, str(cuboid.range[0][0]))
            draw_cuboid.set(xmlconstants.ATTRIBUTE_CUBOID_Y1, str(cuboid.range[0][1]))
            draw_cuboid.set(xmlconstants.ATTRIBUTE_CUBOID_Z1, str(cuboid.range[0][2]))
            draw_cuboid.set(xmlconstants.ATTRIBUTE_CUBOID_X2, str(cuboid.range[1][0]))
            draw_cuboid.set(xmlconstants.ATTRIBUTE_CUBOID_Y2, str(cuboid.range[1][1]))
            draw_cuboid.set(xmlconstants.ATTRIBUTE_CUBOID_Z2, str(cuboid.range[1][2]))
            draw_cuboid.set(xmlconstants.ATTRIBUTE_CUBOID_TYPE, cuboid.type)

    def initialize_agent_section(self, mission):
        for i, name in enumerate(self.agent_names):
            agent_section = Et.SubElement(mission, xmlconstants.ELEMENT_AGENT_SECTION)
            agent_section.set(xmlconstants.ATTRIBUTE_GAME_MODE, self.mode)

            self.initialize_agent_name(agent_section, name)
            self.initialize_agent_start(agent_section, i)
            self.initialize_agent_handlers(agent_section)

    def initialize_agent_name(self, agent_section, name):
        agent_name = Et.SubElement(agent_section, xmlconstants.ELEMENT_AGENT_NAME)
        agent_name.text = name

    def initialize_agent_start(self, agent_section, i):
        agent_start = Et.SubElement(agent_section, xmlconstants.ELEMENT_AGENT_START_SPECIFICATIONS)
        if self.start_positions is not None and self.start_positions[i] is not None:
            placement = Et.SubElement(agent_start, xmlconstants.AGENT_START_POSITION)
            placement.set(xmlconstants.AGENT_START_POSITION_X, str(self.start_positions[i][0]))
            placement.set(xmlconstants.AGENT_START_POSITION_Y, str(self.start_positions[i][1]))
            placement.set(xmlconstants.AGENT_START_POSITION_Z, str(self.start_positions[i][2]))
            placement.set(xmlconstants.AGENT_START_PITCH, str(self.start_pitch))

            if self.start_inventory is not None and self.start_inventory:
                inventory = Et.SubElement(agent_start, xmlconstants.ELEMENT_INVENTORY)
                for i, item in enumerate(self.start_inventory):
                    item_element = Et.SubElement(inventory, xmlconstants.ELEMENT_INVENTORY_ITEM)
                    item_element.set(xmlconstants.ATTRIBUTE_TYPE, item)
                    item_element.set(xmlconstants.ATTRIBUTE_SLOT, str(i))

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
        range_entities.set(xmlconstants.ENTITIES_NAME, self.obs_entities_name)
        range_entities.set(xmlconstants.ENTITIES_RANGE_X, str(self.obs_entities_range[0]))
        range_entities.set(xmlconstants.ENTITIES_RANGE_Y, str(self.obs_entities_range[1]))
        range_entities.set(xmlconstants.ENTITIES_RANGE_Z, str(self.obs_entities_range[2]))

    def initialize_grid_observations(self, agent_handlers):
        observation_grid = Et.SubElement(agent_handlers, xmlconstants.OBSERVATION_GRID)
        self.grid_local.initialize_xml(observation_grid)
        for grid_global in self.grids_global:
            grid_global.initialize_xml(observation_grid)

    def is_flat_world(self):
        return isinstance(self.world_generator, FlatWorldGenerator)


def et_to_xml(root):
    rough_string = Et.tostring(root, 'utf-8')
    return prettify_xml(rough_string)
