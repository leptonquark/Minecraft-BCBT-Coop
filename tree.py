import items

from behaviours import Craft, Equip, JumpIfStuck, GoToMaterial, MineMaterial
from py_trees.composites import Selector, Parallel
from sequence import Sequence


def get_goal_tree(agent_host, goal):
    tree = Selector(
        "Obtain " + goal,
        children=[
            get_gather_tree(agent_host, [items.DIAMOND_ORE], items.IRON_PICKAXE),
            get_iron_craft_tree(agent_host),
            get_gather_tree(agent_host, [items.IRON_ORE], items.STONE_PICKAXE),
            get_stone_craft_tree(agent_host),
            get_gather_tree(agent_host, [items.STONE], items.WOODEN_PICKAXE),
            get_wooden_craft_tree(agent_host),
            get_gather_tree(agent_host, [items.LOG, items.LOG_2])
        ]
    )
    tree.setup_with_descendants()
    return tree


def get_base_goal_tree(agent_host):
    goals = ["stone_pickaxe"]  # REMOVE
    children = [get_goal_tree(agent_host, goal) for goal in goals]
    tree = Sequence(
        "BaseGoalTree",
        children=children
    )
    tree.setup_with_descendants()
    return tree


def get_base_tree(agent_host):
    baseGoalTree = get_base_goal_tree(agent_host)
    tree = Parallel(
        "BaseTree",
        children=[JumpIfStuck(agent_host), baseGoalTree]
    )
    tree.setup_with_descendants()
    return tree


def get_wooden_craft_tree(agent_host):
    tree = Parallel(
        "Craft wood",
        children=[
            Craft(agent_host, items.PLANKS, 7),
            Craft(agent_host, items.STICKS, 8),
            Craft(agent_host, items.CRAFTING_TABLE),
            Craft(agent_host, items.WOODEN_PICKAXE)
        ]
    )
    tree.setup_with_descendants()
    return tree


def get_stone_craft_tree(agent_host):
    tree = Sequence(
        "Craft Stone",
        children=[
            Craft(agent_host, items.FURNACE),
            Craft(agent_host, items.STONE_PICKAXE)
        ]
    )
    tree.setup_with_descendants()
    return tree


def get_iron_craft_tree(agent_host):
    tree = Selector(
        "Craft Iron",
        children=[
            Craft(agent_host, items.IRON_PICKAXE),
            Craft(agent_host, items.IRON_INGOT, 3)
        ]
    )
    tree.setup_with_descendants()
    return tree


def get_gather_tree(agent_host, material, tool=None):
    children = []
    if tool is not None:
        children.append(Equip(agent_host, tool))
    children += [GoToMaterial(agent_host, material, tool), MineMaterial(agent_host, material, tool)]

    tree = Sequence(
        "Gather " + str(material),
        children=children
    )
    tree.setup_with_descendants()
    return tree


class BehaviourTree:
    def __init__(self, agent_host):
        self.root = get_base_tree(agent_host)
