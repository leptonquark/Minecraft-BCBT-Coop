from py_trees.composites import Selector, Parallel

from behaviours import Craft, Equip, JumpIfStuck, GoToMaterial, MineMaterial
from sequence import Sequence



def get_goal_tree(agent_host, goal):
    tree = Selector(
        "Obtain " + goal,
        children=[
            get_gather_tree(agent_host, ["diamond_ore"], "iron_pickaxe"),
            get_iron_craft_tree(agent_host),
            get_gather_tree(agent_host, ["iron_ore"], "stone_pickaxe"),
            get_stone_craft_tree(agent_host),
            get_gather_tree(agent_host, ["stone"], "wooden_pickaxe"),
            get_wooden_craft_tree(agent_host),
            get_gather_tree(agent_host, ["log", "log2"])
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
            Craft(agent_host, "planks", 7),
            Craft(agent_host, "stick", 8),
            Craft(agent_host, "crafting_table", 1),
            Craft(agent_host, "wooden_pickaxe")
        ]
    )
    tree.setup_with_descendants()
    return tree


def get_stone_craft_tree(agent_host):
    tree = Sequence(
        "Craft Stone",
        children=[
            Craft(agent_host, "furnace"),
            Craft(agent_host, "stone_pickaxe")
        ]
    )
    tree.setup_with_descendants()
    return tree


def get_iron_craft_tree(agent_host):
    tree = Selector(
        "Craft Iron",
        children=[
            Craft(agent_host, "iron_pickaxe"),
            Craft(agent_host, "iron_ingot", 3)
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
