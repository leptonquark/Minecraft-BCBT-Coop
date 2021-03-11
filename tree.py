import items

from behaviours import Craft, Equip, JumpIfStuck, Melt, GoToMaterial, MineMaterial, DigDownwardsToMaterial
from py_trees.common import ParallelPolicy
from py_trees.composites import Selector, Parallel
from sequence import Sequence
from gathering import get_gathering_tools


def get_goal_tree(agent_host, goal):
    tree = Selector(
        "Obtain " + goal,
        children=[
            Equip(agent_host, items.DIAMOND_PICKAXE),
            Craft(agent_host, items.DIAMOND_PICKAXE),
            get_gather_tree(agent_host, [items.DIAMOND_ORE]),
            get_iron_craft_tree(agent_host),
            get_gather_tree(agent_host, [items.IRON_ORE]),
            get_stone_craft_tree(agent_host),
            get_gather_tree(agent_host, [items.STONE]),
            get_wooden_craft_tree(agent_host),
            get_gather_tree(agent_host, [items.LOG, items.LOG_2, items.COBBLESTONE])
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
    tree = Sequence(
        "BaseTree",
        children=[JumpIfStuck(agent_host), baseGoalTree]
    )
    tree.setup_with_descendants()
    return tree


def get_wooden_craft_tree(agent_host):
    sub_tree = Parallel(
        "Craft wood",
        policy=ParallelPolicy.SuccessOnAll(),
        children=[
            Craft(agent_host, items.PLANKS, 10),
            Craft(agent_host, items.STICKS, 8),
            Craft(agent_host, items.CRAFTING_TABLE),
        ],
    )
    sub_tree.setup_with_descendants()
    tree = Sequence(
        "Craft wooden pickaxe",
        children=[
            sub_tree,
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
            Melt(agent_host, items.IRON_INGOT, 3)
        ]
    )
    tree.setup_with_descendants()
    return tree


def get_gather_tree(agent_host, material):
    tool = get_gathering_tools(material)

    children = []
    if tool:
        children.append(Equip(agent_host, tool))
    children += [
        DigDownwardsToMaterial(agent_host, material),
        GoToMaterial(agent_host, material),
        MineMaterial(agent_host, material)
    ]

    tree = Sequence(
        "Gather " + str(material),
        children=children
    )
    tree.setup_with_descendants()
    return tree


class BehaviourTree:
    def __init__(self, agent_host):
        self.root = get_base_tree(agent_host)
