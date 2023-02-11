ELEMENT_MISSION = "Mission"

ELEMENT_ABOUT = "About"
ELEMENT_SUMMARY = "Summary"

ELEMENT_MOD_SETTINGS = "ModSettings"
ELEMENT_MS_PER_TICK = "MsPerTick"

ELEMENT_SERVER_SECTION = "ServerSection"
ELEMENT_INITIAL_CONDITIONS = "ServerInitialConditions"
ELEMENT_TIME = "Time"
ELEMENT_START_TIME = "StartTime"
ELEMENT_ALLOW_PASSAGE_OF_TIME = "AllowPassageOfTime"

ELEMENT_SERVER_HANDLERS = "ServerHandlers"
ELEMENT_DEFAULT_WORLD_GENERATOR = "DefaultWorldGenerator"
ELEMENT_FLAT_WORLD_GENERATOR = "FlatWorldGenerator"

ELEMENT_DRAWING_DECORATOR = "DrawingDecorator"

ELEMENT_DRAW_ENTITY = "DrawEntity"
ATTRIBUTE_ENTITY_X = "x"
ATTRIBUTE_ENTITY_Y = "y"
ATTRIBUTE_ENTITY_Z = "z"
ATTRIBUTE_ENTITY_XYZ = [ATTRIBUTE_ENTITY_X, ATTRIBUTE_ENTITY_Y, ATTRIBUTE_ENTITY_Z]
ATTRIBUTE_ENTITY_TYPE = "type"

ELEMENT_DRAW_CUBOID = "DrawCuboid"
ATTRIBUTE_CUBOID_X1 = "x1"
ATTRIBUTE_CUBOID_Y1 = "y1"
ATTRIBUTE_CUBOID_Z1 = "z1"
ATTRIBUTE_CUBOID_X2 = "x2"
ATTRIBUTE_CUBOID_Y2 = "y2"
ATTRIBUTE_CUBOID_Z2 = "z2"
ATTRIBUTE_CUBOID_X = [ATTRIBUTE_CUBOID_X1, ATTRIBUTE_CUBOID_X2]
ATTRIBUTE_CUBOID_Y = [ATTRIBUTE_CUBOID_Y1, ATTRIBUTE_CUBOID_Y2]
ATTRIBUTE_CUBOID_Z = [ATTRIBUTE_CUBOID_Z1, ATTRIBUTE_CUBOID_Z2]
ATTRIBUTE_CUBOID_XYZ = [ATTRIBUTE_CUBOID_X, ATTRIBUTE_CUBOID_Y, ATTRIBUTE_CUBOID_Z]
ATTRIBUTE_CUBOID_TYPE = "type"

ATTRIBUTE_FLAT_WORLD_GENERATOR_STRING = "generatorString"

ATTRIBUTE_FORCE_WORLD_RESET = "forceReset"

ELEMENT_AGENT_SECTION = "AgentSection"
ELEMENT_AGENT_HANDLERS = "AgentHandlers"
ELEMENT_AGENT_NAME = "Name"
ELEMENT_AGENT_START_SPECIFICATIONS = "AgentStart"

ELEMENT_GRID = "Grid"
ELEMENT_GRID_MIN = "min"
ELEMENT_GRID_MAX = "max"

ELEMENT_INVENTORY = "Inventory"
ELEMENT_INVENTORY_ITEM = "InventoryItem"

ATTRIBUTE_XMLNS = "xmlns"
ATTRIBUTE_XSI = "xmlns:xsi"

ATTRIBUTE_SEED = "seed"
ATTRIBUTE_GAME_MODE = "mode"

ATTRIBUTE_TYPE = "type"
ATTRIBUTE_SLOT = "slot"

ATTRIBUTE_GRID_NAME = "name"
ATTRIBUTE_GRID_GLOBAL = "absoluteCoords"
ATTRIBUTE_GRID_X = "x"
ATTRIBUTE_GRID_Y = "y"
ATTRIBUTE_GRID_Z = "z"
ATTRIBUTE_GRID_XYZ = [ATTRIBUTE_GRID_X, ATTRIBUTE_GRID_Y, ATTRIBUTE_GRID_Z]

AGENT_START_POSITION = "Placement"
AGENT_START_POSITION_X = "x"
AGENT_START_POSITION_Y = "y"
AGENT_START_POSITION_Z = "z"
AGENT_START_POSITION_XYZ = [AGENT_START_POSITION_X, AGENT_START_POSITION_Y, AGENT_START_POSITION_Z]
AGENT_START_PITCH = "pitch"

ENTITIES_NAME = "name"
ENTITIES_RANGE = "Range"
ENTITIES_RANGE_X = "xrange"
ENTITIES_RANGE_Y = "yrange"
ENTITIES_RANGE_Z = "zrange"
ENTITIES_RANGE_XYZ = [ENTITIES_RANGE_X, ENTITIES_RANGE_Y, ENTITIES_RANGE_Z]

COMMANDS_CONTINUOUS = "ContinuousMovementCommands"
COMMANDS_DISCRETE = "DiscreteMovementCommands"
COMMANDS_INVENTORY = "InventoryCommands"
COMMANDS_CRAFT = "SimpleCraftCommands"
COMMANDS_QUIT = "MissionQuitCommands"
COMMANDS_CHAT = "ChatCommands"

OBSERVATION_LOS = "ObservationFromRay"
OBSERVATION_STATS = "ObservationFromFullStats"
OBSERVATION_INVENTORY = "ObservationFromFullInventory"
OBSERVATION_ENTITIES = "ObservationFromNearbyEntities"
OBSERVATION_GRID = "ObservationFromGrid"

XMLNS_MALMO = "http://ProjectMalmo.microsoft.com"
XSI_WWW = "http://www.w3.org/2001/XMLSchema-instance"

TRUE = "true"
FALSE = "false"
