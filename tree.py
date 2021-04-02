from py_trees.composites import Selector

import items
from behaviours import Craft, DigDownwardsToMaterial, GoToMaterial, Equip, JumpIfStuck, Melt, MineMaterial, PickupItem
from gathering import get_gathering_tools
from sequence import Sequence


class BehaviourTree:
    def __init__(self, agent):
        self.agent = agent
        self.root = self.get_base_tree()

    def get_goal_tree(self, goal):
        tree = Selector(
            "Obtain " + goal,
            children=[
                Equip(self.agent, items.DIAMOND_PICKAXE),
                Craft(self.agent, items.DIAMOND_PICKAXE),
                self.get_gather_tree([items.DIAMOND_ORE]),
                self.get_iron_craft_tree(),
                self.get_gather_tree([items.IRON_ORE]),
                self.get_stone_craft_tree(),
                self.get_gather_tree([items.STONE]),
                self.get_wooden_craft_tree(),
                self.get_gather_tree([items.LOG, items.LOG_2])
            ]
        )
        tree.setup_with_descendants()
        return tree

    def get_base_goal_tree(self):
        goals = ["stone_pickaxe"]  # REMOVE
        children = [self.get_goal_tree(goal) for goal in goals]
        tree = Sequence(
            "BaseGoalTree",
            children=children
        )
        tree.setup_with_descendants()
        return tree

    def get_base_tree(self):
        baseGoalTree = self.get_base_goal_tree()
        tree = Sequence(
            "BaseTree",
            children=[JumpIfStuck(self.agent), baseGoalTree]
        )
        tree.setup_with_descendants()
        return tree

    def get_wooden_craft_tree(self):
        sub_tree = Sequence(
            "Craft wood",
            children=[
                Craft(self.agent, items.PLANKS, 10),
                Craft(self.agent, items.STICKS, 8),
                Craft(self.agent, items.CRAFTING_TABLE),
            ],
        )
        sub_tree.setup_with_descendants()
        tree = Sequence(
            "Craft wooden pickaxe",
            children=[
                sub_tree,
                Craft(self.agent, items.WOODEN_PICKAXE)
            ]
        )
        tree.setup_with_descendants()
        return tree

    def get_stone_craft_tree(self):
        tree = Sequence(
            "Craft Stone",
            children=[
                Craft(self.agent, items.FURNACE),
                Craft(self.agent, items.STONE_PICKAXE)
            ]
        )
        tree.setup_with_descendants()
        return tree

    def get_iron_craft_tree(self):
        tree = Selector(
            "Craft Iron",
            children=[
                Craft(self.agent, items.IRON_PICKAXE),
                Melt(self.agent, items.IRON_INGOT, 3)
            ]
        )
        tree.setup_with_descendants()
        return tree

    def get_gather_tree(self, material):
        tool = get_gathering_tools(material)

        children = []
        children += [
            PickupItem(self.agent, material),
            MineMaterial(self.agent, material),
            GoToMaterial(self.agent, material),
            DigDownwardsToMaterial(self.agent, material)
        ]
        if tool:
            children.append(Equip(self.agent, tool))

        tree = Selector(
            "Gather " + str(material),
            children=children
        )
        tree.setup_with_descendants()
        return tree
