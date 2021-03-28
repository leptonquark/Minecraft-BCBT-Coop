from py_trees.composites import Selector

import items
from behaviours import Craft, DigDownwardsToMaterial, GoToMaterial, Equip, JumpIfStuck, Melt, MineMaterial, PickupItem
from gathering import get_gathering_tools
from sequence import Sequence


def get_goal_tree(agent, goal):
    tree = Selector(
        "Obtain " + goal,
        children=[
            Equip(agent, items.DIAMOND_PICKAXE),
            Craft(agent, items.DIAMOND_PICKAXE),
            get_gather_tree(agent, [items.DIAMOND_ORE]),
            get_iron_craft_tree(agent),
            get_gather_tree(agent, [items.IRON_ORE]),
            get_stone_craft_tree(agent),
            get_gather_tree(agent, [items.STONE]),
            get_wooden_craft_tree(agent),
            get_gather_tree(agent, [items.LOG, items.LOG_2])
        ]
    )
    tree.setup_with_descendants()
    return tree


def get_base_goal_tree(agent):
    goals = ["stone_pickaxe"]  # REMOVE
    children = [get_goal_tree(agent, goal) for goal in goals]
    tree = Sequence(
        "BaseGoalTree",
        children=children
    )
    tree.setup_with_descendants()
    return tree


def get_base_tree(agent):
    baseGoalTree = get_base_goal_tree(agent)
    tree = Sequence(
        "BaseTree",
        children=[JumpIfStuck(agent), baseGoalTree]
    )
    tree.setup_with_descendants()
    return tree


def get_wooden_craft_tree(agent):
    sub_tree = Sequence(
        "Craft wood",
        children=[
            Craft(agent, items.PLANKS, 10),
            Craft(agent, items.STICKS, 8),
            Craft(agent, items.CRAFTING_TABLE),
        ],
    )
    sub_tree.setup_with_descendants()
    tree = Sequence(
        "Craft wooden pickaxe",
        children=[
            sub_tree,
            Craft(agent, items.WOODEN_PICKAXE)
        ]
    )
    tree.setup_with_descendants()
    return tree


def get_stone_craft_tree(agent):
    tree = Sequence(
        "Craft Stone",
        children=[
            Craft(agent, items.FURNACE),
            Craft(agent, items.STONE_PICKAXE)
        ]
    )
    tree.setup_with_descendants()
    return tree


def get_iron_craft_tree(agent):
    tree = Selector(
        "Craft Iron",
        children=[
            Craft(agent, items.IRON_PICKAXE),
            Melt(agent, items.IRON_INGOT, 3)
        ]
    )
    tree.setup_with_descendants()
    return tree


def get_gather_tree(agent, material):
    tool = get_gathering_tools(material)

    children = []
    children += [
        PickupItem(agent, material),
        MineMaterial(agent, material),
        GoToMaterial(agent, material),
        DigDownwardsToMaterial(agent, material)
    ]
    if tool:
        children.append(Equip(agent, tool))

    tree = Selector(
        "Gather " + str(material),
        children=children
    )
    tree.setup_with_descendants()
    return tree


class BehaviourTree:
    def __init__(self, agent):
        self.root = get_base_tree(agent)
